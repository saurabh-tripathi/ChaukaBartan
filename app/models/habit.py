import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import Priority

if TYPE_CHECKING:
    from app.models.goal import Goal
    from app.models.plan import PlanItem


class HabitFrequency(enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class HabitStatus(enum.Enum):
    TODO = "TODO"
    ACTIVE = "ACTIVE"
    SET = "SET"
    LAPSED = "LAPSED"
    ABANDONED = "ABANDONED"


class Habit(TimestampMixin, Base):
    __tablename__ = "habits"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    frequency: Mapped[HabitFrequency] = mapped_column(
        Enum(HabitFrequency, name="habit_frequency", native_enum=True),
        nullable=False,
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="priority", native_enum=True),
        nullable=False,
        default=Priority.MEDIUM,
    )
    importance_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[HabitStatus] = mapped_column(
        Enum(HabitStatus, name="habit_status", native_enum=True),
        nullable=False,
        default=HabitStatus.ACTIVE,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    set_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    streak_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expected_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, server_default="{}")

    goal: Mapped[Optional["Goal"]] = relationship(
        "Goal",
        back_populates="habits",
    )
    logs: Mapped[list["HabitLog"]] = relationship(
        "HabitLog",
        back_populates="habit",
        cascade="all, delete-orphan",
    )
    plan_items: Mapped[list["PlanItem"]] = relationship(
        "PlanItem",
        back_populates="habit",
    )


class HabitLog(TimestampMixin, Base):
    __tablename__ = "habit_logs"

    habit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False,
    )
    logged_date: Mapped[date] = mapped_column(Date, nullable=False)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    habit: Mapped["Habit"] = relationship(
        "Habit",
        back_populates="logs",
    )
