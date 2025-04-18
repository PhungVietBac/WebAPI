from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DetailInformationBase(BaseModel):
    idtrip: str
    idplace: str
    starttime: datetime
    endtime: datetime
    note: str

class DetailResponse(DetailInformationBase):
    iddetail: str

    class Config:
        from_attributes = True
class DetailCreate(DetailInformationBase):
    note: Optional[str] = None

class DetailUpdate(DetailInformationBase):
    starttime: Optional[datetime] = None
    endtime: Optional[datetime] = None
    note: Optional[str] = None
