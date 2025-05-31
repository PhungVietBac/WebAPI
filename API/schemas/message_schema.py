from pydantic import BaseModel
from typing import Optional, Any, Literal
from datetime import datetime
from schemas.conversation_schema import Pagination

class MessageBase(BaseModel):
    content: str
    role: Literal["user", "assistant"]
    metadata: Optional[Any] = None
    token_count: int
    
class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
    
class MessageCreate(MessageBase):
    conversation_id: str
    created_at: Optional[datetime] = datetime.now()
    
class MessageUpdate(MessageBase):
    pass

class CombineResponse(BaseModel):
    messages: list[MessageResponse]
    pagination: Pagination