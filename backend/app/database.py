from __future__ import annotations
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Align with the live backend and root docker-compose.yml.
# Host port 55432 avoids a native Windows PostgreSQL service on 5432.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:55432/nexus_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    with engine.connect() as conn:
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
    Base.metadata.create_all(bind=engine)