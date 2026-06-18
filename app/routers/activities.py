from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.db.database import get_session
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityRead
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.emission_calculator import calculate_co2e
from app.models.emission_factor import EmissionFactor

router = APIRouter()

@router.post("", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
def log_activity(activity_in: ActivityCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        co2e_kg = calculate_co2e(
            session,
            activity_in.category,
            activity_in.subtype,
            activity_in.quantity,
            activity_in.unit,
            current_user.region
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    activity = Activity(
        user_id=current_user.id,
        category=activity_in.category,
        subtype=activity_in.subtype,
        quantity=activity_in.quantity,
        unit=activity_in.unit,
        activity_date=activity_in.activity_date,
        co2e_kg=co2e_kg,
        notes=activity_in.notes
    )
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity

@router.get("", response_model=List[ActivityRead])
def list_activities(
    from_date: datetime = None, 
    to_date: datetime = None, 
    category: str = None, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    query = select(Activity).where(Activity.user_id == current_user.id)
    if from_date:
        query = query.where(Activity.activity_date >= from_date)
    if to_date:
        query = query.where(Activity.activity_date <= to_date)
    if category:
        query = query.where(Activity.category == category)
        
    query = query.order_by(Activity.activity_date.desc())
    activities = session.exec(query).all()
    return activities

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    activity = session.get(Activity, activity_id)
    if not activity or activity.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Activity not found")
        
    session.delete(activity)
    session.commit()
