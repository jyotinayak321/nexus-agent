"""
models.py
---------
SQLAlchemy models for goals/agent state plus the RAG document store.
"""

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from database import Base

# sentence-transformers/all-MiniLM-L6-v2 produces 384-dimensional embeddings.
# If EMBEDDING_MODEL is changed to a model with a different output dimension,
# update this value (and recreate/migrate the table).
EMBEDDING_DIMENSION = 384


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=False)
    budget = Column(Float, nullable=True)
    deadline_days = Column(Integer, nullable=True)
    status = Column(String, default="created")
    created_at = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"))
    title = Column(String, nullable=False)
    status = Column(String, default="pending")
    priority = Column(Integer, default=1)
    depends_on = Column(String, nullable=True)


class Risk(Base):
    __tablename__ = "risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"))
    description = Column(Text)
    severity = Column(String)


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"))
    chosen_option = Column(Text)
    reasoning = Column(Text)


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIMENSION), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
