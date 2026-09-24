"""
graph.py
--------
LangGraph supervisor flow for NEXUS.
Flow: Research -> Planning -> Risk -> Decision -> Execution -> Review
"""

from langgraph.graph import StateGraph, END
from typing import Any, Optional, TypedDict

from agents.research_agent import research_agent
from agents.planning_agent import planning_agent
from agents.risk_agent import risk_agent
from agents.decision_agent import decision_agent
from agents.execution_agent import execution_agent
from agents.review_agent import review_agent


class NexusState(TypedDict, total=False):
    goal: str
    budget: Optional[float]
    deadline_days: Optional[int]
    rag_context: Optional[str]
    rag_sources: list[dict[str, Any]]
    research_findings: Optional[str]
    task_plan: Optional[str]
    risks: Optional[str]
    final_decision: Optional[str]
    execution_log: Optional[str]
    needs_replanning: Optional[bool]
    status: Optional[str]


def build_nexus_graph():
    graph = StateGraph(NexusState)

    graph.add_node("research", research_agent)
    graph.add_node("planning", planning_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("decision", decision_agent)
    graph.add_node("execution", execution_agent)
    graph.add_node("review", review_agent)

    graph.set_entry_point("research")
    graph.add_edge("research", "planning")
    graph.add_edge("planning", "risk")
    graph.add_edge("risk", "decision")
    graph.add_edge("decision", "execution")
    graph.add_edge("execution", "review")
    graph.add_edge("review", END)

    return graph.compile()


nexus_app = build_nexus_graph()
