from pydantic import BaseModel
from typing import List

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

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
    share_token     = Column(String, unique=True, nullable=False)
    

    owner = relationship("User", back_populates="tours")
    places = relationship("Place", back_populates="tour")

class Hotel(Base):
    """Represents a hotel/central place in a tour stage"""
    __tablename__ = "hotels"
    id      = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    name    = Column(String, nullable=False)
    lat     = Column(Float, nullable=False)
    lon     = Column(Float, nullable=False)
    order   = Column(Integer, nullable=False)  

    places  = relationship("Place", back_populates="hotel")

class Place(Base):
    """Represents a place/city in a tour"""
    __tablename__ = "places"
    id       = Column(Integer, primary_key=True, index=True)
    tour_id  = Column(Integer, ForeignKey("tours.id"), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=True) 
    name     = Column(String, nullable=False)
    lat      = Column(Float, nullable=False)
    lon      = Column(Float, nullable=False)
    order    = Column(Integer, nullable=False)

    tour  = relationship("Tour", back_populates="places")
    hotel = relationship("Hotel", back_populates="places")

class UserLogin(BaseModel):
    """Schema for login and register requests"""
    username: str
    password: str

class PlaceSchema(BaseModel):
    """Schema for a place sent by the frontend"""
    name: str
    lat: float
    lon: float

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