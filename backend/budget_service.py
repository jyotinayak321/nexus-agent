"""
budget_service.py
-----------------
Cost tracking, execution limits, and deadline validation for NEXUS AI.
"""

from typing import Any, Optional


def validate_goal_inputs(goal: str, budget: Optional[float], deadline_days: Optional[int]) -> None:
    """Validate user input constraints for goal submission."""
    cleaned_goal = (goal or "").strip()
    if len(cleaned_goal) < 3:
        raise ValueError("Goal description must be at least 3 characters long.")
    if len(cleaned_goal) > 5000:
        raise ValueError("Goal description cannot exceed 5000 characters.")

    if budget is not None:
        if budget < 0:
            raise ValueError("Budget cannot be negative.")
        if budget > 10_000_000:
            raise ValueError("Budget exceeds maximum allowable limit of $10,000,000.")

    if deadline_days is not None:
        if deadline_days <= 0:
            raise ValueError("Deadline must be at least 1 day.")
        if deadline_days > 3650:
            raise ValueError("Deadline cannot exceed 3650 days (10 years).")


def estimate_tokens(text: str) -> int:
    """Rough character-to-token heuristic (avg ~4 characters per token)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def calculate_cost_and_budget(
    state: dict[str, Any],
    budget: Optional[float],
    deadline_days: Optional[int],
) -> dict[str, Any]:
    """Calculate token estimates, model cost tracking, and feasibility status.
    
    Enforcement Note:
    - Token tracking is estimated from total prompt and generation characters.
    - USD cost uses standard competitive LLM inference rates ($0.0005 / 1k tokens).
    - Hard budget constraints flag 'exceeded' if the estimated operational cost exceeds budget.
    - Hardware, cloud infrastructure, and 3rd-party software license costs are estimated
      by the planning and risk agents and require human approval before deployment.
    """
    # Sum text across state fields
    text_corpus = (
        (state.get("goal") or "")
        + (state.get("rag_context") or "")
        + (state.get("research_findings") or "")
        + (state.get("task_plan") or "")
        + (state.get("risks") or "")
        + (state.get("final_decision") or "")
    )
    total_estimated_tokens = estimate_tokens(text_corpus)

    # Blended price heuristic: $0.0005 per 1,000 tokens
    estimated_cost_usd = round((total_estimated_tokens / 1000.0) * 0.0005, 5)

    # Budget status check
    if budget is None:
        budget_status = "unspecified"
        budget_notes = "No budget limit was specified. Execution proceeded without a monetary cap."
    elif budget == 0:
        budget_status = "zero_budget"
        budget_notes = "Zero budget specified. Open-source/free tier tools and self-hosted components recommended."
    elif estimated_cost_usd > budget:
        budget_status = "exceeded"
        budget_notes = f"Estimated LLM cost (${estimated_cost_usd:.5f}) exceeded allocated budget (${budget:.2f})."
    else:
        budget_status = "within_budget"
        budget_notes = f"Estimated LLM cost (${estimated_cost_usd:.5f}) is well within allocated budget (${budget:.2f})."

    # Deadline feasibility assessment
    if deadline_days is None:
        deadline_status = "unspecified"
        deadline_notes = "No deadline specified. Plan assumes standard implementation pacing."
    elif deadline_days < 3:
        deadline_status = "at_risk"
        deadline_notes = f"Aggressive deadline ({deadline_days} days). High risk of scope compression; prioritize MVP."
    elif deadline_days <= 14:
        deadline_status = "tight"
        deadline_notes = f"Moderate deadline ({deadline_days} days). Requires focused daily milestone tracking."
    else:
        deadline_status = "feasible"
        deadline_notes = f"Comfortable deadline ({deadline_days} days). Sufficient buffer for architecture, testing, and deployment."

    return {
        "estimated_tokens": total_estimated_tokens,
        "estimated_cost_usd": estimated_cost_usd,
        "budget_limit_usd": budget,
        "budget_status": budget_status,
        "budget_notes": budget_notes,
        "deadline_days": deadline_days,
        "deadline_status": deadline_status,
        "deadline_notes": deadline_notes,
        "enforcement_mode": "automated_tracking_and_agent_evaluation",
    }
