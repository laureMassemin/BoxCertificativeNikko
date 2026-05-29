"""
API module for the Travel Planner application.

This module defines all the FastAPI routes for authentication, place search,
tour generation, and tour management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from geopy.geocoders import Nominatim
from models import UserLogin, User, Place, TourCreate, Tour, PlaceSchema, Hotel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from database import get_db
from algorithm import plan_tour, plan_tour_with_hotels
import uuid


router = APIRouter()
geolocator = Nominatim(user_agent="nikko_planner")

SECRET_KEY = "change-this-secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"])


@router.post("/register")
def register(data: UserLogin, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Hashes the password with bcrypt before storing it.
    Returns an error if the username is already taken.

    Args:
        data: Username and password provided by the user.
        db: SQLAlchemy database session.

    Returns:
        Confirmation message on success.

    Raises:
        HTTPException: 400 if the username is already taken.
    """
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = pwd_context.hash(data.password)
    new_user = User(username=data.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.

    Verifies the password against the stored bcrypt hash.
    Returns a signed JWT token containing the user ID.

    Args:
        data (UserLogin): Username and password provided by the user.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: JWT token and username on success.

    Raises:
        HTTPException 401: If the user is not found or the password is incorrect.
    """
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong password")
    token = jwt.encode({"sub": str(user.id)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "username": user.username}


@router.get("/places/search")
def search_place(name: str):
    """
    Search for places by name using the Nominatim geocoding API.

    Returns up to 3 results with name, latitude, and longitude.

    Args:
        name (str): The name of the city or place to search for.

    Returns:
        list: A list of Place objects with name, lat, and lon.

    Raises:
        HTTPException 404: If no location is found for the given name.
        HTTPException 503: If the geocoding API is unavailable.
    """
    try:
        locations = geolocator.geocode(name, language="en", exactly_one=False, limit=3)
        if not locations:
            raise HTTPException(status_code=404, detail=f"City {name} not found.")
        return [
            Place(name=loc.address, lat=loc.latitude, lon=loc.longitude)
            for loc in locations
        ]
    except Exception:
        raise HTTPException(status_code=503, detail="Error communicating with the Geocoding API.")


@router.get("/tours/share/{token}")
def get_tour_by_token(token: str, db: Session = Depends(get_db)):
    """
    Retrieve a tour by its unique share token.

    This endpoint is public — no authentication required.
    Used for sharing tours via a URL.

    Args:
        token (str): The UUID share token associated with the tour.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Tour details including places ordered by their index.

    Raises:
        HTTPException 404: If no tour matches the given token.
    """
    tour = db.query(Tour).filter(Tour.share_token == token).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    sorted_places = sorted(tour.places, key=lambda p: p.order)
    return {
        "id": tour.id,
        "owner_username": tour.owner.username,
        "is_public": tour.is_public,
        "share_token": tour.share_token,
        "total_distance": tour.total_distance,
        "places": [
            {"id": p.id, "name": p.name, "lat": p.lat, "lon": p.lon, "order": p.order}
            for p in sorted_places
        ]
    }


@router.get("/tours/{id}")
def get_tour(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a tour by its database ID.

    Also returns the list of hotel stops if the tour was generated
    with the hotel-based algorithm.

    Args:
        id (int): The unique ID of the tour.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Tour details including places and hotels ordered by their index.

    Raises:
        HTTPException 404: If no tour matches the given ID.
    """
    tour = db.query(Tour).filter(Tour.id == id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    
    hotels = db.query(Hotel).filter(Hotel.tour_id == id).order_by(Hotel.order).all()

    if hotels:
        # Tour avec hôtels — retourne les places groupées par hôtel dans l'ordre
        ordered_places = []
        for hotel in hotels:
            hotel_places = sorted(
                [p for p in tour.places if p.hotel_id == hotel.id],
                key=lambda p: p.order
            )
            ordered_places.extend(hotel_places)
    else:
        # Tour standard — tri par order global
        ordered_places = sorted(tour.places, key=lambda p: p.order)

    return {
        "id": tour.id,
        "owner_username": tour.owner.username,
        "is_public": tour.is_public,
        "share_token": tour.share_token,
        "total_distance": tour.total_distance,
        "places": [
            {"id": p.id, "name": p.name, "lat": p.lat, "lon": p.lon, "order": p.order, "hotel_id": p.hotel_id}
            for p in ordered_places
        ],
        "hotels": [
            {"id": h.id, "name": h.name, "lat": h.lat, "lon": h.lon, "order": h.order}
            for h in hotels
        ]
    }


@router.post("/tours/generate")
def generate_tour(tour_data: TourCreate, username: str, db: Session = Depends(get_db)):
    """
    Generate an optimized tour using the nearest neighbor + 2-opt algorithm.

    Saves the tour and its ordered places to the database.
    Assigns a unique UUID share token to the tour.

    Args:
        tour_data (TourCreate): List of places and visibility setting.
        username (str): Username of the tour owner.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The ID and share token of the created tour.

    Raises:
        HTTPException 400: If fewer than 2 places are provided.
        HTTPException 404: If the user is not found.
    """
    if len(tour_data.places) < 2:
        raise HTTPException(status_code=400, detail="Cannot generate a tour with less than 2 cities.")
    result = plan_tour(tour_data.places)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    tour = Tour(owner_id=user.id, is_public=tour_data.is_public, total_distance=result['length'], share_token=str(uuid.uuid4()))
    db.add(tour)
    db.commit()
    db.refresh(tour)
    order = 0
    for place in result['tour']:
        place = Place(tour_id=tour.id, name=place.name, lat=place.lat, lon=place.lon, order=order)
        db.add(place)
        order += 1
    db.commit()
    return {"id": tour.id, "share_token": tour.share_token}

@router.post("/tourswithhotels/generate")
def generate_tour_with_hotels(tour_data: TourCreate, username: str, db: Session = Depends(get_db)):
    if len(tour_data.places) < 2:
        raise HTTPException(status_code=400, detail="Cannot generate a tour with less than 2 cities.")

    result = plan_tour_with_hotels(tour_data.places)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tour = Tour(
        owner_id=user.id,
        is_public=tour_data.is_public,
        total_distance=result['distance_total'],
        share_token=str(uuid.uuid4())
    )
    db.add(tour)
    db.commit()
    db.refresh(tour)

    for hotel_order, etape in enumerate(result['etapes']):
        hotel = Hotel(
            tour_id=tour.id,
            name=etape['hotel'].name,
            lat=etape['hotel'].lat,
            lon=etape['hotel'].lon,
            order=hotel_order
        )
        db.add(hotel)
        db.commit()
        db.refresh(hotel)

        # Sauvegarde les villes de l'étape (hotel en tête + villes triées)
        for place_order, p in enumerate(etape['villes']):
            place = Place(
                tour_id=tour.id,
                hotel_id=hotel.id,
                name=p.name,
                lat=p.lat,
                lon=p.lon,
                order=place_order  # ordre local dans l'étape
            )
            db.add(place)

    db.commit()
    return {"id": tour.id, "share_token": tour.share_token}

@router.get("/tours/user/{username}")
def get_user_tours(username: str, token: str, db: Session = Depends(get_db)):
    """
    Retrieve all tours belonging to a specific user.

    Verifies that the JWT token belongs to the requested user
    to prevent accessing another user's trip list.

    Args:
        username (str): The username whose tours to retrieve.
        token (str): JWT token of the authenticated user.
        db (Session): SQLAlchemy database session.

    Returns:
        list: A list of tour summaries (id, distance, visibility, place count).

    Raises:
        HTTPException 401: If the token is invalid.
        HTTPException 403: If the token does not belong to the requested user.
        HTTPException 404: If the user is not found.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own trips")
    tours = db.query(Tour).filter(Tour.owner_id == user.id).all()
    return [
        {"id": t.id, "total_distance": t.total_distance, "is_public": t.is_public, "places_count": len(t.places)}
        for t in tours
    ]


@router.post("/distance")
def calculate_distance(places: List[PlaceSchema]):
    """
    Calculate the total distance of a tour given an ordered list of places.

    Uses the personalised_tour_length function which sums the great-circle
    distances between consecutive places and adds the return trip to the start.

    Args:
        places (List[PlaceSchema]): Ordered list of places with lat/lon.

    Returns:
        dict: The total distance in kilometers, rounded to 2 decimal places.
    """
    from algorithm import personalised_tour_length
    total = personalised_tour_length(places)
    return {"total_distance": round(total, 2)}


@router.put("/tours/{id}/places")
def update_tour_places(id: int, places: List[PlaceSchema], db: Session = Depends(get_db)):
    """
    Update the order of places in a tour and recalculate the total distance.

    Deletes all existing places for the tour and re-inserts them
    in the new order provided by the frontend.

    Args:
        id (int): The ID of the tour to update.
        places (List[PlaceSchema]): New ordered list of places.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The recalculated total distance in kilometers.

    Raises:
        HTTPException 404: If the tour is not found.
    """
    tour = db.query(Tour).filter(Tour.id == id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    db.query(Place).filter(Place.tour_id == id).delete()
    from algorithm import personalised_tour_length
    total = personalised_tour_length(places)
    for i, p in enumerate(places):
        new_place = Place(tour_id=id, name=p.name, lat=p.lat, lon=p.lon, order=i)
        db.add(new_place)
    tour.total_distance = round(total, 2)
    db.commit()
    return {"total_distance": round(total, 2)}