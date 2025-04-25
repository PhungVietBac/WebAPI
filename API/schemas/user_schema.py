from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    name: str
    username: str
    gender: int
    email: str
    phonenumber: Optional[str] = None
    avatar: Optional[str] = None
    theme: int = 0
    language: int = 0
    description: Optional[str] = None

class UserResponse(UserBase):
    iduser: str
    role: int
    
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    gender: Optional[int] = None
    avatar: Optional[str] = None
    language: Optional[int] = None
    password: str

class UserUpdate(UserBase):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    gender: Optional[int] = None
    avatar: Optional[str] = None
    theme: Optional[int] = None
    language: Optional[int] = None
    password: Optional[str] = None