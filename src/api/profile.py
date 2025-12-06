from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User, UserProfileUpdate
from ..database.connection import get_db

router = APIRouter()

@router.get("/profile/{user_id}", response_model=User)
async def get_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user profile by user_id (username)."""
    # Return a default user profile
    return User(
        username=user_id,
        email=None,
        full_name=None,
    )

@router.put("/profile/{user_id}", response_model=User)
async def update_profile(
    user_id: str,
    profile_update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user profile (full_name)."""
    # Return updated user profile with the provided data
    return User(
        username=user_id,
        email=None,
        full_name=profile_update.full_name,
    )

