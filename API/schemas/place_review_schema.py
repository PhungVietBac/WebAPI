from pydantic import BaseModel
from typing import Optional

class PlaceReviewBase(BaseModel):
    idplace: str
    name: str
    comment: str
    rating: float  

class PlaceReviewResponse(PlaceReviewBase):
    idreview: str
    
    class Config:
        from_attributes = True
        
class PlaceReviewCreate(PlaceReviewBase):
    comment: Optional[str] = None