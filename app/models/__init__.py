# Import all models in dependency order for Alembic autogenerate discovery.
# Base must be imported first, then shared enums, then models in FK-dependency order.

from app.models.base import Base, TimestampMixin  # noqa: F401
from app.models.enums import Priority  # noqa: F401

# Goal has no FK dependencies on other domain models
from app.models.goal import Goal, GoalStatus, GoalTimeframe  # noqa: F401

# Task depends on Goal
from app.models.task import (  # noqa: F401
    Frequency,
    InstanceStatus,
    Task,
    TaskFeedback,
    TaskInstance,
    TaskType,
)

# Habit depends on Goal
from app.models.habit import Habit, HabitFrequency, HabitLog, HabitStatus  # noqa: F401

# Plan depends on TaskInstance and Habit
from app.models.plan import ItemStatus, Plan, PlanItem, PlanStatus  # noqa: F401
