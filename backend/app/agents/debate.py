"""
Multi-Agent Debate System.

For each key architectural decision, four specialist agents argue from their
own perspective (research, cost, technical, risk). A Final Decision Agent
then weighs the arguments against the user's hard constraints (budget,
hardware, timeline) and picks a winner with a stated rationale.

This is deliberately rule-based (see llm_provider.py) so the demo is
deterministic and offline, but every function here is where a real LLM call
would slot in later — the *shape* of the reasoning (four stances -> synthesis)
stays the same either way.
"""
from __future__ import annotations

from typing import List

from ..knowledge_base import Constraints
from ..models import AgentOpinion, Decision

ICONS = {"research": "\U0001F52C", "cost": "\U0001F4B0", "technical": "⚙️", "risk": "⚠️"}


def _op(agent: str, stance: str, argument: str) -> AgentOpinion:
    return AgentOpinion(agent=agent, icon=ICONS[agent], stance=stance, argument=argument)


def model_hosting(c: Constraints) -> Decision:
    opinions = [
        _op(
            "research",
            "Open-source model via a hosted inference API",
            "For most AI/ML MVPs, a hosted API (e.g. an open-weights model behind a managed endpoint) gets you "
            "working results fastest without managing infrastructure.",
        ),
        _op(
            "cost",
            "Watch the per-token bill" if not c.is_zero_budget else "Budget is ₹0 — paid APIs are off the table",
            f"Budget is ₹{c.budget_inr:.0f}. "
            + (
                "Any paid inference API is unaffordable at scale; must run free/open-source and self-hosted."
                if c.is_zero_budget
                else "A metered API is workable but usage needs to be capped so a 30-day run doesn't blow the budget."
            ),
        ),
        _op(
            "technical",
            "Local model needs a GPU to be practical" if not c.has_gpu else "Local GPU model is the efficient path",
            (
                "No GPU was declared, so a locally-run model would be too slow on CPU for iterative development — "
                "recommend a lightweight/quantized model or an external API instead."
                if not c.has_gpu
                else "A GPU is available, so running an open-source model locally avoids per-call costs entirely "
                "and keeps data on-device."
            ),
        ),
        _op(
            "risk",
            "Offline / dependency risk",
            (
                "Relying on an external API for the whole project introduces a single point of failure — rate "
                "limits or outages during a demo are a real risk."
                if c.budget_inr > 0 or not c.has_gpu
                else "Local GPU inference removes network dependency, but driver/CUDA setup issues can eat build time."
            ),
        ),
    ]

    if not c.has_gpu and c.is_zero_budget:
        final = "Use a CPU-optimized quantized open-source model, with a free-tier hosted API as fallback for demo day"
        rationale = "No GPU and no budget rule out both a heavy local model and a paid API — the only viable path is a small quantized model plus a free-tier fallback."
    elif not c.has_gpu:
        final = "Use a hosted LLM API within a capped monthly budget"
        rationale = "Without a GPU, local inference is impractical; budget allows a metered API if usage is capped."
    elif c.has_gpu and c.is_zero_budget:
        final = "Run an open-source model locally on the available GPU"
        rationale = "GPU is available and budget is zero, so local inference is both feasible and the only free option."
    else:
        final = "Run a local open-source model on GPU, keep a hosted API as an optional upgrade"
        rationale = "GPU + some budget gives flexibility; local-first keeps costs near zero while the API stays available if local performance disappoints."

    return Decision(topic="AI Model Hosting", opinions=opinions, final_decision=final, rationale=rationale)


def database(c: Constraints) -> Decision:
    opinions = [
        _op(
            "research",
            "PostgreSQL + pgvector",
            "Structured relational data and vector/semantic search both live in one engine, which simplifies the "
            "stack for a project that needs both records and embeddings.",
        ),
        _op(
            "cost",
            "Prefer self-hosted / free-tier" if c.budget_inr < 3000 else "Managed service is affordable here",
            (
                "MongoDB Atlas Vector Search is generous on its free tier but scales into paid tiers quickly; "
                "self-hosted Postgres has zero licensing cost."
                if c.budget_inr < 3000
                else "Budget can absorb a small managed database bill if it saves setup time."
            ),
        ),
        _op(
            "technical",
            "Postgres is the safer default",
            "pgvector integrates cleanly with SQLAlchemy/FastAPI and avoids learning a second query language "
            "alongside SQL.",
        ),
        _op(
            "risk",
            "Vendor lock-in",
            "A document-store vector DB ties the schema to that vendor's query API; Postgres keeps the option to "
            "migrate or self-host later.",
        ),
    ]
    final = "PostgreSQL + pgvector"
    rationale = "Covers structured data and vector search in one open-source engine, keeps cost at zero, and avoids vendor lock-in — dominates on every constraint the user gave."
    return Decision(topic="Database & Retrieval", opinions=opinions, final_decision=final, rationale=rationale)


