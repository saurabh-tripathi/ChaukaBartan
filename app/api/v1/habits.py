import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.enums import Priority
from app.models.goal import Goal
from app.models.habit import Habit, HabitFrequency, HabitLog, HabitStatus
from app.schemas.habit import (
    HabitCreate,
    HabitLogCreate,
    HabitLogResponse,
    HabitResponse,
    HabitUpdate,
)

router = APIRouter(prefix="/habits", tags=["habits"])


# ── Habit CRUD ────────────────────────────────────────────────────────────────

@router.get("", response_model=list[HabitResponse])
def list_habits(
    habit_status: Optional[HabitStatus] = Query(None, alias="status"),
    frequency: Optional[HabitFrequency] = Query(None),
    priority: Optional[Priority] = Query(None),
    goal_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Habit)
    if habit_status is not None:
        q = q.filter(Habit.status == habit_status)
    if frequency is not None:
        q = q.filter(Habit.frequency == frequency)
    if priority is not None:
        q = q.filter(Habit.priority == priority)
    if goal_id is not None:
        q = q.filter(Habit.goal_id == goal_id)
    return q.order_by(Habit.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(body: HabitCreate, db: Session = Depends(get_db)):
    if body.goal_id and not db.get(Goal, body.goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    habit = Habit(**body.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(habit_id: uuid.UUID, db: Session = Depends(get_db)):
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@router.patch("/{habit_id}", response_model=HabitResponse)
def update_habit(habit_id: uuid.UUID, body: HabitUpdate, db: Session = Depends(get_db)):
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    if body.goal_id is not None and not db.get(Goal, body.goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)
    db.commit()
    db.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: uuid.UUID, db: Session = Depends(get_db)):
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()


# ── Habit Logs ────────────────────────────────────────────────────────────────

@router.post(
    "/{habit_id}/log",
    response_model=HabitLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def log_habit(habit_id: uuid.UUID, body: HabitLogCreate, db: Session = Depends(get_db)):
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    log = HabitLog(habit_id=habit_id, **body.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/{habit_id}/logs", response_model=list[HabitLogResponse])
def list_habit_logs(
    habit_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    if not db.get(Habit, habit_id):
        raise HTTPException(status_code=404, detail="Habit not found")
    return (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id)
        .order_by(HabitLog.logged_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
