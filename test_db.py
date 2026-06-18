from sqlmodel import Session, select
from app.db.database import engine
from app.models.activity import Activity

with Session(engine) as session:
    activities = session.exec(select(Activity)).all()
    for a in activities:
        print(a.id, a.category, a.activity_date, a.co2e_kg)
