"""
rag_service.py
--------------
RAG pipeline for NEXUS:
1. extract text from PDF/TXT/MD
2. chunk text with overlap
3. create sentence-transformer embeddings
4. store vectors in PostgreSQL/pgvector
5. retrieve nearest chunks with cosine distance
"""

from __future__ import annotations

import io
import os
import re
from functools import lru_cache
from typing import Any

import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Document, DocumentChunk

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))
DEFAULT_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
MAX_TOP_K = 12
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once per backend process."""
    return SentenceTransformer(EMBEDDING_MODEL)


def _extension(filename: str) -> str:
    return os.path.splitext(filename.lower())[1]


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = _extension(filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only PDF, TXT and MD files are supported")

    if ext == ".pdf":
        try:
            pdf = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
        except Exception as exc:
            raise ValueError("Could not open this PDF") from exc

        pages = [page.get_text("text") for page in pdf]
        pdf.close()
        text = "\n\n".join(pages)
    else:
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("utf-8", errors="ignore")

    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if not text:
        raise ValueError("No readable text found in the document")
    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    def flush(value: str) -> None:
        value = value.strip()
        if value:
            chunks.append(value)

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            flush(current)
            current = ""
            start = 0
            while start < len(paragraph):
                end = min(start + chunk_size, len(paragraph))
                flush(paragraph[start:end])
                if end == len(paragraph):
                    break
                start = end - overlap
            continue

        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        flush(current)
        prefix = current[-overlap:] if overlap and current else ""
        current = f"{prefix}\n\n{paragraph}".strip()
        if len(current) > chunk_size:
            flush(current[:chunk_size])
            current = current[max(0, chunk_size - overlap):]

    flush(current)
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()


def ingest_document(db: Session, file_bytes: bytes, filename: str, content_type: str | None) -> dict[str, Any]:
    text = extract_text(file_bytes, filename)
    chunks = chunk_text(text)
    vectors = embed_texts(chunks)

    document = Document(
        filename=filename,
        content_type=content_type,
        chunk_count=len(chunks),
    )
    db.add(document)
    db.flush()

    db.add_all(
        DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            embedding=vector,
        )
        for index, (chunk, vector) in enumerate(zip(chunks, vectors))
    )
    db.commit()
    db.refresh(document)

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "chunks": document.chunk_count,
    }


def search_similar(db: Session, query: str, top_k: int = DEFAULT_TOP_K) -> list[dict[str, Any]]:
    query = query.strip()
    if not query:
        return []

    top_k = max(1, min(int(top_k), MAX_TOP_K))
    query_vector = embed_texts([query])[0]
    distance = DocumentChunk.embedding.cosine_distance(query_vector)

    statement = (
        select(DocumentChunk, Document.filename, distance.label("distance"))
        .join(Document, Document.id == DocumentChunk.document_id)
        .order_by(distance)
        .limit(top_k)
    )

    rows = db.execute(statement).all()
    results: list[dict[str, Any]] = []
    for chunk, filename, cosine_distance in rows:
        distance_value = float(cosine_distance)
        results.append(
            {
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "filename": filename,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": round(max(0.0, 1.0 - distance_value), 4),
            }
        )
    return results


def retrieve_context(query: str, top_k: int = DEFAULT_TOP_K) -> tuple[str, list[dict[str, Any]]]:
    """Convenience helper for LangGraph execution; manages its own DB session."""
    db = SessionLocal()
    try:
        results = search_similar(db, query, top_k=top_k)
    finally:
        db.close()

    if not results:
        return "", []

    context_parts = []
    sources = []
    for result in results:
        label = f"{result['filename']}#chunk-{result['chunk_index']}"
        context_parts.append(f"SOURCE [{label}]\n{result['content']}")
        sources.append(
            {
                "filename": result["filename"],
                "chunk_index": result["chunk_index"],
                "score": result["score"],
            }
        )
    return "\n\n---\n\n".join(context_parts), sources
