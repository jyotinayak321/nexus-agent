from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class TeamMember(BaseModel):
    name: str
    skills: str = ""  # free text e.g. "python, ai, ml"


class MissionInput(BaseModel):
    goal: str
    days: int = Field(gt=0, le=365)
    hours_per_day: float = Field(gt=0, le=16)
    budget_inr: float = Field(ge=0)
    has_gpu: bool = False
    team: List[TeamMember] = Field(default_factory=list)
    notes: Optional[str] = None


class Task(BaseModel):
    id: str
    title: str
    hours: float
    assignee: str = "You"


class Phase(BaseModel):
    id: str
    title: str
    tasks: List[Task]

    @property
    def total_hours(self) -> float:
        return sum(t.hours for t in self.tasks)


class AgentOpinion(BaseModel):
    agent: str  # research | cost | technical | risk
    icon: str
    stance: str
    argument: str


class Decision(BaseModel):
    topic: str
    opinions: List[AgentOpinion]
    final_decision: str
    rationale: str


class ResearchItem(BaseModel):
    topic: str
    recommendation: str
    reasoning: str
    evidence: List[str]
    alternative: str


class BlockerRequest(BaseModel):
    description: str


class TaskStatusUpdate(BaseModel):
    status: str  # pending | in_progress | done | blocked


class MissionResult(BaseModel):
    mission_id: str
    input: MissionInput
    total_hours: float
    mvp_mode: bool
    decomposition: List[Phase]
    research: List[ResearchItem]
    debate: List[Decision]
    execution_log: List[str]
    task_status: dict = Field(default_factory=dict)


class ScenarioResult(BaseModel):
    label: str
    total_hours: float
    mvp_mode: bool
    changed_decisions: List[str]
    phase_count: int
    summary: str
