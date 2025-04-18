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
