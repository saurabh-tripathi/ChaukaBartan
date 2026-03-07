from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.goal import GoalResponse


# ── Daily dashboard ───────────────────────────────────────────────────────────

class DailyPlanStats(BaseModel):
    total_items: int
    completed: int
    skipped: int
    pending: int
    completion_rate: float


class DailyTaskStats(BaseModel):
    total_instances: int
    completed: int
    skipped: int
    pending: int
    in_progress: int
    completion_rate: float
    avg_difficulty: Optional[float]
    avg_satisfaction: Optional[float]
    total_duration_minutes: int


class DailyHabitStats(BaseModel):
    logged: int


class DailyDashboard(BaseModel):
    date: date
    plan: Optional[DailyPlanStats]   # None if no plan exists for this date
    tasks: DailyTaskStats
    habits: DailyHabitStats


# ── History report (background job) ──────────────────────────────────────────

class HistoryReportRequest(BaseModel):
    from_date: date
    to_date: date


class DailyBreakdown(BaseModel):
    date: date
    tasks_total: int
    tasks_completed: int
    habits_logged: int
    plan_completion_rate: Optional[float]   # None if no plan that day


class HistoryReport(BaseModel):
    from_date: date
    to_date: date
    total_task_instances: int
    tasks_completed: int
    task_completion_rate: float
    total_habit_logs: int
    avg_difficulty: Optional[float]
    avg_satisfaction: Optional[float]
    total_duration_minutes: int
    daily_breakdown: list[DailyBreakdown]


class ReportStatus(BaseModel):
    job_id: str
    status: str                     # pending | running | done | error
    result: Optional[HistoryReport]
    error: Optional[str]


# ── Goal progress ─────────────────────────────────────────────────────────────

class GoalTaskProgress(BaseModel):
    total_tasks: int
    active_tasks: int
    completed_instances_last_30d: int


class GoalHabitProgress(BaseModel):
    total_habits: int
    active_habits: int
    avg_streak: float
    logs_last_30d: int


class GoalProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    goal: GoalResponse
    tasks: GoalTaskProgress
    habits: GoalHabitProgress
