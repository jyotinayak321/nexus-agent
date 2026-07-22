from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Constraints:
    goal: str
    days: int
    hours_per_day: float
    budget_inr: float
    has_gpu: bool
    team_size: int
    team_skills: List[str] = field(default_factory=list)

    @property
    def total_hours(self) -> float:
        return round(self.days * self.hours_per_day, 1)

    @property
    def goal_lower(self) -> str:
        return self.goal.lower()

    @property
    def is_zero_budget(self) -> bool:
        return self.budget_inr <= 0

    @property
    def is_low_budget(self) -> bool:
        return 0 < self.budget_inr <= 2000

    @property
    def is_tight_timeline(self) -> bool:
        return self.total_hours <= 20

    @property
    def team_skills_text(self) -> str:
        return " ".join(self.team_skills).lower()

    def has_skill(self, *keywords: str) -> bool:
        text = self.team_skills_text
        return any(k in text for k in keywords)
