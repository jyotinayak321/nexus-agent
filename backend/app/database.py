from __future__ import annotations
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# 55432, not 5432: a native Windows PostgreSQL service already owns 5432 on this machine.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://nexus:nexus_pass@localhost:55432/nexus_db",
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