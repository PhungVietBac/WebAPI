from pydantic import BaseModel
from typing import Optional

class ReviewBase(BaseModel):
    idtrip: str
    iduser: str
    comment: str
    rating: float  

class ReviewResponse(ReviewBase):
    idreview: str
    
    class Config:
        from_attributes = True
class ReviewCreate(ReviewBase):
    comment: Optional[str] = None