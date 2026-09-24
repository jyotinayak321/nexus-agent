"""
planning_agent.py
------------------
Kaam: Goal + research findings ko dekh kar chhote tasks mein todna.
Real-world analogy: yeh ek "project manager" hai jo ek badi problem ko
to-do list mein convert karta hai.
"""

from llm_provider import get_llm_provider

llm = get_llm_provider()


def planning_agent(state: dict) -> dict:
    goal = state["goal"]
    findings = state.get("research_findings", "")

    prompt = f"""
    Goal: {goal}
    Research findings: {findings}

    Is goal ko 4-6 chhote, actionable tasks mein todo.
    Har task ek numbered list item ke roop mein do.
    """

    plan = llm.generate(prompt)

    return {**state, "task_plan": plan}
