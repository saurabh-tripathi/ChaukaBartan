"""
Plan builder — core business logic for generating a daily plan.

Rules:
  Tasks
  -----
  - DAILY      → always included if is_active and not past end_date
  - ONE_TIME   → included if no TaskInstance exists yet
  - AD_HOC     → never auto-included
  - WEEKLY / MONTHLY / QUARTERLY / HALF_YEARLY / YEARLY
               → included if no TaskInstance exists, or last instance is ≥ N days ago

  Habits
  ------
  - ACTIVE / SET status only
  - DAILY      → always included
  - WEEKLY     → included only if no HabitLog in the 7-day window ending on plan_date

  Ordering
  --------
  All candidates are sorted by priority (CRITICAL first) then by title.
  display_order is assigned based on this sorted position.
"""

from datetime import date, timedelta
from typing import Optional, Union

from sqlalchemy.orm import Session

from app.models.enums import Priority
from app.models.habit import Habit, HabitFrequency, HabitLog, HabitStatus
from app.models.plan import Plan, PlanItem
from app.models.task import Frequency, Task, TaskInstance

_PRIORITY_RANK: dict[Priority, int] = {
    Priority.CRITICAL: 0,
    Priority.HIGH: 1,
    Priority.MEDIUM: 2,
    Priority.LOW: 3,
}

_FREQUENCY_DAYS: dict[Frequency, int] = {
    Frequency.WEEKLY: 7,
    Frequency.MONTHLY: 28,
    Frequency.QUARTERLY: 90,
    Frequency.HALF_YEARLY: 180,
    Frequency.YEARLY: 365,
}


def _task_is_due(task: Task, plan_date: date, db: Session) -> bool:
    if task.end_date and plan_date > task.end_date:
        return False
    if task.frequency == Frequency.DAILY:
        return True
    if task.frequency == Frequency.AD_HOC:
        return False
    if task.frequency == Frequency.ONE_TIME:
        return not db.query(TaskInstance).filter(TaskInstance.task_id == task.id).first()

    threshold = _FREQUENCY_DAYS[task.frequency]
    last = (
        db.query(TaskInstance)
        .filter(TaskInstance.task_id == task.id)
        .order_by(TaskInstance.scheduled_date.desc())
        .first()
    )
    return last is None or (plan_date - last.scheduled_date).days >= threshold


def _habit_is_due(habit: Habit, plan_date: date, db: Session) -> bool:
    if habit.frequency == HabitFrequency.DAILY:
        return True
    # WEEKLY: include only if no log exists in the 7-day window ending on plan_date
    week_start = plan_date - timedelta(days=6)
    logged = (
        db.query(HabitLog)
        .filter(
            HabitLog.habit_id == habit.id,
            HabitLog.logged_date >= week_start,
            HabitLog.logged_date <= plan_date,
        )
        .first()
    )
    return logged is None


def generate_plan(db: Session, plan_date: date, notes: Optional[str] = None) -> Plan:
    """
    Generate and persist a Plan for plan_date.
    Raises ValueError if a plan already exists for that date.
    """
    existing = db.query(Plan).filter(Plan.plan_date == plan_date).first()
    if existing:
        raise ValueError(f"A plan already exists for {plan_date}")

    plan = Plan(plan_date=plan_date, notes=notes)
    db.add(plan)
    db.flush()  # assigns plan.id before creating items

    # Collect (priority_rank, title, type, model) tuples
    candidates: list[tuple[int, str, str, Union[Task, Habit]]] = []

    for task in db.query(Task).filter(Task.is_active == True).all():
        if _task_is_due(task, plan_date, db):
            candidates.append((_PRIORITY_RANK[task.priority], task.title, "task", task))

    for habit in (
        db.query(Habit)
        .filter(Habit.status.in_([HabitStatus.ACTIVE, HabitStatus.SET]))
        .all()
    ):
        if _habit_is_due(habit, plan_date, db):
            candidates.append((_PRIORITY_RANK[habit.priority], habit.title, "habit", habit))

    candidates.sort(key=lambda c: (c[0], c[1]))

    for order, (_, _, item_type, item) in enumerate(candidates):
        if item_type == "task":
            # Reuse an existing instance for this date if one already exists
            instance = (
                db.query(TaskInstance)
                .filter(
                    TaskInstance.task_id == item.id,
                    TaskInstance.scheduled_date == plan_date,
                )
                .first()
            )
            if not instance:
                instance = TaskInstance(task_id=item.id, scheduled_date=plan_date)
                db.add(instance)
                db.flush()
            db.add(PlanItem(plan_id=plan.id, task_instance_id=instance.id, display_order=order))
        else:
            db.add(PlanItem(plan_id=plan.id, habit_id=item.id, display_order=order))

    db.commit()
    return plan.id  # return ID so caller can re-query with eager loading
