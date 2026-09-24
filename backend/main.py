"""
main.py
-------
FastAPI entry point for NEXUS.

Core routes:
    POST /goal
    POST /execute/{goal_id}
    GET  /plan/{goal_id}

RAG routes:
    POST /documents/upload
    GET  /documents
    POST /rag/search
"""

import os
import uuid

from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agents.graph import nexus_app
from database import get_db, init_db
from models import Document, Goal
from rag_service import ingest_document, retrieve_context, search_similar

app = FastAPI(title="NEXUS Autonomous Agent", version="0.2.0")

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5174,http://127.0.0.1:5174",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable pgvector, then create all tables.
init_db()


class GoalRequest(BaseModel):
    goal: str = Field(min_length=3, max_length=5000)
    budget: float | None = None
    deadline_days: int | None = Field(default=None, ge=0)


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=12)


goal_results_cache: dict[str, dict] = {}


@app.get("/health")
def health():
    return {"status": "ok", "service": "nexus-backend"}


@app.post("/goal")
def create_goal(request: GoalRequest, db: Session = Depends(get_db)):
    new_goal = Goal(
        description=request.goal,
        budget=request.budget,
        deadline_days=request.deadline_days,
        status="created",
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return {"goal_id": str(new_goal.id), "status": new_goal.status}


@app.post("/execute/{goal_id}")
def execute_goal(goal_id: str, db: Session = Depends(get_db)):
    try:
        goal_uuid = uuid.UUID(goal_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid goal id") from exc

    goal = db.query(Goal).filter(Goal.id == goal_uuid).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    rag_context, rag_sources = retrieve_context(goal.description)

    initial_state = {
        "goal": goal.description,
        "budget": goal.budget,
        "deadline_days": goal.deadline_days,
        "rag_context": rag_context,
        "rag_sources": rag_sources,
    }

    goal.status = "executing"
    db.commit()

    try:
        result = nexus_app.invoke(initial_state)
    except Exception:
        goal.status = "failed"
        db.commit()
        raise

    goal.status = "executed"
    db.commit()
    goal_results_cache[goal_id] = result
    return result


@app.get("/plan/{goal_id}")
def get_plan(goal_id: str):
    result = goal_results_cache.get(goal_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Plan not generated yet — call /execute first",
        )

    return {
        "task_plan": result.get("task_plan"),
        "risks": result.get("risks"),
        "final_decision": result.get("final_decision"),
        "rag_sources": result.get("rag_sources", []),
    }


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    max_bytes = int(os.getenv("MAX_DOCUMENT_MB", "20")) * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(status_code=413, detail="Document is too large")

    try:
        return ingest_document(db, file_bytes, file.filename, file.content_type)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise


@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {
            "document_id": str(document.id),
            "filename": document.filename,
            "content_type": document.content_type,
            "chunks": document.chunk_count,
            "created_at": document.created_at.isoformat(),
        }
        for document in documents
    ]


@app.post("/rag/search")
def rag_search(request: RagSearchRequest, db: Session = Depends(get_db)):
    return {
        "query": request.query,
        "results": search_similar(db, request.query, request.top_k),
    }
