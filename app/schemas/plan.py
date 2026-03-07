import uuid
from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import Priority
from app.models.habit import HabitFrequency
from app.models.plan import ItemStatus, PlanStatus
from app.models.task import InstanceStatus, TaskType


class PlanGenerate(BaseModel):
    plan_date: Optional[date] = None  # defaults to tomorrow
    notes: Optional[str] = None


class PlanUpdate(BaseModel):
    status: Optional[PlanStatus] = None
    notes: Optional[str] = None


class PlanItemAdd(BaseModel):
    task_instance_id: Optional[uuid.UUID] = None
    habit_id: Optional[uuid.UUID] = None
    scheduled_time: Optional[time] = None


class PlanItemUpdate(BaseModel):
    status: Optional[ItemStatus] = None
    scheduled_time: Optional[time] = None
    display_order: Optional[int] = None


# ── Nested summaries for rich iOS-friendly item responses ─────────────────────

class TaskSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    priority: Priority
    task_type: TaskType


class TaskInstanceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    scheduled_date: date
    status: InstanceStatus
    task: TaskSummary


class HabitSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    priority: Priority
    frequency: HabitFrequency
    streak_count: int


class PlanItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plan_id: uuid.UUID
    task_instance_id: Optional[uuid.UUID]
    habit_id: Optional[uuid.UUID]
    scheduled_time: Optional[time]
    display_order: int
    status: ItemStatus
    task_instance: Optional[TaskInstanceSummary]
    habit: Optional[HabitSummary]
    created_at: datetime
    updated_at: datetime


class PlanSummaryResponse(BaseModel):
    """Lightweight response for list endpoints — no items."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plan_date: date
    status: PlanStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class PlanResponse(BaseModel):
    """Full plan with all items and nested task/habit detail."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plan_date: date
    status: PlanStatus
    notes: Optional[str]
    items: list[PlanItemResponse]
    created_at: datetime
    updated_at: datetime
