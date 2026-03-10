import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import Priority
from app.models.goal import GoalStatus, GoalTimeframe


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    timeframe: GoalTimeframe
    priority: Priority = Priority.MEDIUM
    time_requirement_hrs: Optional[float] = None
    motivation: Optional[str] = None
    status: GoalStatus = GoalStatus.ACTIVE
    target_date: Optional[date] = None
    parent_goal_id: Optional[uuid.UUID] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    timeframe: Optional[GoalTimeframe] = None
    priority: Optional[Priority] = None
    time_requirement_hrs: Optional[float] = None
    motivation: Optional[str] = None
    status: Optional[GoalStatus] = None
    target_date: Optional[date] = None
    parent_goal_id: Optional[uuid.UUID] = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: Optional[str]
    timeframe: GoalTimeframe
    priority: Priority
    time_requirement_hrs: Optional[float]
    motivation: Optional[str]
    status: GoalStatus
    target_date: Optional[date]
    parent_goal_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
