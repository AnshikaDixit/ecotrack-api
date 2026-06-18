from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from app.db.database import create_db_and_tables
from app.db.seed_emission_factors import seed_factors
from app.routers import auth, activities, reference, footprint, insights, goals
from app.core.rate_limit import limiter, _rate_limit_exceeded_handler
import os

app = FastAPI(title="EcoTrack API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_factors()

# Setup CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(auth.router, prefix="/users", tags=["users"]) # Since /me is in auth.py
app.include_router(activities.router, prefix="/activities", tags=["activities"])
app.include_router(reference.router, prefix="/reference", tags=["reference"])
app.include_router(footprint.router, prefix="/footprint", tags=["footprint"])
app.include_router(insights.router, prefix="/insights", tags=["insights"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

