from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ConversationBase(BaseModel):
    title: str
    
class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    
    class Config:
        from_attributes = True
        
class ConversationCreate(ConversationBase):
    user_id: str
    created_at: Optional[datetime] = datetime.now()

class ConversationUpdate(ConversationBase):
    title: Optional[str] = None
    updated_at: Optional[datetime] = datetime.now()
    is_archived: Optional[bool] = False
    
class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int
    hasNext: bool
    hasPrev: bool
    
class CombineResponse(BaseModel):
    conversations: list[ConversationResponse]
    pagination: Pagination