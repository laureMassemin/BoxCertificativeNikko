from pydantic import BaseModel
from typing import List

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# 1. Vue envoie        → { username: "hubert", password: "1234" }
# 2. Pydantic vérifie  → les données sont valides et crée un objet UserLogin
# 3. SQLAlchemy cherche → SELECT * FROM users WHERE username = "hubert"
# 4. FastAPI répond    → { token: "eyJ..." }
# 5. Vue reçoit        → redirige vers /trip

class User(Base):
    """Represents a user account in the database"""
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    tours = relationship("Tour", back_populates="owner")

class Tour(Base):
    """Represents a tour/trip in the database"""
    __tablename__ = "tours"
    id              = Column(Integer, primary_key=True, index=True)
    owner_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public       = Column(Boolean, default=False)
    total_distance  = Column(Float, default=0.0)

    owner = relationship("User", back_populates="tours")
    places = relationship("Place", back_populates="tour")

class Place(Base):
    """Represents a place/city in a tour"""
    __tablename__ = "places"
    id      = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    name    = Column(String, nullable=False)
    lat     = Column(Float, nullable=False)
    lon     = Column(Float, nullable=False)
    order  = Column(Integer, nullable=False)  

    tour = relationship("Tour", back_populates="places")

#Login
class UserLogin(BaseModel):
    """Schema for login and register requests"""
    username: str
    password: str

#Place
class PlaceSchema(BaseModel):
    """Schema for a place sent by the frontend"""
    name: str
    lat: float
    lon: float

#Tour
class TourCreate(BaseModel):
    """Schema for creating a new trip"""
    is_public: bool
    places: List[PlaceSchema]

class TourResponse(BaseModel):
    id: int
    owner_username: str
    is_public: bool
    places: List[PlaceSchema]
    total_distance: float