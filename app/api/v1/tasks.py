import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.enums import Priority
from app.models.goal import Goal
from app.models.task import Frequency, InstanceStatus, Task, TaskFeedback, TaskInstance, TaskType
from app.schemas.task import (
    FlatInstanceFeedbackSummary,
    FlatInstanceResponse,
    FlatInstanceTaskSummary,
    TaskCreate,
    TaskFeedbackCreate,
    TaskFeedbackResponse,
    TaskFeedbackUpdate,
    TaskInstanceCreate,
    TaskInstanceResponse,
    TaskInstanceUpdate,
    TaskResponse,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ── Task CRUD ────────────────────────────────────────────────────────────────

@router.get("", response_model=list[TaskResponse])
def list_tasks(
    is_active: Optional[bool] = Query(None),
    task_type: Optional[TaskType] = Query(None),
    frequency: Optional[Frequency] = Query(None),
    priority: Optional[Priority] = Query(None),
    goal_id: Optional[uuid.UUID] = Query(None),
    tags: list[str] = Query(default=[]),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Task)
    if is_active is not None:
        q = q.filter(Task.is_active == is_active)
    if task_type is not None:
        q = q.filter(Task.task_type == task_type)
    if frequency is not None:
        q = q.filter(Task.frequency == frequency)
    if priority is not None:
        q = q.filter(Task.priority == priority)
    if goal_id is not None:
        q = q.filter(Task.goal_id == goal_id)
    if tags:
        q = q.filter(Task.tags.overlap(tags))
    return q.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    if body.goal_id and not db.get(Goal, body.goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    if body.parent_task_id and not db.get(Task, body.parent_task_id):
        raise HTTPException(status_code=404, detail="Parent task not found")
    task = Task(**body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/instances", response_model=list[FlatInstanceResponse])
def list_all_instances(
    instance_status: InstanceStatus = Query(InstanceStatus.COMPLETED, alias="status"),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    goal_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = (
        db.query(TaskInstance)
        .join(TaskInstance.task)
        .options(
            joinedload(TaskInstance.task).joinedload(Task.goal),
            joinedload(TaskInstance.feedback),
        )
        .filter(TaskInstance.status == instance_status)
    )
    if from_date:
        q = q.filter(TaskInstance.scheduled_date >= from_date)
    if to_date:
        q = q.filter(TaskInstance.scheduled_date <= to_date)
    if goal_id:
        q = q.filter(Task.goal_id == goal_id)
    if search:
        q = q.filter(Task.title.ilike(f"%{search}%"))

    instances = q.order_by(TaskInstance.scheduled_date.desc()).offset(skip).limit(limit).all()

    results = []
    for inst in instances:
        task = inst.task
        goal_title = task.goal.title if task.goal else None
        task_summary = FlatInstanceTaskSummary(
            id=task.id,
            title=task.title,
            goal_id=task.goal_id,
            goal_title=goal_title,
            tags=task.tags or [],
            expected_duration_minutes=task.expected_duration_minutes,
        )
        feedback_summary = None
        if inst.feedback:
            feedback_summary = FlatInstanceFeedbackSummary(
                duration_minutes=inst.feedback.duration_minutes,
                difficulty_rating=inst.feedback.difficulty_rating,
                satisfaction_rating=inst.feedback.satisfaction_rating,
                notes=inst.feedback.notes,
            )
        results.append(FlatInstanceResponse(
            task_instance_id=inst.id,
            scheduled_date=inst.scheduled_date,
            status=inst.status,
            task=task_summary,
            feedback=feedback_summary,
        ))
    return results


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: uuid.UUID, body: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if body.goal_id is not None and not db.get(Goal, body.goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    if body.parent_task_id is not None:
        if body.parent_task_id == task_id:
            raise HTTPException(status_code=400, detail="Task cannot be its own parent")
        if not db.get(Task, body.parent_task_id):
            raise HTTPException(status_code=404, detail="Parent task not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


# ── Task Instances ────────────────────────────────────────────────────────────

@router.get("/{task_id}/instances", response_model=list[TaskInstanceResponse])
def list_instances(
    task_id: uuid.UUID,
    instance_status: Optional[InstanceStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    if not db.get(Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    q = db.query(TaskInstance).filter(TaskInstance.task_id == task_id)
    if instance_status is not None:
        q = q.filter(TaskInstance.status == instance_status)
    return q.order_by(TaskInstance.scheduled_date.desc()).offset(skip).limit(limit).all()


@router.post(
    "/{task_id}/instances",
    response_model=TaskInstanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_instance(task_id: uuid.UUID, body: TaskInstanceCreate, db: Session = Depends(get_db)):
    if not db.get(Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    instance = TaskInstance(task_id=task_id, **body.model_dump())
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@router.patch("/{task_id}/instances/{instance_id}", response_model=TaskInstanceResponse)
def update_instance(
    task_id: uuid.UUID,
    instance_id: uuid.UUID,
    body: TaskInstanceUpdate,
    db: Session = Depends(get_db),
):
    instance = db.get(TaskInstance, instance_id)
    if not instance or instance.task_id != task_id:
        raise HTTPException(status_code=404, detail="Task instance not found")
    instance.status = body.status
    db.commit()
    db.refresh(instance)
    return instance


# ── Task Feedback ─────────────────────────────────────────────────────────────

@router.get("/{task_id}/instances/{instance_id}/feedback", response_model=TaskFeedbackResponse)
def get_feedback(task_id: uuid.UUID, instance_id: uuid.UUID, db: Session = Depends(get_db)):
    instance = db.get(TaskInstance, instance_id)
    if not instance or instance.task_id != task_id:
        raise HTTPException(status_code=404, detail="Task instance not found")
    if not instance.feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return instance.feedback


@router.post(
    "/{task_id}/instances/{instance_id}/feedback",
    response_model=TaskFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback(
    task_id: uuid.UUID,
    instance_id: uuid.UUID,
    body: TaskFeedbackCreate,
    db: Session = Depends(get_db),
):
    instance = db.get(TaskInstance, instance_id)
    if not instance or instance.task_id != task_id:
        raise HTTPException(status_code=404, detail="Task instance not found")
    if instance.feedback:
        raise HTTPException(status_code=409, detail="Feedback already exists for this instance")
    feedback = TaskFeedback(task_instance_id=instance_id, **body.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.patch("/{task_id}/instances/{instance_id}/feedback", response_model=TaskFeedbackResponse)
def update_feedback(
    task_id: uuid.UUID,
    instance_id: uuid.UUID,
    body: TaskFeedbackUpdate,
    db: Session = Depends(get_db),
):
    instance = db.get(TaskInstance, instance_id)
    if not instance or instance.task_id != task_id:
        raise HTTPException(status_code=404, detail="Task instance not found")
    if not instance.feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(instance.feedback, field, value)
    db.commit()
    db.refresh(instance.feedback)
    return instance.feedback
