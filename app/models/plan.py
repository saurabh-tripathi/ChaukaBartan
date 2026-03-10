import enum
import uuid
from datetime import date, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.habit import Habit
    from app.models.task import TaskInstance


class PlanStatus(enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class ItemStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class Plan(TimestampMixin, Base):
    __tablename__ = "plans"

    __table_args__ = (UniqueConstraint("plan_date", name="uq_plan_date"),)

    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[PlanStatus] = mapped_column(
        Enum(PlanStatus, name="plan_status", native_enum=True),
        nullable=False,
        default=PlanStatus.DRAFT,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[list["PlanItem"]] = relationship(
        "PlanItem",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="PlanItem.display_order",
    )


class PlanItem(TimestampMixin, Base):
    __tablename__ = "plan_items"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_instance_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    habit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("habits.id", ondelete="SET NULL"),
        nullable=True,
    )
    scheduled_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus, name="item_status", native_enum=True),
        nullable=False,
        default=ItemStatus.PENDING,
    )

    plan: Mapped["Plan"] = relationship(
        "Plan",
        back_populates="items",
    )
    task_instance: Mapped[Optional["TaskInstance"]] = relationship(
        "TaskInstance",
        back_populates="plan_items",
    )
    habit: Mapped[Optional["Habit"]] = relationship(
        "Habit",
        back_populates="plan_items",
    )
