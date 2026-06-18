from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.db.database import get_session
from app.models.activity import Activity
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.footprint import FootprintSummary
from app.services.recommendation_engine import get_footprint_summary

router = APIRouter()

@router.get("/summary", response_model=FootprintSummary)
def read_footprint_summary(
    period: str = "week", 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    query = select(Activity).where(Activity.user_id == current_user.id)
    now = datetime.utcnow()
    
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = None
        
    if start_date:
        query = query.where(Activity.activity_date >= start_date)
        
    activities = session.exec(query).all()
    
    from sqlmodel import func
    total_activities = session.exec(select(func.count(Activity.id)).where(Activity.user_id == current_user.id)).one()
    eco_points = total_activities * 10
    
    return get_footprint_summary(activities, eco_points)
