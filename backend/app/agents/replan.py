"""
Self-Correcting Agent: the difference between "planning tool" and "mission
agent". A free-text blocker report is parsed into concrete constraint
changes, the whole pipeline is re-run, and the before/after decisions are
diffed so the user sees exactly what changed and why — not just a new plan
dropped on top of the old one.

  DETECT FAILURE -> ANALYZE -> FIND ALTERNATIVE -> CHANGE PLAN -> VERIFY
"""
from __future__ import annotations

import re
from typing import List, Tuple

from ..models import MissionInput, MissionResult
from ..orchestrator import run_pipeline


def _parse_blocker(text: str, current: MissionInput) -> Tuple[MissionInput, List[str]]:
    t = text.lower()
    changes: List[str] = []
    updated = current.model_copy(deep=True)
    numbers = [int(n) for n in re.findall(r"\d+", t)]

    if "gpu" in t and updated.has_gpu:
        updated.has_gpu = False
        changes.append("GPU marked unavailable")

    if "budget" in t or "₹" in text or "rs" in t or "money" in t:
        if any(k in t for k in ("zero", "none", "no budget", "no money", "cut to zero")):
            if updated.budget_inr != 0:
                updated.budget_inr = 0
                changes.append("Budget reduced to ₹0")
        elif numbers:
            new_budget = float(numbers[0])
            if new_budget < updated.budget_inr:
                updated.budget_inr = new_budget
                changes.append(f"Budget reduced to ₹{new_budget:.0f}")

    if any(k in t for k in ("day", "deadline", "timeline", "time")) and numbers:
        candidate = numbers[0]
        if 0 < candidate < updated.days:
            updated.days = candidate
            changes.append(f"Timeline shortened to {candidate} days")

    if any(k in t for k in ("left", "quit", "unavailable", "dropped out", "resign", "sick")):
        removed = next((m for m in updated.team if m.name.lower() in t), None)
        if removed is None and updated.team and any(k in t for k in ("member", "teammate", "developer")):
            removed = updated.team[-1]
        if removed is not None:
            updated.team = [m for m in updated.team if m.name != removed.name]
            changes.append(f"Removed team member '{removed.name}' from the roster")

    return updated, changes


def apply_blocker(current: MissionResult, blocker_text: str) -> dict:
    narrative: List[str] = [f'Blocker reported: "{blocker_text}"', "Detecting affected constraints..."]

    updated_input, changes = _parse_blocker(blocker_text, current.input)

    if not changes:
        narrative.append(
            "No concrete constraint change could be extracted from that description — logged as a risk note, plan unchanged."
        )
        return {
            "narrative": narrative,
            "changed_decisions": [],
            "changed": False,
            "mission": current,
        }

    narrative.append("Detected change(s): " + "; ".join(changes))
    narrative.append("Re-running research, debate and decomposition against the updated constraints...")

    new_result = run_pipeline(current.mission_id, updated_input)
    new_result.task_status = {
        task_id: current.task_status.get(task_id, status) for task_id, status in new_result.task_status.items()
    }

    base_map = {d.topic: d.final_decision for d in current.debate}
    decision_changes = [
        f"{d.topic}: “{base_map.get(d.topic)}” → “{d.final_decision}”"
        for d in new_result.debate
        if base_map.get(d.topic) != d.final_decision
    ]

    if decision_changes:
        narrative.append("Plan adapted: " + "; ".join(decision_changes))
    else:
        narrative.append("Core architecture decisions still hold — only task scope/timeline scaled.")

    if new_result.mvp_mode and not current.mvp_mode:
        narrative.append("Switched into MVP mode — the roadmap no longer fits the available time.")
    elif not new_result.mvp_mode and current.mvp_mode:
        narrative.append("Timeline eased — expanded back out of MVP mode.")

    narrative.append("Replanning complete — plan below reflects the new reality.")
    new_result.execution_log = current.execution_log + narrative

    return {
        "narrative": narrative,
        "changed_decisions": decision_changes,
        "changed": True,
        "mission": new_result,
    }
