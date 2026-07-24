from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..llm_provider import get_provider
from ..mission_repository import get_mission
from ..services.rag import ingest_pdf, semantic_search, synthesize_answer

router = APIRouter(prefix="/api/mission", tags=["research"])


class ResearchQuery(BaseModel):
    query: str


class ResearchChunk(BaseModel):
    source: str
    content: str


class ResearchAnswer(BaseModel):
    answer: str
    chunks: list[ResearchChunk]
    llm_provider: str


def _require_mission(db: Session, mission_id: str) -> None:
    if get_mission(db, mission_id) is None:
        raise HTTPException(status_code=404, detail="Mission not found")


@router.post("/{mission_id}/documents")
async def upload_document(mission_id: str, file: UploadFile, db: Session = Depends(get_db)) -> dict:
    _require_mission(db, mission_id)
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    pdf_bytes = await file.read()
    chunk_count = ingest_pdf(db, mission_id, file.filename, pdf_bytes)
    return {"filename": file.filename, "chunks_stored": chunk_count}


@router.post("/{mission_id}/research-query", response_model=ResearchAnswer)
def research_query(mission_id: str, payload: ResearchQuery, db: Session = Depends(get_db)) -> ResearchAnswer:
    _require_mission(db, mission_id)
    chunks = semantic_search(db, mission_id, payload.query)
    provider = get_provider()
    answer = synthesize_answer(provider, payload.query, chunks)
    return ResearchAnswer(
        answer=answer,
        chunks=[ResearchChunk(source=c.source, content=c.content) for c in chunks],
        llm_provider=provider.name,
    )
