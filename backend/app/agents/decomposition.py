"""
Goal Decomposition Agent.

Breaks the goal into phases/tasks scaled to the *actual* hours available
(days x hours_per_day), not a fixed template. Below a tight-timeline
threshold it collapses straight into MVP mode: fewer phases, no polish work,
every remaining hour aimed at a demoable core.

Task titles are generated from the debate's winning decisions, so the plan
visibly reflects *why* each task exists rather than being generic filler.
"""
from __future__ import annotations

import itertools
from typing import Dict, List, Tuple

from ..knowledge_base import Constraints
from ..models import Decision, Phase, Task
from ..models import TeamMember

SKILL_HINTS = {
    "research": ("python", "ai", "ml", "research"),
    "core": ("python", "ai", "ml"),
    "requirements": ("python", "data", "sql", "database"),
    "backend": ("python", "backend", "api", "fastapi"),
    "frontend": ("react", "frontend", "javascript", "js", "css"),
    "test": ("qa", "test", "python"),
    "deploy": ("devops", "cloud", "deployment"),
}


def _decision_by_topic(decisions: List[Decision], topic: str) -> Decision:
    return next(d for d in decisions if d.topic == topic)


def _assignee_pool(team: List[TeamMember]):
    if not team:
        return None
    return itertools.cycle([m.name for m in team])


def _pick_assignee(category: str, team: List[TeamMember], fallback_cycle) -> str:
    if not team:
        return "You"
    hints = SKILL_HINTS.get(category, ())
    for member in team:
        skills = member.skills.lower()
        if any(h in skills for h in hints):
            return member.name
    return next(fallback_cycle)


def _make_phase(
    phase_id: str,
    title: str,
    weight: float,
    total_hours: float,
    task_specs: List[Tuple[str, str]],  # (title, skill-category)
    team: List[TeamMember],
    fallback_cycle,
) -> Phase:
    phase_hours = round(total_hours * weight, 1)
    per_task = round(phase_hours / max(len(task_specs), 1), 1)
    tasks = [
        Task(
            id=f"{phase_id}-t{i + 1}",
            title=t_title,
            hours=per_task,
            assignee=_pick_assignee(category, team, fallback_cycle),
        )
        for i, (t_title, category) in enumerate(task_specs)
    ]
    return Phase(id=phase_id, title=title, tasks=tasks)


def build_decomposition_with_team(
    c: Constraints, decisions: List[Decision], team: List[TeamMember]
) -> Tuple[List[Phase], bool]:
    model_d = _decision_by_topic(decisions, "AI Model Hosting")
    db_d = _decision_by_topic(decisions, "Database & Retrieval")
    backend_d = _decision_by_topic(decisions, "Backend Framework")
    deploy_d = _decision_by_topic(decisions, "Deployment")
    frontend_d = _decision_by_topic(decisions, "Frontend")
    return _build(c, decisions, model_d, db_d, backend_d, deploy_d, frontend_d, team)


def _build(
    c: Constraints,
    decisions: List[Decision],
    model_d: Decision,
    db_d: Decision,
    backend_d: Decision,
    deploy_d: Decision,
    frontend_d: Decision,
    team: List[TeamMember],
) -> Tuple[List[Phase], bool]:
    total_hours = c.total_hours
    mvp_mode = c.is_tight_timeline
    fallback_cycle = _assignee_pool(team)

    if mvp_mode:
        specs: List[Tuple[str, str, float, List[Tuple[str, str]]]] = [
            (
                "p1",
                "Research & Setup",
                0.15,
                [
                    ("Clarify problem statement & one success metric", "research"),
                    (f"Scaffold {backend_d.final_decision} project + {db_d.final_decision}", "backend"),
                ],
            ),
            (
                "p2",
                "Core Build (MVP)",
                0.50,
                [
                    (f"Implement core AI logic using {model_d.final_decision}", "core"),
                    ("Expose core logic via a minimal API", "backend"),
                ],
            ),
            (
                "p3",
                "Integrate & Connect",
                0.25,
                [(f"Build {frontend_d.final_decision} to call the API", "frontend")],
            ),
            (
                "p4",
                "Quick Test & Deploy",
                0.10,
                [
                    ("Smoke-test the happy path end to end", "test"),
                    (f"Deploy via {deploy_d.final_decision}", "deploy"),
                ],
            ),
        ]
    else:
        specs = [
            (
                "p1",
                "Research & Planning",
                0.10,
                [
                    ("Clarify problem statement & success metrics", "research"),
                    (f"Validate evidence behind {model_d.final_decision}", "research"),
                ],
            ),
            (
                "p2",
                "Requirements & Data",
                0.15,
                [
                    (f"Define data schema in {db_d.final_decision}", "requirements"),
                    ("Collect / prepare sample dataset", "requirements"),
                ],
            ),
            (
                "p3",
                "Core Build",
                0.30,
                [
                    (f"Implement core AI logic using {model_d.final_decision}", "core"),
                    ("Write core business logic & API contracts", "core"),
                ],
            ),
            (
                "p4",
                "Backend Integration",
                0.15,
                [
                    (f"Build REST endpoints with {backend_d.final_decision}", "backend"),
                    ("Wire model + database into the backend service", "backend"),
                ],
            ),
            (
                "p5",
                "Frontend",
                0.15,
                [
                    (f"Build UI with {frontend_d.final_decision}", "frontend"),
                    ("Connect frontend to backend API", "frontend"),
                ],
            ),
            (
                "p6",
                "Testing & QA",
                0.10,
                [
                    ("Write unit tests for core logic", "test"),
                    ("End-to-end manual testing pass", "test"),
                ],
            ),
            (
                "p7",
                "Deployment",
                0.05,
                [(f"Deploy via {deploy_d.final_decision}", "deploy")],
            ),
        ]

    phases = [
        _make_phase(pid, title, weight, total_hours, tasks, team, fallback_cycle)
        for pid, title, weight, tasks in specs
    ]
    return phases, mvp_mode
