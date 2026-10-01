"""
main.py
-------
FastAPI application entry point.

Run:
    python -m uvicorn main:app --reload --host 127.0.0.1 --port 8420

Routes:
    GET  /                     -> frontend redirect
    GET  /api/health           -> backend health check
    POST /goal                 -> create a new goal
    GET  /plan/{goal_id}       -> get generated plan
    POST /execute/{goal_id}    -> run agent pipeline
    POST /upload-document      -> upload PDF for RAG
"""

import os
import uuid
import shutil
import logging
import tempfile

from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, get_db, Base
from models import Goal
from agents.graph import nexus_app
from rag.vector_store import ingest_pdf
from rag.vector_models import DocumentChunk  # noqa: F401


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus")


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title="NEXUS Autonomous Agent",
    description="Autonomous Research, Decision & Execution Agent",
    version="1.0.0",
)


# --------------------------------------------------
# Root route
# --------------------------------------------------

@app.get("/", include_in_schema=False)
def root():
    """
    Backend root open karne par frontend par redirect karega.
    """
    return RedirectResponse(url="http://localhost:5174")


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "NEXUS Backend"
    }


# --------------------------------------------------
# CORS
# --------------------------------------------------

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5174,http://127.0.0.1:5174"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Database
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Request Models
# --------------------------------------------------

class GoalRequest(BaseModel):
    goal: str
    budget: float | None = None
    deadline_days: int | None = None


# Demo cache
goal_results_cache: dict[str, dict] = {}


# --------------------------------------------------
# Create Goal
# --------------------------------------------------

@app.post("/goal")
def create_goal(
    request: GoalRequest,
    db: Session = Depends(get_db)
):
    new_goal = Goal(
        description=request.goal,
        budget=request.budget,
        deadline_days=request.deadline_days,
        status="created",
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return {
        "goal_id": str(new_goal.id),
        "status": new_goal.status,
    }


# --------------------------------------------------
# Execute Goal
# --------------------------------------------------

@app.post("/execute/{goal_id}")
def execute_goal(
    goal_id: str,
    db: Session = Depends(get_db)
):
    try:
        goal_uuid = uuid.UUID(goal_id)
    except ValueError:
        return {"error": "Invalid goal ID"}

    goal = (
        db.query(Goal)
        .filter(Goal.id == goal_uuid)
        .first()
    )

    if not goal:
        return {"error": "Goal not found"}

    initial_state = {
        "goal": goal.description,
        "budget": goal.budget,
        "deadline_days": goal.deadline_days,
    }

    try:
        result = nexus_app.invoke(initial_state)

    except Exception as e:
        logger.exception(
            f"Agent pipeline failed for goal {goal_id}"
        )

        return {
            "error": "Agent pipeline failed",
            "detail": str(e),
        }

    goal.status = "executed"

    db.commit()

    goal_results_cache[goal_id] = result

    return result


# --------------------------------------------------
# Get Plan
# --------------------------------------------------

@app.get("/plan/{goal_id}")
def get_plan(goal_id: str):

    result = goal_results_cache.get(goal_id)

    if not result:
        return {
            "error": (
                "Plan not generated yet. "
                "First call /execute/{goal_id}"
            )
        }

    return {
        "task_plan": result.get("task_plan"),
        "risks": result.get("risks"),
        "final_decision": result.get("final_decision"),
    }


# --------------------------------------------------
# Upload Document for RAG
# --------------------------------------------------

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename:
        return {"error": "No file selected"}

    # Only PDF
    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "Only PDF files are currently supported"
        }

    temp_dir = tempfile.gettempdir()

    temp_path = os.path.join(
        temp_dir,
        f"{uuid.uuid4()}_{file.filename}"
    )

    try:

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        result = ingest_pdf(
            temp_path,
            db
        )

        return result

    except Exception as e:

        logger.exception(
            "Document ingestion failed"
        )

        return {
            "error": "Document ingestion failed",
            "detail": str(e),
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)