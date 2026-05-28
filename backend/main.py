from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from api import router

# Create the FastAPI app
app = FastAPI(title="Travel Planner API")

# Allow Vue (localhost:5173) to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables in travel.db on startup
Base.metadata.create_all(bind=engine)

# Register all routes from api.py
app.include_router(router)