import pytest
from datetime import datetime
from app.models.user import User
from app.models.activity import Activity
from app.schemas.footprint import FootprintSummary
from app.services.recommendation_engine import get_footprint_summary, generate_insights

def test_get_footprint_summary():
    activities = [
        Activity(id=1, user_id=1, category="Transport", subtype="Car", quantity=10, unit="km", activity_date=datetime.utcnow(), co2e_kg=2.0),
        Activity(id=2, user_id=1, category="Transport", subtype="Bus", quantity=5, unit="km", activity_date=datetime.utcnow(), co2e_kg=0.5),
        Activity(id=3, user_id=1, category="Energy", subtype="Electricity", quantity=10, unit="kWh", activity_date=datetime.utcnow(), co2e_kg=7.1),
    ]
    summary = get_footprint_summary(activities)
    assert summary.total_co2e_kg == 9.6
    assert summary.category_breakdown["Transport"] == 2.5
    assert summary.category_breakdown["Energy"] == 7.1

def test_generate_insights_transport_carpool():
    user = User(id=1, email="test@example.com", hashed_password="123", diet_baseline="omnivore")
    activities = [
        # Top contributor transport, > 50 km solo car
        Activity(id=1, user_id=1, category="Transport", subtype="Car, petrol (avg)", quantity=60, unit="km", activity_date=datetime.utcnow(), co2e_kg=10.2)
    ]
    summary = get_footprint_summary(activities)
    insights = generate_insights(user, activities, summary)
    
    assert len(insights) >= 1
    assert any(i.insight_key == "transport_carpool" for i in insights)

def test_generate_insights_transport_carpool_skip_bus():
    user = User(id=1, email="test@example.com", hashed_password="123", diet_baseline="omnivore")
    activities = [
        # Top contributor transport, > 50 km solo car, but already taking bus twice
        Activity(id=1, user_id=1, category="Transport", subtype="Car, petrol (avg)", quantity=60, unit="km", activity_date=datetime.utcnow(), co2e_kg=10.2),
        Activity(id=2, user_id=1, category="Transport", subtype="Bus", quantity=5, unit="km", activity_date=datetime.utcnow(), co2e_kg=0.5),
        Activity(id=3, user_id=1, category="Transport", subtype="Bus", quantity=5, unit="km", activity_date=datetime.utcnow(), co2e_kg=0.5),
    ]
    summary = get_footprint_summary(activities)
    insights = generate_insights(user, activities, summary)
    
    # Should skip transport_carpool
    assert not any(i.insight_key == "transport_carpool" for i in insights)

def test_generate_insights_food_meat_free():
    user = User(id=1, email="test@example.com", hashed_password="123", diet_baseline="high_meat")
    activities = [
        Activity(id=1, user_id=1, category="Food", subtype="High-meat diet", quantity=1, unit="day", activity_date=datetime.utcnow(), co2e_kg=3.3)
    ]
    summary = get_footprint_summary(activities)
    insights = generate_insights(user, activities, summary)
    
    assert any(i.insight_key == "food_meat_free" for i in insights)

def test_generate_insights_food_meat_free_skip_vegan():
    user = User(id=1, email="test@example.com", hashed_password="123", diet_baseline="vegan") # Vegan doesn't trigger
    activities = [
        Activity(id=1, user_id=1, category="Food", subtype="Vegan diet", quantity=1, unit="day", activity_date=datetime.utcnow(), co2e_kg=1.5)
    ]
    summary = get_footprint_summary(activities)
    insights = generate_insights(user, activities, summary)
    
    assert not any(i.insight_key == "food_meat_free" for i in insights)
    
def test_generate_insights_congratulate():
    user = User(id=1, email="test@example.com", hashed_password="123", diet_baseline="vegan")
    # No activities logged!
    summary = get_footprint_summary([])
    insights = generate_insights(user, [], summary)
    
    assert any(i.insight_key == "any_congratulate" for i in insights)
