from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class TripBase(BaseModel):
    name: str
    startdate: datetime
    enddate: datetime
    
class TripResponse(TripBase):
    idtrip: str

    class Config:
        from_attributes = True

class TripCreate(TripBase):
    pass

class TripUpdate(TripBase):
    name: Optional[str] = None
    startdate: Optional[datetime] = None
    enddate: Optional[datetime] = None