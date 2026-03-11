import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import Priority

if TYPE_CHECKING:
    from app.models.goal import Goal
    from app.models.plan import PlanItem


class TaskType(enum.Enum):
    CHORE = "CHORE"
    IMPROVEMENT = "IMPROVEMENT"


class Frequency(enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    HALF_YEARLY = "HALF_YEARLY"
    YEARLY = "YEARLY"
    ONE_TIME = "ONE_TIME"
    AD_HOC = "AD_HOC"


class InstanceStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_type: Mapped[TaskType] = mapped_column(
        Enum(TaskType, name="task_type", native_enum=True),
        nullable=False,
    )
    frequency: Mapped[Frequency] = mapped_column(
        Enum(Frequency, name="frequency", native_enum=True),
        nullable=False,
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="priority", native_enum=True),
        nullable=False,
        default=Priority.MEDIUM,
    )
    importance_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expected_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, server_default="{}")

    parent_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Self-referential relationships
    parent: Mapped[Optional["Task"]] = relationship(
        "Task",
        back_populates="children",
        remote_side="Task.id",
        foreign_keys=[parent_task_id],
    )
    children: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="parent",
        foreign_keys=[parent_task_id],
        cascade="all, delete-orphan",
    )

    goal: Mapped[Optional["Goal"]] = relationship(
        "Goal",
        back_populates="tasks",
    )
    instances: Mapped[list["TaskInstance"]] = relationship(
        "TaskInstance",
        back_populates="task",
        cascade="all, delete-orphan",
    )


class TaskInstance(TimestampMixin, Base):
    __tablename__ = "task_instances"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[InstanceStatus] = mapped_column(
        Enum(InstanceStatus, name="instance_status", native_enum=True),
        nullable=False,
        default=InstanceStatus.PENDING,
    )

    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="instances",
    )
    feedback: Mapped[Optional["TaskFeedback"]] = relationship(
        "TaskFeedback",
        back_populates="task_instance",
        uselist=False,
        cascade="all, delete-orphan",
    )
    plan_items: Mapped[list["PlanItem"]] = relationship(
        "PlanItem",
        back_populates="task_instance",
    )


class TaskFeedback(TimestampMixin, Base):
    __tablename__ = "task_feedbacks"

    __table_args__ = (
        CheckConstraint("difficulty_rating >= 1 AND difficulty_rating <= 5", name="ck_difficulty_rating"),
        CheckConstraint("satisfaction_rating >= 1 AND satisfaction_rating <= 5", name="ck_satisfaction_rating"),
    )

    task_instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_instances.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    satisfaction_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    task_instance: Mapped["TaskInstance"] = relationship(
        "TaskInstance",
        back_populates="feedback",
    )
