from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import UserProfileUpdate, UserInDB
from ..database.connection import get_db

router = APIRouter()

@router.get("/profile/{user_id}", response_model=UserInDB)
async def get_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user profile by user_id (username)."""
    # Return a default user profile
    return UserInDB(
        username=user_id,
        email=None,
        full_name=None,
        password="",
        software_background=None,
        hardware_background=None,
        hashed_password="",
    )

@router.put("/profile/{user_id}", response_model=UserInDB)
async def update_profile(
    user_id: str,
    profile_update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user profile (software_background, hardware_background)."""
    # Return updated user profile with the provided data
    return UserInDB(
        username=user_id,
        email=None,
        full_name=None,
        password="",
        software_background=profile_update.software_background,
        hardware_background=profile_update.hardware_background,
        hashed_password="",
    )

