"""
research_agent.py
-----------------
Research node enriched with retrieved document context (RAG).
Enforces English output, factual grounding, and explicit verification status.
"""

from llm_provider import get_llm_provider

llm = get_llm_provider()


def research_agent(state: dict) -> dict:
    goal = state["goal"]
    rag_context = state.get("rag_context", "")

    system_rules = (
        "LANGUAGE RULE: You MUST output strictly and entirely in professional English. "
        "Even if any retrieved context, document excerpts, or questions contain Hindi or other languages, "
        "translate all findings and write your entire summary strictly in English.\n"
        "FACTUALITY RULE: Do not fabricate sources, completed actions, or unsupported benchmarks. "
        "Clearly distinguish verified facts from assumptions. State explicitly: "
        "'Web search is currently not connected; findings are derived from local uploaded documents and model baseline knowledge.'\n"
        "FRAMEWORK RULE: If the goal involves comparing AI frameworks (e.g., LangChain, LangGraph, AutoGPT), "
        "include architectural analysis, multi-agent capabilities, vector database options (such as PostgreSQL/pgvector), "
        "document ingestion (PDF/TXT/MD), and custom-code requirements."
    )

    if rag_context:
        prompt = f"""{system_rules}

User goal:
{goal}

Retrieved context from user's uploaded documents:
{rag_context}

Instructions:
1. Use the retrieved context as primary evidence. When referencing context, cite the source label (e.g. [manual.pdf#chunk-2]).
2. Summarize the core technologies, architectural facts, and constraints in 4-6 concise, bulleted sections.
3. Identify key trade-offs, vector storage considerations (e.g. pgvector), and multi-agent requirements.
4. Conclude with an explicit 'Verification & Assumptions' section detailing what is verified vs. assumed.
"""
    else:
        prompt = f"""{system_rules}

User goal:
{goal}

Instructions:
1. Note that no relevant local document context was found in the knowledge base.
2. Provide a thorough, structured technical overview of technologies, architectures, and best practices relevant to the goal.
3. If comparing frameworks (such as LangChain, LangGraph, AutoGPT), detail architecture, multi-agent capabilities, and pgvector storage.
4. Conclude with an explicit 'Verification & Assumptions' section noting that findings are based on model baseline knowledge without live web search.
"""

    findings = llm.generate(prompt)
    return {**state, "research_findings": findings}
