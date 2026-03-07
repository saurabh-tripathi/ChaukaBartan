"""
Dashboard API.

Endpoints
---------
GET  /dashboard/daily              – single-day stats (sync, fast)
GET  /dashboard/goals/{goal_id}    – goal progress over last 30 days (sync, fast)
POST /dashboard/history/report     – kick off a background history report
GET  /dashboard/history/report/{job_id} – poll for report result
"""

import uuid
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.models.enums import Priority
from app.models.goal import Goal
from app.models.habit import Habit, HabitLog, HabitStatus
from app.models.plan import ItemStatus, Plan, PlanItem
from app.models.task import Frequency, InstanceStatus, Task, TaskFeedback, TaskInstance
from app.schemas.dashboard import (
    DailyBreakdown,
    DailyDashboard,
    DailyHabitStats,
    DailyPlanStats,
    DailyTaskStats,
    GoalHabitProgress,
    GoalProgress,
    GoalTaskProgress,
    HistoryReport,
    HistoryReportRequest,
    ReportStatus,
)
from app.schemas.goal import GoalResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# ── In-memory job store (fine for single-instance; swap for Redis in prod) ────
_jobs: dict[str, dict] = {}


# ── Daily dashboard ───────────────────────────────────────────────────────────

@router.get("/daily", response_model=DailyDashboard)
def daily_dashboard(
    report_date: date = Query(default_factory=date.today, alias="date"),
    db: Session = Depends(get_db),
):
    # Plan stats
    plan_stats: Optional[DailyPlanStats] = None
    plan = db.query(Plan).filter(Plan.plan_date == report_date).first()
    if plan:
        rows = (
            db.query(PlanItem.status, func.count(PlanItem.id))
            .filter(PlanItem.plan_id == plan.id)
            .group_by(PlanItem.status)
            .all()
        )
        counts = {s: c for s, c in rows}
        total = sum(counts.values())
        completed = counts.get(ItemStatus.COMPLETED, 0)
        plan_stats = DailyPlanStats(
            total_items=total,
            completed=completed,
            skipped=counts.get(ItemStatus.SKIPPED, 0),
            pending=counts.get(ItemStatus.PENDING, 0),
            completion_rate=completed / total if total else 0.0,
        )

    # Task instance stats
    inst_rows = (
        db.query(TaskInstance.status, func.count(TaskInstance.id))
        .filter(TaskInstance.scheduled_date == report_date)
        .group_by(TaskInstance.status)
        .all()
    )
    inst_counts = {s: c for s, c in inst_rows}
    total_inst = sum(inst_counts.values())
    completed_inst = inst_counts.get(InstanceStatus.COMPLETED, 0)

    fb = (
        db.query(
            func.avg(TaskFeedback.difficulty_rating),
            func.avg(TaskFeedback.satisfaction_rating),
            func.coalesce(func.sum(TaskFeedback.duration_minutes), 0),
        )
        .join(TaskInstance, TaskFeedback.task_instance_id == TaskInstance.id)
        .filter(TaskInstance.scheduled_date == report_date)
        .first()
    )

    task_stats = DailyTaskStats(
        total_instances=total_inst,
        completed=completed_inst,
        skipped=inst_counts.get(InstanceStatus.SKIPPED, 0),
        pending=inst_counts.get(InstanceStatus.PENDING, 0),
        in_progress=inst_counts.get(InstanceStatus.IN_PROGRESS, 0),
        completion_rate=completed_inst / total_inst if total_inst else 0.0,
        avg_difficulty=float(fb[0]) if fb[0] is not None else None,
        avg_satisfaction=float(fb[1]) if fb[1] is not None else None,
        total_duration_minutes=int(fb[2]) if fb[2] else 0,
    )

    # Habit logs
    habit_log_count = (
        db.query(func.count(HabitLog.id))
        .filter(HabitLog.logged_date == report_date)
        .scalar()
    )

    return DailyDashboard(
        date=report_date,
        plan=plan_stats,
        tasks=task_stats,
        habits=DailyHabitStats(logged=habit_log_count or 0),
    )


# ── Goal progress ─────────────────────────────────────────────────────────────

