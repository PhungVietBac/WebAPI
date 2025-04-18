from pydantic import BaseModel

class TripMemberBase(BaseModel):
    idtrip: str
    iduser: str

class TripMemberResponse(TripMemberBase):
    class Config:
        from_attributes = True

class TripMemberCreate(TripMemberBase):
    pass