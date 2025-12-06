from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None

