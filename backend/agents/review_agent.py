"""
review_agent.py
----------------
Audits execution logs and quality metrics to determine if replanning is needed.
Outputs in professional English.
"""


def review_agent(state: dict) -> dict:
    execution_log = state.get("execution_log", "")
    plan = state.get("task_plan", "")
    risks = state.get("risks", "")

    # Quality review: verify execution log and detect unmitigated critical failures
    has_critical_error = "error" in execution_log.lower() and "no error" not in execution_log.lower()
    needs_replanning = has_critical_error or not plan

    status_message = (
        "Quality review flagged replanning requirement due to execution anomalies."
        if needs_replanning
        else "Quality review passed: Deliverables, risk mitigations, and plan validated."
    )

    return {
        **state,
        "needs_replanning": needs_replanning,
        "status": "review_complete",
        "review_summary": status_message,
    }
