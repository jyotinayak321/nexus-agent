# NEXUS — Autonomous Research, Decision & Execution Agent

*"From Idea to Execution — an AI Agent That Thinks, Plans, Acts, Learns, and Adapts."*

A hackathon prototype of the goal-to-execution loop: most planning tools stop
at a roadmap. NEXUS keeps going — it decomposes the goal, has specialist
agents **debate** the key technical decisions, produces an **evidence-based**
plan scaled to your real constraints, lets you **simulate what-if scenarios**
before committing, and **self-corrects** when you report a blocker (no GPU,
budget cut, teammate leaves) by re-running the whole pipeline and showing you
exactly what changed and why.

## Architecture

```
GOAL → CONSTRAINTS → RESEARCH → MULTI-AGENT DEBATE → DECISION
     → DECOMPOSITION (MVP-aware) → TEAM ASSIGNMENT → PLAN
     → [WHAT-IF SIMULATION]  → [BLOCKER → ADAPTIVE REPLAN]
```

- `backend/app/knowledge_base.py` — constraint model (budget, GPU, timeline, team)
- `backend/app/agents/debate.py` — 4 agents (research/cost/technical/risk) argue
  5 architecture decisions; a final-decision synthesis picks a winner with a
  rationale, conditioned on the user's actual constraints
- `backend/app/agents/research.py` — turns debate output into evidence-based
  recommendation cards
- `backend/app/agents/decomposition.py` — phase/task breakdown, scaled to
  available hours; collapses into MVP mode under a tight timeline; assigns
  tasks to team members by skill match
- `backend/app/agents/simulate.py` — replays the pipeline against a
  hypothetical constraint change without persisting it ("what if budget hits ₹0?")
- `backend/app/agents/replan.py` — the self-correcting loop: parses a free-text
  blocker into concrete constraint changes, re-runs the pipeline, diffs
  decisions before/after
- `backend/app/llm_provider.py` — pluggable reasoning layer. Ships with a
  deterministic rule-based `MockProvider` (offline, no API key). Set
  `LLM_PROVIDER=claude` + `ANTHROPIC_API_KEY` to switch to real Claude
  reasoning later without touching any agent code.

## Run it

Backend:
```
cd backend
python -m venv venv
./venv/Scripts/activate   # or source venv/bin/activate on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8420
```

Frontend:
```
cd frontend
npm install
npm run dev   # http://localhost:5174
```

## Demo script

1. Submit a goal (try the example chip: "Build an AI Healthcare diagnosis assistant"),
   30 days / 2 hrs/day / ₹5,000 budget / no GPU.
2. **Plan** tab — full 7-phase roadmap, scaled to 60 available hours.
3. **Debate** tab — see all 4 agents argue AI hosting, database, framework,
   deployment, frontend, and the constraint-aware final call on each.
4. **What-if** tab — click "Deadline drops to 7 days" and watch it flip into
   MVP mode (4 phases) and swap the frontend choice — without touching the live plan.
5. **Adapt** tab — report "My teammate left and the budget got cut to zero".
   Watch NEXUS detect both changes, re-debate, and flip the AI-hosting and
   deployment decisions with a stated rationale — the plan updates live.

## What's mocked vs. real

The reasoning is rule-based today (fast, deterministic, offline — ideal for a
live demo). The *shape* of every agent call is written so a real Claude call
slots in behind `get_provider()` later with no change to routes, models, or
the frontend.
