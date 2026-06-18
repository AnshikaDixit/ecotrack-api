from sqlmodel import Session, select
from app.models.emission_factor import EmissionFactor
from app.db.database import engine

factors = [
    {"category": "Transport", "subtype": "Car, petrol (avg)", "unit": "km", "factor_value": 0.17, "source_note": "solo driver"},
    {"category": "Transport", "subtype": "Car, diesel (avg)", "unit": "km", "factor_value": 0.18, "source_note": "solo driver"},
    {"category": "Transport", "subtype": "Two-wheeler", "unit": "km", "factor_value": 0.08, "source_note": "common in India"},
    {"category": "Transport", "subtype": "Bus", "unit": "km", "factor_value": 0.10, "source_note": "per passenger-km"},
    {"category": "Transport", "subtype": "Train/Metro", "unit": "km", "factor_value": 0.04, "source_note": "per passenger-km"},
    {"category": "Transport", "subtype": "Domestic flight", "unit": "km", "factor_value": 0.15, "source_note": "per passenger-km"},
    {"category": "Transport", "subtype": "Bicycle/Walk", "unit": "km", "factor_value": 0.0, "source_note": ""},
    {"category": "Energy", "subtype": "Electricity (India grid, default)", "unit": "kWh", "factor_value": 0.71, "source_note": "adjust per state if known"},
    {"category": "Energy", "subtype": "LPG cooking gas", "unit": "kg", "factor_value": 2.98, "source_note": ""},
    {"category": "Food", "subtype": "Vegan diet", "unit": "day", "factor_value": 1.5, "source_note": ""},
    {"category": "Food", "subtype": "Vegetarian diet", "unit": "day", "factor_value": 1.7, "source_note": ""},
    {"category": "Food", "subtype": "Omnivore (avg) diet", "unit": "day", "factor_value": 2.5, "source_note": ""},
    {"category": "Food", "subtype": "High-meat diet", "unit": "day", "factor_value": 3.3, "source_note": ""},
    {"category": "Waste", "subtype": "Landfill", "unit": "kg", "factor_value": 0.5, "source_note": ""},
    {"category": "Waste", "subtype": "Recycled", "unit": "kg", "factor_value": 0.1, "source_note": ""},
]

def seed_factors():
    with Session(engine) as session:
        for f in factors:
            existing = session.exec(select(EmissionFactor).where(
                EmissionFactor.category == f["category"],
                EmissionFactor.subtype == f["subtype"]
            )).first()
            if not existing:
                factor = EmissionFactor(**f)
                session.add(factor)
        session.commit()
