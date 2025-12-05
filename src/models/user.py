from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: str
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    email: str
    password: str
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None


class UserProfileUpdate(BaseModel):
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None

