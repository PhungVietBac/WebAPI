from pydantic import BaseModel

class PlaceImageBase(BaseModel):
    idplace: str
    image: str

class PlaceImageResponse(PlaceImageBase):
    idimage: str
    
    class Config:
        from_attributes = True
        
class PlaceImageCreate(PlaceImageBase):
    pass
