from __future__ import annotations

import uuid
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..agents.replan import apply_blocker
from ..agents.simulate import SCENARIOS, run_scenario
from ..database import get_db
from ..mission_repository import get_mission, save_mission, update_task_status
from ..models import BlockerRequest, MissionInput, MissionResult, ScenarioResult, TaskStatusUpdate
from ..orchestrator import run_pipeline

router = APIRouter(prefix="/api/mission", tags=["mission"])


def _get_or_404(db: Session, mission_id: str) -> MissionResult:
    mission = get_mission(db, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.post("", response_model=MissionResult)
def create_mission(payload: MissionInput, db: Session = Depends(get_db)) -> MissionResult:
    mission_id = str(uuid.uuid4())[:8]
    result = run_pipeline(mission_id, payload)
    save_mission(db, result)
    return result


@router.get("/{mission_id}", response_model=MissionResult)
def get_mission_route(mission_id: str, db: Session = Depends(get_db)) -> MissionResult:
    return _get_or_404(db, mission_id)


@router.get("/{mission_id}/scenarios")
def list_scenarios(mission_id: str, db: Session = Depends(get_db)) -> List[Dict[str, str]]:
    _get_or_404(db, mission_id)
    return [{"key": k, "label": v} for k, v in SCENARIOS.items()]


@router.post("/{mission_id}/simulate/{scenario_key}", response_model=ScenarioResult)
def simulate(mission_id: str, scenario_key: str, db: Session = Depends(get_db)) -> ScenarioResult:
    mission = _get_or_404(db, mission_id)
    try:
        return run_scenario(mission, scenario_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{mission_id}/blocker")
def report_blocker(mission_id: str, payload: BlockerRequest, db: Session = Depends(get_db)) -> dict:
    mission = _get_or_404(db, mission_id)
    outcome = apply_blocker(mission, payload.description)
    save_mission(db, outcome["mission"])
    return {
        "narrative": outcome["narrative"],
        "changed_decisions": outcome["changed_decisions"],
        "changed": outcome["changed"],
        "mission": outcome["mission"],
    }


@router.patch("/{mission_id}/task/{task_id}", response_model=MissionResult)
def update_task_status_route(
    mission_id: str, task_id: str, payload: TaskStatusUpdate, db: Session = Depends(get_db)
) -> MissionResult:
    updated = update_task_status(db, mission_id, task_id, payload.status)
    if updated is None:
        raise HTTPException(status_code=404, detail="Mission or task not found")
    return updated