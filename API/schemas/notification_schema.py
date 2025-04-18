from pydantic import BaseModel
from typing import Optional

class NotificationBase(BaseModel):
    content: str

class NotificationResponse(NotificationBase):
    idnotf: str
    iduser: str
    isread: bool
    class Config:
        from_attributes = True

class NotificationCreate(NotificationBase):
    iduser: str

class NotificationUpdate(NotificationBase):
    content: Optional[str] = None
    isread: bool