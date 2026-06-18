from typing import List
from app.models.user import User
from app.models.activity import Activity
from app.schemas.footprint import FootprintSummary, Insight

def get_footprint_summary(activities: List[Activity], eco_points: int = 0) -> FootprintSummary:
    total = sum(a.co2e_kg for a in activities)
    breakdown = {}
    for a in activities:
        breakdown[a.category] = breakdown.get(a.category, 0.0) + a.co2e_kg
    return FootprintSummary(total_co2e_kg=total, category_breakdown=breakdown, eco_points=eco_points)

def sort_by_contribution_desc(breakdown: dict) -> List[str]:
    return sorted(breakdown.keys(), key=lambda k: breakdown[k], reverse=True)

def generate_insights(user: User, recent_activities: List[Activity], footprint_summary: FootprintSummary) -> List[Insight]:
    breakdown = footprint_summary.category_breakdown
    insights = []
    
    # Analyze transport
    solo_car_km = sum(a.quantity for a in recent_activities if a.category == "Transport" and a.subtype in ["Car, petrol (avg)", "Car, diesel (avg)"])
    flight_km = sum(a.quantity for a in recent_activities if a.category == "Transport" and "flight" in a.subtype.lower())
    bus_carpool_count = sum(1 for a in recent_activities if a.category == "Transport" and a.subtype == "Bus")
    short_car_trips = sum(1 for a in recent_activities if a.category == "Transport" and "Car" in a.subtype and a.quantity < 3)
    bike_walk_short_trips = sum(1 for a in recent_activities if a.category == "Transport" and a.subtype == "Bicycle/Walk" and a.quantity < 3)
    
    # Analyze energy
    energy_activities = [a for a in recent_activities if a.category == "Energy"]
    
    # Analyze waste
    recycled = sum(a.quantity for a in recent_activities if a.category == "Waste" and a.subtype == "Recycled")
    landfill = sum(a.quantity for a in recent_activities if a.category == "Waste" and a.subtype == "Landfill")
    recycled_ratio = recycled / (recycled + landfill) if (recycled + landfill) > 0 else 0
    
    categories_desc = sort_by_contribution_desc(breakdown)
    
    for category in categories_desc:
        if category == "Transport":
            if flight_km > 1000:
                insights.append(Insight(
                    category="Transport",
                    trigger="High flight usage",
                    recommendation="Flights are highly carbon intensive. Consider trains for regional travel or carbon offsetting.",
                    insight_key="transport_flights"
                ))
            elif solo_car_km > 50 and category == categories_desc[0]:
                if not (solo_car_km < 10 or bus_carpool_count >= 2):
                    insights.append(Insight(
                        category="Transport",
                        trigger="High solo driving",
                        recommendation="Suggest carpool/transit for ≥1 trip/week.",
                        estimated_savings_kg=10.0,
                        insight_key="transport_carpool"
                    ))
            
            if short_car_trips > 0 and bike_walk_short_trips == 0:
                insights.append(Insight(
                    category="Transport",
                    trigger="Short car trips",
                    recommendation="Suggest walking/cycling for short trips.",
                    estimated_savings_kg=2.0,
                    insight_key="transport_short_trips"
                ))
                
        elif category == "Energy":
            if category == categories_desc[0] and len(energy_activities) == 0:
                insights.append(Insight(
                    category="Energy",
                    trigger="High energy baseline",
                    recommendation="Suggest LED/off-peak/unplug-idle tips.",
                    insight_key="energy_efficiency"
                ))
                
        elif category == "Food":
            meat_meals = sum(a.quantity for a in recent_activities if a.category == "Food" and a.subtype in ["Omnivore (avg) diet", "High-meat diet"])
            veg_meals = sum(a.quantity for a in recent_activities if a.category == "Food" and a.subtype in ["Vegetarian diet", "Vegan diet"])
            
            if (meat_meals > 0 or (user.diet_baseline in ["omnivore", "high_meat"] and veg_meals == 0)):
                insights.append(Insight(
                    category="Food",
                    trigger="High meat diet",
                    recommendation="Suggest 1–2 meat-free days/week.",
                    estimated_savings_kg=5.0,
                    insight_key="food_meat_free"
                ))
            elif veg_meals > 0 and meat_meals == 0:
                insights.append(Insight(
                    category="Food",
                    trigger="Plant-based diet",
                    recommendation="Fantastic job sticking to a plant-based diet! You are saving a huge amount of carbon.",
                    insight_key="food_veg_congrats"
                ))
                
        elif category == "Waste":
            if recycled_ratio < 0.30 and (recycled + landfill) > 0:
                insights.append(Insight(
                    category="Waste",
                    trigger="Low recycling",
                    recommendation="Suggest segregating recyclables.",
                    insight_key="waste_recycle"
                ))
            elif recycled_ratio > 0.70:
                insights.append(Insight(
                    category="Waste",
                    trigger="High recycling",
                    recommendation="Great job recycling! You are keeping waste out of landfills.",
                    insight_key="waste_recycle_congrats"
                ))
                
        if len(insights) >= 3:
            break
            
    # Universal fallbacks
    if len(insights) == 0:
        if footprint_summary.total_co2e_kg > 200:
            insights.append(Insight(
                category="Any",
                trigger="High overall emissions",
                recommendation="Your emissions are running high. Explore carbon offset programs to neutralize your footprint.",
                insight_key="any_high_emissions"
            ))
        else:
            insights.append(Insight(
                category="Any",
                trigger="Consistent tracking",
                recommendation="You're doing great! Keep logging your daily activities to find more ways to reduce.",
                insight_key="any_keep_tracking"
            ))
            
    if len(insights) < 3 and "Transport" not in breakdown and footprint_summary.total_co2e_kg > 0:
        insights.append(Insight(
            category="Any",
            trigger="No transport logged",
            recommendation="Zero transport emissions! Walking/biking is great for you and the planet.",
            insight_key="any_congratulate"
        ))
        
    return insights[:3]