def backend_framework(c: Constraints) -> Decision:
    opinions = [
        _op(
            "research",
            "FastAPI",
            "Async-first, automatic OpenAPI docs, and the de-facto standard for serving Python ML models.",
        ),
        _op(
            "cost",
            "No cost difference",
            "All three major Python frameworks (FastAPI, Flask, Django) are free and open-source; this decision "
            "doesn't move the budget.",
        ),
        _op(
            "technical",
            "FastAPI fits an AI-heavy stack",
            "Native async support matters once you add streaming model responses or websocket voice/chat features.",
        ),
        _op(
            "risk",
            "Django is over-scoped for a short timeline" if c.is_tight_timeline else "Low risk either way",
            (
                f"Only {c.total_hours:.0f} total hours are available — Django's batteries-included ORM/admin/auth "
                "stack costs more setup time than it saves here."
                if c.is_tight_timeline
                else "With more runway, Django's structure could pay off, but FastAPI still ships an MVP faster."
            ),
        ),
    ]
    final = "FastAPI"
    rationale = "Best async/ML-serving fit at zero extra cost, and the lightest setup overhead for the available time budget."
    return Decision(topic="Backend Framework", opinions=opinions, final_decision=final, rationale=rationale)


def deployment(c: Constraints) -> Decision:
    opinions = [
        _op(
            "research",
            "Container on a managed PaaS",
            "A Dockerized app on a platform like Render/Railway/Fly.io gets HTTPS, CI deploys, and logs without "
            "manual server ops.",
        ),
        _op(
            "cost",
            "Free tier only" if c.is_zero_budget or c.is_low_budget else "Small paid tier is affordable",
            (
                "Budget doesn't leave room for paid hosting — must stay on a free tier (with its sleep/cold-start "
                "limits) or self-host."
                if c.is_zero_budget or c.is_low_budget
                else "A ~$5-10/mo tier is affordable and avoids free-tier cold starts during a demo."
            ),
        ),
        _op(
            "technical",
            "Keep infra minimal for an MVP",
            "One service (backend + static frontend build) instead of a multi-service cluster reduces failure "
            "points before the deadline.",
        ),
        _op(
            "risk",
            "Free-tier cold starts during a live demo",
            "Free-tier containers sleep after inactivity — first request during a demo can lag several seconds; "
            "worth a warm-up ping before presenting.",
        ),
    ]
    if c.is_zero_budget or c.is_low_budget:
        final = "Deploy on a free-tier PaaS (e.g. Render/Railway free tier or HF Spaces)"
        rationale = "Budget rules out paid hosting; a free-tier PaaS still gives HTTPS and CI deploys, with a warm-up step to avoid demo-day cold starts."
    else:
        final = "Deploy on a low-cost managed container tier"
        rationale = "Small budget available — a paid low tier removes cold-start risk for a live demo, which free tiers don't."
    return Decision(topic="Deployment", opinions=opinions, final_decision=final, rationale=rationale)


def frontend(c: Constraints) -> Decision:
    react_skill = c.has_skill("react", "frontend", "javascript", "js")
    quick_ui = c.is_tight_timeline and c.team_size <= 1 and not react_skill
    opinions = [
        _op(
            "research",
            "Match the UI framework to the goal and audience",
            "A polished product demo benefits from a real frontend framework; a pure AI/ML proof-of-concept "
            "benefits more from shipping the model behind a quick UI.",
        ),
        _op(
            "cost",
            "No cost difference",
            "Both React and Streamlit/Gradio are free and open-source.",
        ),
        _op(
            "technical",
            "React needs frontend hours the plan may not have" if quick_ui else "Team has frontend capacity",
            (
                "Solo builder, tight timeline, no declared frontend skill — a full React build would eat hours "
                "needed for the core AI work."
                if quick_ui
                else "Team composition supports a proper React frontend without starving the core build."
            ),
        ),
        _op(
            "risk",
            "Scope creep on UI polish",
            "Time spent on frontend styling is time not spent validating the core AI feature — the riskiest part "
            "of most AI/ML MVPs.",
        ),
    ]
    if quick_ui:
        final = "Streamlit/Gradio quick UI"
        rationale = "Solo builder + tight timeline + no frontend skill declared — a minimal UI library lets nearly all remaining hours go to the core AI feature."
    else:
        final = "React (Vite) frontend"
        rationale = "Timeline and/or team composition can absorb a proper frontend without starving the core build."
    return Decision(topic="Frontend", opinions=opinions, final_decision=final, rationale=rationale)


TOPIC_FUNCS = [model_hosting, database, backend_framework, deployment, frontend]


def run_debate(c: Constraints) -> List[Decision]:
    return [fn(c) for fn in TOPIC_FUNCS]
