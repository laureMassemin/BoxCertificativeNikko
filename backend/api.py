from fastapi import APIRouter
from models import UserLogin, Place, TourCreate

router = APIRouter()

@router.post("/login")
def login(user_data: UserLogin):
    #mock user
    return {"token": "faux_token_temporaire", "message": "Login success"}

#City search test
@router.get("/places/search")
def search_place(name: str):
    #Coordinate return simulation
    return [
        {"name": f"{name} Center", "lat": 48.8566, "lon": 2.3522},
        {"name": f"{name} Station", "lat": 48.8738, "lon": 2.3596}
    ]

#mock algo route
@router.post("/tours/generate")
def generate_tour(tour_data: TourCreate):
    #Mock tour
    return {
        "distance_total": 45.2,
        "optimized_route": tour_data.places
    }