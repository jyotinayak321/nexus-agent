"""
risk_agent.py
-------------
Evaluates technical, budget, and timeline risks against proposed architecture and plans.
Categorizes risks by severity and provides concrete mitigation strategies in English.
"""

from llm_provider import get_llm_provider

llm = get_llm_provider()


def risk_agent(state: dict) -> dict:
    goal = state.get("goal", "")
    plan = state.get("task_plan", "")
    budget = state.get("budget")
    deadline_days = state.get("deadline_days")

    budget_str = f"${budget:.2f} USD" if budget is not None else "Unspecified"
    deadline_str = f"{deadline_days} days" if deadline_days is not None else "Unspecified"

    prompt = f"""You are a Principal Security, Reliability, and Risk Engineer.
LANGUAGE RULE: You MUST output strictly and entirely in professional English. Do not use Hindi or any other language.

Goal:
{goal}

Proposed Task Plan:
{plan}

Budget Constraints: {budget_str}
Deadline Constraints: {deadline_str}

Instructions:
Perform an exhaustive risk analysis formatted into the following structured sections:
1. **Critical Architectural & Technical Risks**:
   - Provide 3 to 5 risks labeled explicitly with severity: `[HIGH]`, `[MEDIUM]`, or `[LOW]`.
   - Consider token rate limits, cyclic agent execution loops, vector retrieval irrelevance, and custom-code maintainability.
2. **Mitigation Strategies**:
   - For every identified risk, provide an actionable, technical mitigation strategy.
3. **Budget & Cost Feasibility Assessment**:
   - Evaluate whether the proposed solution fits within the allocated budget ({budget_str}).
   - Identify potential hidden costs (e.g. LLM token consumption, vector storage hosting).
4. **Timeline & Schedule Feasibility Assessment**:
   - Evaluate the realism of delivering the plan within the target deadline ({deadline_str}).
   - Highlight potential schedule bottlenecks and critical path items.
"""

    risks = llm.generate(prompt)
    return {**state, "risks": risks}
