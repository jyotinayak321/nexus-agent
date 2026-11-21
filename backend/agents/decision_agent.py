"""
decision_agent.py
------------------
Synthesizes research, plans, and risk assessments into a final architectural decision.
Generates weighted scoring comparison tables and executive recommendations in English.
"""

from llm_provider import get_llm_provider

llm = get_llm_provider()


def decision_agent(state: dict) -> dict:
    goal = state.get("goal", "")
    findings = state.get("research_findings", "")
    plan = state.get("task_plan", "")
    risks = state.get("risks", "")
    budget = state.get("budget")
    deadline_days = state.get("deadline_days")

    budget_str = f"${budget:.2f} USD" if budget is not None else "Unspecified"
    deadline_str = f"{deadline_days} days" if deadline_days is not None else "Unspecified"

    prompt = f"""You are the Chief Technology Officer and Final Decision Maker.
LANGUAGE RULE: You MUST output strictly and entirely in professional English. Do not use Hindi or any other language.

Goal:
{goal}

Research Findings:
{findings}

Task Plan:
{plan}

Risk Analysis:
{risks}

Budget: {budget_str} | Target Deadline: {deadline_str}

Instructions:
Synthesize all prior agent outputs and provide an authoritative decision structured as follows:

1. **Executive Decision & Selected Architecture**:
   - Explicitly declare the recommended framework, pattern, or approach with concise technical rationale.
2. **Weighted Scoring Evaluation Table**:
   - Provide a Markdown table comparing viable options (e.g., if comparing frameworks, compare LangGraph, LangChain, and AutoGPT; or architecture alternatives).
   - Columns: `Evaluation Criteria`, `Weight (%)`, Candidate Option columns, `Score (out of 10)`.
   - Criteria should include: Multi-agent orchestration, Production reliability, Vector/RAG integration (pgvector), Budget/Token efficiency, and Custom-code requirements.
   - Include a final `Weighted Overall Score` row.
3. **Core Architectural Deliverables**:
   - Summary Setup Guide (key configuration commands).
   - High-level phased implementation timeline aligned with {deadline_str}.
   - Recommended Test Cases for production validation.
4. **Budget & Timeline Feasibility Verdict**:
   - Clear statement on whether the selected architecture is feasible within {budget_str} and {deadline_str}.
5. **Verified Facts vs. Assumptions**:
   - Clearly delineate which conclusions are verified from local evidence vs. assumptions requiring future validation.
"""

    decision = llm.generate(prompt)
    return {**state, "final_decision": decision}
