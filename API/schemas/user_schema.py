from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    name: str
    username: str
    gender: int
    email: str
    phonenumber: Optional[str] = None
    avatar: Optional[bytes] = None
    theme: int = 0
    language: int = 0

class UserResponse(UserBase):
    iduser: str
    
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    gender: Optional[int] = None
    avatar: Optional[bytes] = None
    language: Optional[int] = None
    password: str

class UserUpdate(UserBase):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    gender: Optional[int] = None
    avatar: Optional[bytes] = None
    theme: Optional[int] = None
    language: Optional[int] = None
    password: Optional[str] = None