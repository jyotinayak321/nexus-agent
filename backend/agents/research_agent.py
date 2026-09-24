"""
research_agent.py
-----------------
Research node enriched with retrieved local document context (RAG).
"""

from llm_provider import get_llm_provider

llm = get_llm_provider()


def research_agent(state: dict) -> dict:
    goal = state["goal"]
    rag_context = state.get("rag_context", "")

    if rag_context:
        prompt = f"""
User goal:
{goal}

Retrieved context from the user's uploaded documents:
{rag_context}

Use the retrieved context as the primary evidence. Do not invent details that
are not supported by the context. Summarize the most relevant facts,
technologies and constraints in 3-6 concise bullet points. When useful,
mention the source label exactly as provided (for example [manual.pdf#chunk-2]).
"""
    else:
        prompt = f"""
User goal:
{goal}

No relevant local document context is available. Provide 3-4 concise bullet
points covering important technologies, constraints and best practices.
"""

    findings = llm.generate(prompt)
    return {**state, "research_findings": findings}
