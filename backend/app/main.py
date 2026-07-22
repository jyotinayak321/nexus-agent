from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .llm_provider import get_provider
from .routers import mission

app = FastAPI(title="NEXUS — Autonomous Research, Decision & Execution Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mission.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "llm_provider": get_provider().name}
