from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List

from app.db.database import get_session
from app.models.emission_factor import EmissionFactor

router = APIRouter()

@router.get("/emission-factors")
def get_emission_factors(session: Session = Depends(get_session)):
    return session.exec(select(EmissionFactor)).all()
