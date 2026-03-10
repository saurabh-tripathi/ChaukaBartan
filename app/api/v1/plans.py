import uuid
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.habit import Habit
from app.models.plan import Plan, PlanItem, PlanStatus
from app.models.task import Task, TaskInstance
from app.modules.plan.builder import generate_plan
from app.schemas.plan import (
    PlanGenerate,
    PlanItemAdd,
    PlanItemResponse,
    PlanItemUpdate,
    PlanResponse,
    PlanSummaryResponse,
    PlanUpdate,
)

router = APIRouter(prefix="/plans", tags=["plans"])

# Eager-load options for full plan detail (avoids N+1 on item → task_instance → task)
_PLAN_DETAIL_OPTIONS = [
    selectinload(Plan.items).options(
        selectinload(PlanItem.task_instance).selectinload(TaskInstance.task),
        selectinload(PlanItem.habit),
    )
]


def _load_plan_detail(plan_id: uuid.UUID, db: Session) -> Plan:
    plan = (
        db.query(Plan)
        .filter(Plan.id == plan_id)
        .options(*_PLAN_DETAIL_OPTIONS)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


# ── Plan endpoints ─────────────────────────────────────────────────────────────

@router.post("/generate", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def generate(body: PlanGenerate, db: Session = Depends(get_db)):
    plan_date = body.plan_date or (date.today() + timedelta(days=1))
    try:
        plan_id = generate_plan(db, plan_date, body.notes)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return _load_plan_detail(plan_id, db)


@router.get("", response_model=list[PlanSummaryResponse])
def list_plans(
    plan_status: Optional[PlanStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Plan)
    if plan_status is not None:
        q = q.filter(Plan.status == plan_status)
    return q.order_by(Plan.plan_date.desc()).offset(skip).limit(limit).all()


@router.get("/by-date/{plan_date}", response_model=PlanResponse)
def get_plan_by_date(plan_date: date, db: Session = Depends(get_db)):
    plan = (
        db.query(Plan)
        .filter(Plan.plan_date == plan_date)
        .options(*_PLAN_DETAIL_OPTIONS)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found for this date")
    return plan


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: uuid.UUID, db: Session = Depends(get_db)):
    return _load_plan_detail(plan_id, db)


@router.patch("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: uuid.UUID, body: PlanUpdate, db: Session = Depends(get_db)):
    plan = _load_plan_detail(plan_id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    return _load_plan_detail(plan_id, db)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: uuid.UUID, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()


# ── Plan item endpoints ────────────────────────────────────────────────────────

@router.post("/{plan_id}/items", response_model=PlanItemResponse, status_code=status.HTTP_201_CREATED)
def add_item(plan_id: uuid.UUID, body: PlanItemAdd, db: Session = Depends(get_db)):
    if not db.get(Plan, plan_id):
        raise HTTPException(status_code=404, detail="Plan not found")
    if not body.task_instance_id and not body.habit_id:
        raise HTTPException(status_code=400, detail="Either task_instance_id or habit_id is required")
    if body.task_instance_id and body.habit_id:
        raise HTTPException(status_code=400, detail="Provide task_instance_id or habit_id, not both")
    if body.task_instance_id and not db.get(TaskInstance, body.task_instance_id):
        raise HTTPException(status_code=404, detail="Task instance not found")
    if body.habit_id and not db.get(Habit, body.habit_id):
        raise HTTPException(status_code=404, detail="Habit not found")

    next_order = db.query(PlanItem).filter(PlanItem.plan_id == plan_id).count()
    item = PlanItem(
        plan_id=plan_id,
        task_instance_id=body.task_instance_id,
        habit_id=body.habit_id,
        scheduled_time=body.scheduled_time,
        display_order=next_order,
    )
    db.add(item)
    db.commit()

    return (
        db.query(PlanItem)
        .filter(PlanItem.id == item.id)
        .options(
            selectinload(PlanItem.task_instance).selectinload(TaskInstance.task),
            selectinload(PlanItem.habit),
        )
        .first()
    )


@router.patch("/{plan_id}/items/{item_id}", response_model=PlanItemResponse)
def update_item(
    plan_id: uuid.UUID,
    item_id: uuid.UUID,
    body: PlanItemUpdate,
    db: Session = Depends(get_db),
):
    item = db.get(PlanItem, item_id)
    if not item or item.plan_id != plan_id:
        raise HTTPException(status_code=404, detail="Plan item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()

    return (
        db.query(PlanItem)
        .filter(PlanItem.id == item_id)
        .options(
            selectinload(PlanItem.task_instance).selectinload(TaskInstance.task),
            selectinload(PlanItem.habit),
        )
        .first()
    )


@router.delete("/{plan_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(plan_id: uuid.UUID, item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(PlanItem, item_id)
    if not item or item.plan_id != plan_id:
        raise HTTPException(status_code=404, detail="Plan item not found")
    db.delete(item)
    db.commit()