@router.get("/goals/{goal_id}", response_model=GoalProgress)
def goal_progress(goal_id: uuid.UUID, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    cutoff = date.today() - timedelta(days=30)

    # Task counts
    task_agg = (
        db.query(
            func.count(Task.id),
            func.coalesce(
                func.sum(case((Task.is_active == True, 1), else_=0)), 0
            ),
        )
        .filter(Task.goal_id == goal_id)
        .first()
    )
    total_tasks = int(task_agg[0] or 0)
    active_tasks = int(task_agg[1] or 0)

    completed_30d = (
        db.query(func.count(TaskInstance.id))
        .join(Task, TaskInstance.task_id == Task.id)
        .filter(
            Task.goal_id == goal_id,
            TaskInstance.status == InstanceStatus.COMPLETED,
            TaskInstance.scheduled_date >= cutoff,
        )
        .scalar()
    )

    # Habit counts
    habit_agg = (
        db.query(
            func.count(Habit.id),
            func.coalesce(
                func.sum(case((Habit.status.in_([HabitStatus.ACTIVE, HabitStatus.SET]), 1), else_=0)), 0
            ),
            func.coalesce(func.avg(Habit.streak_count), 0.0),
        )
        .filter(Habit.goal_id == goal_id)
        .first()
    )
    total_habits = int(habit_agg[0] or 0)
    active_habits = int(habit_agg[1] or 0)
    avg_streak = float(habit_agg[2] or 0.0)

    logs_30d = (
        db.query(func.count(HabitLog.id))
        .join(Habit, HabitLog.habit_id == Habit.id)
        .filter(Habit.goal_id == goal_id, HabitLog.logged_date >= cutoff)
        .scalar()
    )

    return GoalProgress(
        goal=GoalResponse.model_validate(goal),
        tasks=GoalTaskProgress(
            total_tasks=total_tasks,
            active_tasks=active_tasks,
            completed_instances_last_30d=completed_30d or 0,
        ),
        habits=GoalHabitProgress(
            total_habits=total_habits,
            active_habits=active_habits,
            avg_streak=avg_streak,
            logs_last_30d=logs_30d or 0,
        ),
    )


# ── History report (background job) ──────────────────────────────────────────

def _run_history_report(job_id: str, from_date: date, to_date: date) -> None:
    """Runs in a background thread; creates its own DB session."""
    _jobs[job_id]["status"] = "running"
    db = SessionLocal()
    try:
        # Aggregate task instances
        agg = (
            db.query(
                func.count(TaskInstance.id),
                func.coalesce(
                    func.sum(case((TaskInstance.status == InstanceStatus.COMPLETED, 1), else_=0)), 0
                ),
                func.avg(TaskFeedback.difficulty_rating),
                func.avg(TaskFeedback.satisfaction_rating),
                func.coalesce(func.sum(TaskFeedback.duration_minutes), 0),
            )
            .outerjoin(TaskFeedback, TaskFeedback.task_instance_id == TaskInstance.id)
            .filter(TaskInstance.scheduled_date.between(from_date, to_date))
            .first()
        )
        total_inst = int(agg[0] or 0)
        completed_inst = int(agg[1] or 0)

        # Daily task breakdown
        daily_tasks = (
            db.query(
                TaskInstance.scheduled_date,
                func.count(TaskInstance.id).label("total"),
                func.coalesce(
                    func.sum(case((TaskInstance.status == InstanceStatus.COMPLETED, 1), else_=0)), 0
                ).label("completed"),
            )
            .filter(TaskInstance.scheduled_date.between(from_date, to_date))
            .group_by(TaskInstance.scheduled_date)
            .all()
        )

        # Daily habit logs
        daily_habits = (
            db.query(
                HabitLog.logged_date,
                func.count(HabitLog.id).label("count"),
            )
            .filter(HabitLog.logged_date.between(from_date, to_date))
            .group_by(HabitLog.logged_date)
            .all()
        )

        # Daily plan completion
        daily_plans = (
            db.query(
                Plan.plan_date,
                func.count(PlanItem.id).label("total"),
                func.coalesce(
                    func.sum(case((PlanItem.status == ItemStatus.COMPLETED, 1), else_=0)), 0
                ).label("completed"),
            )
            .join(PlanItem, PlanItem.plan_id == Plan.id)
            .filter(Plan.plan_date.between(from_date, to_date))
            .group_by(Plan.plan_date)
            .all()
        )

        tasks_by_date = {r.scheduled_date: (r.total, r.completed) for r in daily_tasks}
        habits_by_date = {r.logged_date: r.count for r in daily_habits}
        plans_by_date = {r.plan_date: (r.total, r.completed) for r in daily_plans}

        all_dates = sorted(
            set(list(tasks_by_date) + list(habits_by_date) + list(plans_by_date))
        )

        breakdown = []
        for d in all_dates:
            t_total, t_done = tasks_by_date.get(d, (0, 0))
            h_logged = habits_by_date.get(d, 0)
            p_total, p_done = plans_by_date.get(d, (0, 0))
            breakdown.append(
                DailyBreakdown(
                    date=d,
                    tasks_total=t_total,
                    tasks_completed=t_done,
                    habits_logged=h_logged,
                    plan_completion_rate=p_done / p_total if p_total else None,
                )
            )

        result = HistoryReport(
            from_date=from_date,
            to_date=to_date,
            total_task_instances=total_inst,
            tasks_completed=completed_inst,
            task_completion_rate=completed_inst / total_inst if total_inst else 0.0,
            total_habit_logs=sum(habits_by_date.values()),
            avg_difficulty=float(agg[2]) if agg[2] is not None else None,
            avg_satisfaction=float(agg[3]) if agg[3] is not None else None,
            total_duration_minutes=int(agg[4]) if agg[4] else 0,
            daily_breakdown=breakdown,
        )
        _jobs[job_id] = {"status": "done", "result": result, "error": None}
    except Exception as exc:
        _jobs[job_id] = {"status": "error", "result": None, "error": str(exc)}
    finally:
        db.close()


@router.post("/history/report", response_model=ReportStatus, status_code=202)
def start_history_report(
    body: HistoryReportRequest,
    background_tasks: BackgroundTasks,
):
    if body.from_date > body.to_date:
        raise HTTPException(status_code=400, detail="from_date must be ≤ to_date")
    if (body.to_date - body.from_date).days > 366:
        raise HTTPException(status_code=400, detail="Date range cannot exceed 366 days")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "result": None, "error": None}
    background_tasks.add_task(_run_history_report, job_id, body.from_date, body.to_date)

    return ReportStatus(job_id=job_id, status="pending", result=None, error=None)


@router.get("/history/report/{job_id}", response_model=ReportStatus)
def get_history_report(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Report job not found")
    return ReportStatus(job_id=job_id, **job)
