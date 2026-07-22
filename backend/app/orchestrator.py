"""
Goal-to-Execution pipeline: ties Research -> Debate -> Decomposition into one
MissionResult. This is the single place that defines the "spine" of NEXUS:

  GOAL -> UNDERSTAND -> RESEARCH -> DEBATE -> DECIDE -> DECOMPOSE -> PLAN
"""
from __future__ import annotations

from .agents.debate import run_debate
from .agents.decomposition import build_decomposition_with_team
from .agents.research import build_research
from .knowledge_base import Constraints
from .models import MissionInput, MissionResult


def constraints_from_input(input: MissionInput) -> Constraints:
    return Constraints(
        goal=input.goal,
        days=input.days,
        hours_per_day=input.hours_per_day,
        budget_inr=input.budget_inr,
        has_gpu=input.has_gpu,
        team_size=len(input.team),
        team_skills=[m.skills for m in input.team],
    )


def run_pipeline(mission_id: str, input: MissionInput) -> MissionResult:
    c = constraints_from_input(input)

    decisions = run_debate(c)
    research = build_research(decisions)
    phases, mvp_mode = build_decomposition_with_team(c, decisions, input.team)

    log = [
        f'Goal received: "{input.goal}"',
        f"Constraints parsed: {c.total_hours:.0f}h available over {input.days} days, "
        f"budget ₹{input.budget_inr:.0f}, GPU {'yes' if input.has_gpu else 'no'}, "
        f"team of {max(len(input.team), 1)}.",
        f"Research agent gathered evidence for {len(research)} key decisions.",
        f"Multi-agent debate (research/cost/technical/risk) resolved {len(decisions)} architecture decisions.",
        f"Decomposed into {len(phases)} phases ({'MVP mode — timeline is tight' if mvp_mode else 'full roadmap'}).",
        "Plan ready for execution.",
    ]

    task_status = {t.id: "pending" for p in phases for t in p.tasks}

    return MissionResult(
        mission_id=mission_id,
        input=input,
        total_hours=c.total_hours,
        mvp_mode=mvp_mode,
        decomposition=phases,
        research=research,
        debate=decisions,
        execution_log=log,
        task_status=task_status,
    )
