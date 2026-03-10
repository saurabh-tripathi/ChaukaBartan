import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import Priority

if TYPE_CHECKING:
    from app.models.habit import Habit
    from app.models.task import Task


class GoalTimeframe(enum.Enum):
    THREE_MONTHS = "THREE_MONTHS"
    SIX_MONTHS = "SIX_MONTHS"
    ONE_YEAR = "ONE_YEAR"
    FIVE_YEARS = "FIVE_YEARS"


class GoalStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    PAUSED = "PAUSED"


class Goal(TimestampMixin, Base):
    __tablename__ = "goals"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timeframe: Mapped[GoalTimeframe] = mapped_column(
        Enum(GoalTimeframe, name="goal_timeframe", native_enum=True),
        nullable=False,
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="priority", native_enum=True),
        nullable=False,
        default=Priority.MEDIUM,
    )
    time_requirement_hrs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    motivation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus, name="goal_status", native_enum=True),
        nullable=False,
        default=GoalStatus.ACTIVE,
    )
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    parent_goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Self-referential relationships
    parent: Mapped[Optional["Goal"]] = relationship(
        "Goal",
        back_populates="children",
        remote_side="Goal.id",
        foreign_keys=[parent_goal_id],
    )
    children: Mapped[list["Goal"]] = relationship(
        "Goal",
        back_populates="parent",
        foreign_keys=[parent_goal_id],
        cascade="all, delete-orphan",
    )

    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="goal",
        cascade="all, delete-orphan",
    )
    habits: Mapped[list["Habit"]] = relationship(
        "Habit",
        back_populates="goal",
        cascade="all, delete-orphan",
    )
