"""
review_agent.py
----------------
Kaam: Execution result verify karna. Agar kuch galat laga toh
'needs_replanning' flag set kar dena — isse system adaptive banta hai.
"""


def review_agent(state: dict) -> dict:
    execution_log = state.get("execution_log", "")

    # Simple rule-based check (real project mein LLM se bhi verify kar sakte ho)
    needs_replanning = "error" in execution_log.lower()

    return {
        **state,
        "needs_replanning": needs_replanning,
        "status": "review_complete",
    }
