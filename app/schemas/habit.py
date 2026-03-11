import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import Priority
from app.models.habit import HabitFrequency, HabitStatus


class HabitCreate(BaseModel):
    title: str
    description: Optional[str] = None
    frequency: HabitFrequency
    priority: Priority = Priority.MEDIUM
    importance_note: Optional[str] = None
    goal_id: Optional[uuid.UUID] = None
    status: HabitStatus = HabitStatus.ACTIVE
    started_at: Optional[datetime] = None
    set_at: Optional[datetime] = None
    expected_duration_minutes: Optional[int] = None
    tags: list[str] = []


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[HabitFrequency] = None
    priority: Optional[Priority] = None
    importance_note: Optional[str] = None
    goal_id: Optional[uuid.UUID] = None
    status: Optional[HabitStatus] = None
    started_at: Optional[datetime] = None
    set_at: Optional[datetime] = None
    streak_count: Optional[int] = None
    expected_duration_minutes: Optional[int] = None
    tags: Optional[list[str]] = None


class HabitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: Optional[str]
    frequency: HabitFrequency
    priority: Priority
    importance_note: Optional[str]
    goal_id: Optional[uuid.UUID]
    status: HabitStatus
    started_at: Optional[datetime]
    set_at: Optional[datetime]
    streak_count: int
    expected_duration_minutes: Optional[int]
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class HabitLogCreate(BaseModel):
    logged_date: date
    notes: Optional[str] = None


class HabitLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    habit_id: uuid.UUID
    logged_date: date
    logged_at: datetime
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
