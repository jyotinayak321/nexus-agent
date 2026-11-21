"""
planning_agent.py
------------------
Deconstructs goals and research findings into actionable, structured implementation plans.
Outputs in professional English with deliverables, timelines, test cases, and budget alignment.
"""

from llm_provider import get_llm_provider

llm = get_llm_provider()


def planning_agent(state: dict) -> dict:
    goal = state["goal"]
    findings = state.get("research_findings", "")
    budget = state.get("budget")
    deadline_days = state.get("deadline_days")

    budget_info = f"${budget:.2f} USD" if budget is not None else "Not specified (assume standard development costs)"
    deadline_info = f"{deadline_days} days" if deadline_days is not None else "Not specified (assume standard pacing)"

    prompt = f"""You are a Lead AI Architect and Project Planner.
LANGUAGE RULE: You MUST output strictly and entirely in professional English. Do not use Hindi or any other language.

Goal:
{goal}

Research Findings:
{findings}

Constraints:
- Budget Limit: {budget_info}
- Target Deadline: {deadline_info}

Instructions:
Deconstruct this objective into a comprehensive, highly actionable plan with the following dedicated sections:
1. **Phased Implementation Plan**: 4 to 6 numbered phases with specific technical tasks and concrete deliverables.
2. **Technical Setup Guide**: Specific commands, environment configuration (Postgres, pgvector, Python dependencies), and ingestion pipeline setup.
3. **Test Cases & Quality Assurance**: 3 to 4 unit and integration test scenarios (e.g. vector retrieval accuracy, budget enforcement, language consistency).
4. **Implementation Timeline & Milestones**: Realistic pacing mapped to the target deadline ({deadline_info}).
5. **Budget & Resource Allocation**: Estimated token and tooling expenditure within the allocated budget ({budget_info}).

If the goal involves AI agent frameworks (e.g. LangChain, LangGraph, AutoGPT), ensure the plan outlines ingestion of PDF/TXT/MD, vector storage via pgvector, and stateful multi-agent execution.
"""

    plan = llm.generate(prompt)
    return {**state, "task_plan": plan}
