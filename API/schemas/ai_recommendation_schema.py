from pydantic import BaseModel

class AIRecommendationBase(BaseModel):
    input: str
    iduser: str
class AIRecResponse(AIRecommendationBase):
    idairec: str
    output: str

    class Config:
        from_attributes = True
class AIRecCreate(AIRecommendationBase):
    pass

class AIRecUpdate(AIRecommendationBase):
    pass

class AIRequest(BaseModel):
    departure: str
    destination: str
    time: str
    days: int
    people: int
    money: str
    transportation: str = None
    travelStyle: str = None
    interests: list[str] = None
    accommodation: str = None
