"""
RAG (Retrieval-Augmented Generation) pipeline.

PDF -> text extraction (PyMuPDF) -> chunking -> embeddings (fastembed,
384-dim, matches ResearchResult.embedding in db_models.py) -> pgvector
storage -> cosine-similarity search -> Groq-synthesized answer over the
retrieved chunks.

This is the Research Agent's "evidence" arm: instead of only the built-in
knowledge base (agents/research.py), it can now answer questions grounded
in documents the user actually uploads for a mission.
"""
from __future__ import annotations

from typing import List

import fitz  # PyMuPDF
from fastembed import TextEmbedding
from sqlalchemy.orm import Session

from ..db_models import ResearchResult
from ..llm_provider import LLMProvider

_embedder: TextEmbedding | None = None

EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # 384-dim, matches Vector(384) column


def get_embedder() -> TextEmbedding:
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedding(model_name=EMBED_MODEL)
    return _embedder


def extract_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    normalized = " ".join(text.split())
    chunks: List[str] = []
    start = 0
    n = len(normalized)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = end - overlap
    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    return [vec.tolist() for vec in get_embedder().embed(texts)]


def ingest_pdf(db: Session, mission_id: str, filename: str, pdf_bytes: bytes) -> int:
    raw_text = extract_text(pdf_bytes)
    chunks = chunk_text(raw_text)
    if not chunks:
        return 0
    vectors = embed_texts(chunks)
    for chunk, vector in zip(chunks, vectors):
        db.add(
            ResearchResult(
                goal_id=mission_id,
                source=filename,
                content=chunk,
                relevance_score=0.0,
                embedding=vector,
            )
        )
    db.commit()
    return len(chunks)


def semantic_search(db: Session, mission_id: str, query: str, top_k: int = 5) -> List[ResearchResult]:
    query_vector = embed_texts([query])[0]
    return (
        db.query(ResearchResult)
        .filter(ResearchResult.goal_id == mission_id)
        .order_by(ResearchResult.embedding.cosine_distance(query_vector))
        .limit(top_k)
        .all()
    )


def synthesize_answer(provider: LLMProvider, query: str, chunks: List[ResearchResult]) -> str:
    if not chunks:
        return "No relevant documents found for this mission yet — upload a PDF first."
    context = "\n\n".join(f"[Source: {c.source}]\n{c.content}" for c in chunks)
    system = (
        "You are the Research Agent inside NEXUS, an autonomous project-planning agent. "
        "Answer the user's research question using ONLY the provided context chunks. "
        "Cite which source each fact comes from. If the context doesn't answer the question, say so plainly."
    )
    user = f"Context:\n{context}\n\nQuestion: {query}"
    return provider.generate(system, user, max_tokens=500)
