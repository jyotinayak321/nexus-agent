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
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agents.graph import nexus_app
from budget_service import calculate_cost_and_budget, validate_goal_inputs
from database import database_ready, get_db, init_db
from models import Document, Goal
from rag_service import (
    RagUnavailableError,
    ingest_document,
    retrieve_context,
    search_similar,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Create extensions/tables after the process is up, not at import time.
    try:
        init_db()
    except Exception as exc:
        print(f"Database initialization deferred (database not ready: {exc})")
    yield


app = FastAPI(title="NEXUS Autonomous Agent", version="0.2.0", lifespan=lifespan)

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
    if not database_ready():
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok", "service": "nexus-backend", "database": "ok"}


@app.post("/goal")
def create_goal(request: GoalRequest, db: Session = Depends(get_db)):
    try:
        validate_goal_inputs(request.goal, request.budget, request.deadline_days)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    new_goal = Goal(
        description=request.goal.strip(),
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

    try:
        rag_context, rag_sources = retrieve_context(goal.description)
    except RagUnavailableError as exc:
        print(f"[RAG] Context retrieval unavailable: {exc}")
        rag_context, rag_sources = "", []

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

    # Compute execution cost tracking and constraint evaluation
    cost_summary = calculate_cost_and_budget(result, goal.budget, goal.deadline_days)
    result["cost_summary"] = cost_summary

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
        "goal_id": goal_id,
        "goal": result.get("goal"),
        "task_plan": result.get("task_plan"),
        "risks": result.get("risks"),
        "final_decision": result.get("final_decision"),
        "research_findings": result.get("research_findings"),
        "rag_sources": result.get("rag_sources", []),
        "cost_summary": result.get("cost_summary", {}),
        "execution_log": result.get("execution_log"),
        "review_summary": result.get("review_summary"),
        "status": result.get("status", "completed"),
        "needs_replanning": result.get("needs_replanning", False),
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
    except RagUnavailableError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
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
    try:
        return {
            "query": request.query,
            "results": search_similar(db, request.query, request.top_k),
        }
    except RagUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
