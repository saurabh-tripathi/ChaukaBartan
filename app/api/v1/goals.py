import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.enums import Priority
from app.models.goal import Goal, GoalStatus, GoalTimeframe
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[GoalResponse])
def list_goals(
    status: Optional[GoalStatus] = Query(None),
    timeframe: Optional[GoalTimeframe] = Query(None),
    priority: Optional[Priority] = Query(None),
    parent_goal_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Goal)
    if status is not None:
        q = q.filter(Goal.status == status)
    if timeframe is not None:
        q = q.filter(Goal.timeframe == timeframe)
    if priority is not None:
        q = q.filter(Goal.priority == priority)
    if parent_goal_id is not None:
        q = q.filter(Goal.parent_goal_id == parent_goal_id)
    return q.order_by(Goal.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(body: GoalCreate, db: Session = Depends(get_db)):
    if body.parent_goal_id:
        parent = db.get(Goal, body.parent_goal_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent goal not found")
    goal = Goal(**body.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: uuid.UUID, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: uuid.UUID, body: GoalUpdate, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if body.parent_goal_id is not None:
        if body.parent_goal_id == goal_id:
            raise HTTPException(status_code=400, detail="Goal cannot be its own parent")
        parent = db.get(Goal, body.parent_goal_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent goal not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: uuid.UUID, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
