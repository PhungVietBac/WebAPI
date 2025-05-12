from pydantic import BaseModel
from typing import Optional

class PlaceBase(BaseModel):
    name: str
    country: str
    city: str
    province: Optional[str] = None
    address: str
    description: str
    rating: float
    type: Optional[int] = None
    lat: float
    lon: float

class PlaceResponse(PlaceBase):
    idplace: str

    class Config:
        from_attributes = True
        
class PlaceCreate(PlaceBase):
    description: Optional[str]

class PlaceUpdate(PlaceBase):
    name: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    type: Optional[int] = None