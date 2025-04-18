from pydantic import BaseModel

class FriendBase(BaseModel):
    idself: str
    idfriend: str

class FriendResponse(FriendBase):
    isaccept: bool
    class Config:
        from_attributes = True
        
class FriendCreate(FriendBase):
    pass

class FriendUpdate(FriendBase):
    isaccept: bool