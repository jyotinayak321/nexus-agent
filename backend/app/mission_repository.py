"""
Mission Repository — DB-backed replacement for mission.py's old
STORE: Dict[str, MissionResult] = {} dictionary.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from .db_models import AgentDecision, ExecutionLog, MissionRow, TaskRow
from .models import MissionInput, MissionResult


def save_mission(db: Session, result: MissionResult) -> None:
    row = db.get(MissionRow, result.mission_id)
    if row is None:
        row = MissionRow(mission_id=result.mission_id)
        db.add(row)

    row.input_json = result.input.model_dump_json()
    row.result_json = result.model_dump_json()
    db.flush()  # parent row DB mein pehle jaani chahiye child FK inserts se pehle

    db.query(TaskRow).filter(TaskRow.plan_id == result.mission_id).delete()
    db.query(AgentDecision).filter(AgentDecision.goal_id == result.mission_id).delete()
    db.query(ExecutionLog).filter(ExecutionLog.goal_id == result.mission_id).delete()

    for phase in result.decomposition:
        for task in phase.tasks:
            db.add(
                TaskRow(
                    id=task.id,
                    plan_id=result.mission_id,
                    title=task.title,
                    status=result.task_status.get(task.id, "pending"),
                    hours=task.hours,
                    assignee=task.assignee,
                )
            )

    for decision in result.debate:
        db.add(
            AgentDecision(
                goal_id=result.mission_id,
                agent_name=decision.topic,
                decision=decision.final_decision,
                reason=decision.rationale,
            )
        )

    for line in result.execution_log:
        db.add(ExecutionLog(goal_id=result.mission_id, action=line, result="ok", status="logged"))

    db.commit()


def get_mission(db: Session, mission_id: str) -> MissionResult | None:
    row = db.get(MissionRow, mission_id)
    if row is None:
        return None
    return MissionResult.model_validate_json(row.result_json)


def update_task_status(db: Session, mission_id: str, task_id: str, status: str) -> MissionResult | None:
    result = get_mission(db, mission_id)
    if result is None or task_id not in result.task_status:
        return None
    result.task_status[task_id] = status
    save_mission(db, result)
    return result