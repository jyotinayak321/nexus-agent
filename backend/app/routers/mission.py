from __future__ import annotations

import uuid
from typing import Dict, List

from fastapi import APIRouter, HTTPException

from ..agents.replan import apply_blocker
from ..agents.simulate import SCENARIOS, run_scenario
from ..models import BlockerRequest, MissionInput, MissionResult, ScenarioResult, TaskStatusUpdate
from ..orchestrator import run_pipeline

router = APIRouter(prefix="/api/mission", tags=["mission"])

STORE: Dict[str, MissionResult] = {}


def _get_or_404(mission_id: str) -> MissionResult:
    mission = STORE.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.post("", response_model=MissionResult)
def create_mission(payload: MissionInput) -> MissionResult:
    mission_id = str(uuid.uuid4())[:8]
    result = run_pipeline(mission_id, payload)
    STORE[mission_id] = result
    return result


@router.get("/{mission_id}", response_model=MissionResult)
def get_mission(mission_id: str) -> MissionResult:
    return _get_or_404(mission_id)


@router.get("/{mission_id}/scenarios")
def list_scenarios(mission_id: str) -> List[Dict[str, str]]:
    _get_or_404(mission_id)
    return [{"key": k, "label": v} for k, v in SCENARIOS.items()]


@router.post("/{mission_id}/simulate/{scenario_key}", response_model=ScenarioResult)
def simulate(mission_id: str, scenario_key: str) -> ScenarioResult:
    mission = _get_or_404(mission_id)
    try:
        return run_scenario(mission, scenario_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{mission_id}/blocker")
def report_blocker(mission_id: str, payload: BlockerRequest) -> dict:
    mission = _get_or_404(mission_id)
    outcome = apply_blocker(mission, payload.description)
    STORE[mission_id] = outcome["mission"]
    return {
        "narrative": outcome["narrative"],
        "changed_decisions": outcome["changed_decisions"],
        "changed": outcome["changed"],
        "mission": outcome["mission"],
    }


@router.patch("/{mission_id}/task/{task_id}", response_model=MissionResult)
def update_task_status(mission_id: str, task_id: str, payload: TaskStatusUpdate) -> MissionResult:
    mission = _get_or_404(mission_id)
    if task_id not in mission.task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    mission.task_status[task_id] = payload.status
    return mission
