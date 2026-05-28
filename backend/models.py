from pydantic import BaseModel
from typing import List

#Login
class UserLogin(BaseModel):
    username: str
    password: str

#Place
class Place(BaseModel):
    name: str
    lat: float
    lon: float

#Tour
class TourCreate(BaseModel):
    is_public: bool
    places: List[Place]

class TourResponse(BaseModel):
    id: int
    owner_username: str
    is_public: bool
    places: List[Place]
    total_distance: float