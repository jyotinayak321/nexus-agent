"""
What-if Simulation Agent: replays the whole pipeline against a hypothetically
changed constraint set WITHOUT persisting anything, then diffs the result
against the live mission so the user can compare scenarios before committing.
"""
from __future__ import annotations

from typing import Callable, Dict

from ..models import MissionInput, MissionResult, ScenarioResult
from ..orchestrator import run_pipeline

SCENARIOS: Dict[str, str] = {
    "reduce_deadline_7d": "Deadline drops to 7 days",
    "no_gpu": "GPU becomes unavailable",
    "zero_budget": "Budget cut to ₹0",
    "solo_dev": "Team shrinks to solo (just you)",
    "double_budget": "Budget doubles",
}

_MUTATORS: Dict[str, Callable[[MissionInput], MissionInput]] = {
    "reduce_deadline_7d": lambda i: i.model_copy(update={"days": min(i.days, 7)}),
    "no_gpu": lambda i: i.model_copy(update={"has_gpu": False}),
    "zero_budget": lambda i: i.model_copy(update={"budget_inr": 0}),
    "solo_dev": lambda i: i.model_copy(update={"team": []}),
    "double_budget": lambda i: i.model_copy(update={"budget_inr": i.budget_inr * 2 if i.budget_inr > 0 else 5000}),
}


def run_scenario(base_result: MissionResult, scenario_key: str) -> ScenarioResult:
    if scenario_key not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{scenario_key}'")

    mutated_input = _MUTATORS[scenario_key](base_result.input)
    scenario_result = run_pipeline(f"sim-{scenario_key}", mutated_input)

    base_map = {d.topic: d.final_decision for d in base_result.debate}
    changed = [
        f"{d.topic}: “{base_map.get(d.topic)}” → “{d.final_decision}”"
        for d in scenario_result.debate
        if base_map.get(d.topic) != d.final_decision
    ]

    bits = []
    if scenario_result.mvp_mode != base_result.mvp_mode:
        bits.append("switches to MVP mode" if scenario_result.mvp_mode else "unlocks the full roadmap")
    if len(scenario_result.decomposition) != len(base_result.decomposition):
        bits.append(f"phase count {len(base_result.decomposition)} → {len(scenario_result.decomposition)}")
    if changed:
        bits.append(f"{len(changed)} architecture decision(s) flip")
    summary = "; ".join(bits) if bits else "Plan stays materially the same."

    return ScenarioResult(
        label=SCENARIOS[scenario_key],
        total_hours=scenario_result.total_hours,
        mvp_mode=scenario_result.mvp_mode,
        changed_decisions=changed,
        phase_count=len(scenario_result.decomposition),
        summary=summary,
    )
