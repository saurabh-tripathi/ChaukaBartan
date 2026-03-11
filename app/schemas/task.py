import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Priority
from app.models.task import Frequency, InstanceStatus, TaskType


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: TaskType
    frequency: Frequency
    priority: Priority = Priority.MEDIUM
    importance_note: Optional[str] = None
    end_date: Optional[date] = None
    is_active: bool = True
    parent_task_id: Optional[uuid.UUID] = None
    goal_id: Optional[uuid.UUID] = None
    expected_duration_minutes: Optional[int] = None
    tags: list[str] = []


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[TaskType] = None
    frequency: Optional[Frequency] = None
    priority: Optional[Priority] = None
    importance_note: Optional[str] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    parent_task_id: Optional[uuid.UUID] = None
    goal_id: Optional[uuid.UUID] = None
    expected_duration_minutes: Optional[int] = None
    tags: Optional[list[str]] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: Optional[str]
    task_type: TaskType
    frequency: Frequency
    priority: Priority
    importance_note: Optional[str]
    end_date: Optional[date]
    is_active: bool
    parent_task_id: Optional[uuid.UUID]
    goal_id: Optional[uuid.UUID]
    expected_duration_minutes: Optional[int]
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class TaskInstanceCreate(BaseModel):
    scheduled_date: date
    status: InstanceStatus = InstanceStatus.PENDING


class TaskInstanceUpdate(BaseModel):
    status: InstanceStatus


class TaskInstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    scheduled_date: date
    status: InstanceStatus
    created_at: datetime
    updated_at: datetime


class TaskFeedbackCreate(BaseModel):
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class TaskFeedbackUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class TaskFeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_instance_id: uuid.UUID
    completed_at: Optional[datetime]
    duration_minutes: Optional[int]
    difficulty_rating: Optional[int]
    satisfaction_rating: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


# ── Flat instance response (for completed tasks page) ─────────────────────────

class FlatInstanceTaskSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    goal_id: Optional[uuid.UUID]
    goal_title: Optional[str] = None
    tags: list[str]
    expected_duration_minutes: Optional[int]


class FlatInstanceFeedbackSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    duration_minutes: Optional[int]
    difficulty_rating: Optional[int]
    satisfaction_rating: Optional[int]
    notes: Optional[str]


class FlatInstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_instance_id: uuid.UUID
    scheduled_date: date
    status: InstanceStatus
    task: FlatInstanceTaskSummary
    feedback: Optional[FlatInstanceFeedbackSummary]
