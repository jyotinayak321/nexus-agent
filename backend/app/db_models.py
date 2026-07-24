"""
ORM tables — matches the schema from the hackathon requirement doc:
users, goals, plans, tasks, dependencies, agent_decisions,
research_results, execution_logs.
"""
from __future__ import annotations

import datetime as dt
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)

    goals: Mapped[list["Goal"]] = relationship(back_populates="user")


class Goal(Base):
    __tablename__ = "goals"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    goal: Mapped[str] = mapped_column(Text)
    deadline_days: Mapped[int] = mapped_column(Integer)
    budget_inr: Mapped[float] = mapped_column(Float)
    constraints_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="active")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="goals")
    plans: Mapped[list["Plan"]] = relationship(back_populates="goal")


class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(ForeignKey("goals.id"))
    plan_name: Mapped[str] = mapped_column(String)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    goal: Mapped["Goal"] = relationship(back_populates="plans")
    # NOTE: tasks are NOT linked to Plan in this MVP — TaskRow.plan_id
    # points at missions.mission_id instead (see mission_repository.py).
    # Plan/Goal/User hierarchy is reserved for a future multi-user auth layer.


class TaskRow(Base):
    """id (e.g. 'p1-t1') is only unique within one mission's plan, so the
    primary key is the (plan_id, id) pair — not id alone."""
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("missions.mission_id"), primary_key=True)
    title: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String, default="medium")
    status: Mapped[str] = mapped_column(String, default="pending")
    hours: Mapped[float] = mapped_column(Float, default=0)
    assignee: Mapped[str] = mapped_column(String, default="You")


class Dependency(Base):
    """Edge in the task dependency graph: task_id depends on depends_on_task_id.

    task_id/depends_on_task_id are plain strings, not FKs — TaskRow.id is only
    unique per plan_id (see TaskRow), so a same-column FK can't be enforced here.
    The dependency graph itself is built and topologically sorted in memory
    (NetworkX), so DB-level FK enforcement isn't needed.
    """
    __tablename__ = "dependencies"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    plan_id: Mapped[str] = mapped_column(ForeignKey("missions.mission_id"))
    task_id: Mapped[str] = mapped_column(String)
    depends_on_task_id: Mapped[str] = mapped_column(String)


class AgentDecision(Base):
    __tablename__ = "agent_decisions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(ForeignKey("missions.mission_id"))
    agent_name: Mapped[str] = mapped_column(String)
    decision: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    timestamp: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class ResearchResult(Base):
    __tablename__ = "research_results"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(ForeignKey("missions.mission_id"))
    source: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    embedding: Mapped[list] = mapped_column(Vector(384), nullable=True)


class MissionRow(Base):
    """Full snapshot (input + result) for fast reload — see mission_repository.py."""
    __tablename__ = "missions"
    mission_id: Mapped[str] = mapped_column(String, primary_key=True)
    input_json: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow
    )


class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(ForeignKey("missions.mission_id"))
    action: Mapped[str] = mapped_column(String)
    result: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)