from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import List

from app.db.database import get_session
from app.models.activity import Activity
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.footprint import Insight
from app.services.recommendation_engine import get_footprint_summary, generate_insights

router = APIRouter()

@router.get("", response_model=List[Insight])
def read_insights(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    # Fetch recent activities (e.g., last 7 days)
    now = datetime.utcnow()
    start_date = now - timedelta(days=7)
    
    query = select(Activity).where(
        Activity.user_id == current_user.id,
        Activity.activity_date >= start_date
    )
    recent_activities = session.exec(query).all()
    
    footprint_summary = get_footprint_summary(recent_activities)
    insights = generate_insights(current_user, recent_activities, footprint_summary)
    
    return insights
