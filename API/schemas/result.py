from pydantic import BaseModel
from typing import List, Optional

class Activity(BaseModel):
    time: str
    name: Optional[str] = None
    lat: float
    lon: float
    description: str
    namePlace: str
    city: str
    province: Optional[str] = None
    address: str
    rating: float
    
class TripDay(BaseModel):
    day: int
    date: str
    activities: List[Activity]
    
class TripParameters(BaseModel):
    location: str
    days: List[TripDay]
    
class TripPlan(BaseModel):
    name: str
    parameters: TripParameters