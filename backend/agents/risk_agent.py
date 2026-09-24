"""
risk_agent.py
-------------
Kaam: Plan ko dekh kar risks nikalna — time, budget, resources ke against.
Real-world analogy: yeh "quality/safety checker" hai jo bolta hai
"yeh plan risky hai kyunki budget zero hai."
"""

from llm_provider import get_llm_provider

llm = get_llm_provider()


def risk_agent(state: dict) -> dict:
    plan = state.get("task_plan", "")
    budget = state.get("budget", "not specified")
    deadline = state.get("deadline_days", "not specified")

    prompt = f"""
    Task plan: {plan}
    Budget: {budget}
    Deadline (days): {deadline}

    Is plan ke 3 sabse bade risks batao (low/medium/high severity ke saath).
    """

    risks = llm.generate(prompt)

    return {**state, "risks": risks}
