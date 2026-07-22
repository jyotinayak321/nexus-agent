"""
Research Agent: turns each debated Decision into an evidence-based
recommendation card — recommendation, why, supporting evidence, alternative
considered. This is what a user reads before trusting the plan.
"""
from __future__ import annotations

from typing import List

from ..models import Decision, ResearchItem


def build_research(decisions: List[Decision]) -> List[ResearchItem]:
    items: List[ResearchItem] = []
    for d in decisions:
        evidence = [f"{op.icon} {op.agent.title()} Agent: {op.argument}" for op in d.opinions]
        alternative = next(
            (op.stance for op in d.opinions if op.stance and op.stance != d.final_decision),
            "No strong alternative — all agents converged.",
        )
        items.append(
            ResearchItem(
                topic=d.topic,
                recommendation=d.final_decision,
                reasoning=d.rationale,
                evidence=evidence,
                alternative=alternative,
            )
        )
    return items
