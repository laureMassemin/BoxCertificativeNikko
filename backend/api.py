from fastapi import APIRouter, HTTPException, Depends
from typing import List
from geopy.geocoders import Nominatim
from models import UserLogin, User, Place, TourCreate, Tour, PlaceSchema
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from database import get_db
from algorithm import (plan_tour)


router = APIRouter()

geolocator = Nominatim(user_agent="nikko_planner")
router = APIRouter()

SECRET_KEY = "change-this-secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"])

@router.post("/register")
def register(data: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    else:
        hashed_password = pwd_context.hash(data.password)
        new_user = User(username=data.username, password=hashed_password)
        db.add(new_user)
        db.commit()
        return {"message": "User created successfully"}

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    username = data.username
    user = db.query(User).filter(User.username == username).first()
    if not user : 
        raise HTTPException(status_code=401, detail="User not found")
    else:
        password_is_correct = pwd_context.verify(data.password, user.password)
        if not password_is_correct:
            raise HTTPException(status_code=401, detail="Wrong password")
        else:
            token = jwt.encode({"sub": str(user.id)}, SECRET_KEY, algorithm=ALGORITHM)
            return {"token": token, "username": user.username}


#City search test
@router.get("/places/search")
def search_place(name: str):
    #Coordinate return simulation
    try:
        locations = geolocator.geocode(name, exactly_one=False, limit=3)
        if not locations:
            raise HTTPException(status_code=404, detail=f"City {name} not found.")

        results=[]
        for loc in locations:
            results.append(
                Place(
                    name=loc.address,
                    lat=loc.latitude,
                    lon=loc.longitude
                )
            )
        return results
    except Exception as e:
        raise HTTPException(status_code=503, detail="Error communicating with the Geocoding API.")

    
@router.get("/tours/{id}")
def search_tours(id: int, db: Session = Depends(get_db)):
    tour = db.query(Tour).filter(Tour.id == id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    
    sorted_places = sorted(tour.places, key=lambda p: p.order)
    
    return {
        "id": tour.id,
        "owner_username": tour.owner.username,
        "is_public": tour.is_public,
        "total_distance": tour.total_distance,
        "places": [
            {"id": p.id, "name": p.name, "lat": p.lat, "lon": p.lon, "order": p.order}
            for p in sorted_places
        ]
    }

@router.post("/tours/generate")
def generate_tour(tour_data: TourCreate, username: str, db: Session = Depends(get_db)):
    '''return the id of the generated tour'''
    if len(tour_data.places) <2:
        raise HTTPException(status_code=400, detail="Cannot generate a tour with less than 2 cities.")
    
    result = plan_tour(tour_data.places)

    user = db.query(User).filter(User.username ==username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tour = Tour(owner_id=user.id, is_public = tour_data.is_public, total_distance = result['length'])
    db.add(tour)
    db.commit()
    db.refresh(tour)

    order=0
    for place in result['tour']:
        place = Place(tour_id=tour.id, name=place.name, lat=place.lat, lon=place.lon, order=order)
        db.add(place)
        order+=1
    db.commit()

    return {"id": tour.id}
@router.get("/tours/user/{username}")
def get_user_tours(username: str, token: str, db: Session = Depends(get_db)):
    
    # Verify token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check that the token belongs to the requested username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own trips")

    tours = db.query(Tour).filter(Tour.owner_id == user.id).all()
    return [
        {
            "id": t.id,
            "total_distance": t.total_distance,
            "is_public": t.is_public,
            "places_count": len(t.places)
        }
        for t in tours
    ]
@router.post("/distance")
def calculate_distance(places: List[PlaceSchema]):
    from algorithm import personalised_tour_length
    total = personalised_tour_length(places)
    return {"total_distance": round(total, 2)}