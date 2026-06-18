import pytest
from sqlmodel import Session, create_engine, SQLModel, pool
from app.db.seed_emission_factors import seed_factors
from app.services.emission_calculator import calculate_co2e, lookup_emission_factor
from app.models.emission_factor import EmissionFactor
from app.db.database import engine as db_engine

# We can use an in-memory db just for these tests to be fast and isolated
sqlite_url = "sqlite:///:memory:"
test_engine = create_engine(
    sqlite_url, 
    connect_args={"check_same_thread": False},
    poolclass=pool.StaticPool
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    # Monkey patch the engine in seed_emission_factors just for tests
    import app.db.seed_emission_factors as seeder
    original_engine = seeder.engine
    seeder.engine = test_engine
    seeder.seed_factors()
    
    with Session(test_engine) as session:
        yield session
        
    SQLModel.metadata.drop_all(test_engine)
    seeder.engine = original_engine

def test_lookup_emission_factor(session: Session):
    factor = lookup_emission_factor(session, "Transport", "Car, petrol (avg)")
    assert factor.factor_value == 0.17

def test_calculate_co2e(session: Session):
    co2e = calculate_co2e(session, "Transport", "Car, petrol (avg)", 100, "km")
    # 100 * 0.17 = 17.0
    assert co2e == 17.0

def test_calculate_co2e_regional_fallback(session: Session):
    # Insert a regional factor
    regional_factor = EmissionFactor(
        category="Transport",
        subtype="Car, petrol (avg)",
        region="UK",
        factor_value=0.20,
        unit="km"
    )
    session.add(regional_factor)
    session.commit()
    
    # Should use regional
    co2e_uk = calculate_co2e(session, "Transport", "Car, petrol (avg)", 100, "km", region="UK")
    assert co2e_uk == 20.0
    
    # Should fallback to global (0.17)
    co2e_global = calculate_co2e(session, "Transport", "Car, petrol (avg)", 100, "km", region="IN")
    assert co2e_global == 17.0

def test_invalid_category_raises_error(session: Session):
    with pytest.raises(ValueError):
        calculate_co2e(session, "Transport", "Rocket Ship", 100, "km")
