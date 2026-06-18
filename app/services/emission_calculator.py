from sqlmodel import Session, select
from app.models.emission_factor import EmissionFactor

def lookup_emission_factor(session: Session, category: str, subtype: str, region: str = None) -> EmissionFactor:
    query = select(EmissionFactor).where(
        EmissionFactor.category == category,
        EmissionFactor.subtype == subtype
    )
    results = session.exec(query).all()
    
    if not results:
        raise ValueError(f"Emission factor not found for {category} / {subtype}")
        
    # Prefer region match, fallback to global default
    if region:
        for r in results:
            if r.region == region:
                return r
    
    for r in results:
        if r.region is None:
            return r
            
    return results[0] # Fallback to first if somehow no global default

def calculate_co2e(session: Session, category: str, subtype: str, quantity: float, unit: str, region: str = None) -> float:
    factor = lookup_emission_factor(session, category, subtype, region)
    
    # Normally we'd check if units match, but for MVP we assume UI enforces correct units.
    return round(quantity * factor.factor_value, 3)
