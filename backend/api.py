from fastapi import APIRouter, HTTPException
from typing import List
from geopy.geocoders import Nominatim
from models import UserLogin, Place, TourCreate

router = APIRouter()

geolocator = Nominatim(user_agent="nikko_planner")

@router.post("/login")
def login(user_data: UserLogin):
    #mock user
    return {"token": "faux_token_temporaire", "message": "Login success"}

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



#mock algo route
@router.post("/tours/generate")
def generate_tour(tour_data: TourCreate):
    if len(tour_data.places) <2:
        raise HTTPException(status_code=400, detail="Cannot generate a tour with less than 2 cities.")
    try:
        #algo_result = optimize_tour(tour_data.places)
        #return algo_result

        return {
            "message" : "Waiting for the algorithm",
            "total_distance" : 0.0,
            "optimized_route" : tour_data.places
        }
    except Exception as e :
        raise HTTPException(status_code=500, detail="Internal server error during tour calculation")