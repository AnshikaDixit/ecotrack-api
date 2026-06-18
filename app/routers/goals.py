from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db.database import get_session
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate
from app.routers.auth import get_current_user

router = APIRouter()

from app.models.activity import Activity

@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(goal_in: GoalCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    goal = Goal(
        user_id=current_user.id,
        title=goal_in.title,
        target_reduction_percent=goal_in.target_reduction_percent,  
        baseline_co2e_kg=goal_in.baseline_co2e_kg,
        period_start=goal_in.period_start,
        period_end=goal_in.period_end
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    
    # Newly created goal has 0 current_co2e_kg (or calculate if backdated)
    activities = session.exec(select(Activity).where(
        Activity.user_id == current_user.id,
        Activity.activity_date >= goal.period_start,
        Activity.activity_date <= goal.period_end
    )).all()
    
    current_co2e = sum(a.co2e_kg for a in activities)
    
    return {**goal.model_dump(), "current_co2e_kg": current_co2e}

@router.get("", response_model=List[GoalRead])
def list_goals(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    goals = session.exec(select(Goal).where(Goal.user_id == current_user.id)).all()
    
    results = []
    for goal in goals:
        activities = session.exec(select(Activity).where(
            Activity.user_id == current_user.id,
            Activity.activity_date >= goal.period_start,
            Activity.activity_date <= goal.period_end
        )).all()
        current_co2e = sum(a.co2e_kg for a in activities)
        results.append({**goal.model_dump(), "current_co2e_kg": current_co2e})
        
    return results

@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(goal_id: int, goal_update: GoalUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    if goal_update.title is not None:
        goal.title = goal_update.title
    if goal_update.status is not None:
        goal.status = goal_update.status
        
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal
