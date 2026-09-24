"""
decision_agent.py
------------------
Kaam: Saare agents ka output dekh kar final decision lena.
Real-world analogy: yeh "senior manager" hai jo sabki report sunn kar
final call leta hai.
"""

from llm_provider import get_llm_provider

llm = get_llm_provider()


def decision_agent(state: dict) -> dict:
    findings = state.get("research_findings", "")
    plan = state.get("task_plan", "")
    risks = state.get("risks", "")

    prompt = f"""
    Research: {findings}
    Plan: {plan}
    Risks: {risks}

    In sabko dekh kar ek final recommendation do — kaunsa approach best hai
    aur kyun. 2-3 lines mein reasoning ke saath jawaab do.
    """

    decision = llm.generate(prompt)

    return {**state, "final_decision": decision}
