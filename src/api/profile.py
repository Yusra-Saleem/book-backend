from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import UserProfileUpdate, UserInDB
from ..services.auth_service import get_user_by_id, update_user_profile
from ..database.connection import get_db

router = APIRouter()

@router.get("/profile/{user_id}", response_model=UserInDB)
async def get_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user profile by user_id (username)."""
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/profile/{user_id}", response_model=UserInDB)
async def update_profile(
    user_id: str,
    profile_update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user profile (software_background, hardware_background)."""
    updated_user = await update_user_profile(
        username=user_id,
        software_background=profile_update.software_background,
        hardware_background=profile_update.hardware_background,
        db=db
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

