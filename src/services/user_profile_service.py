from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.user import User, UserCreate, UserProfileUpdate

class UserProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: dict) -> User:
        new_user = User(**user_data)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def update_user_profile(self, user_id: UUID, profile_update: UserProfileUpdate) -> User | None:
        user = await self.get_user_by_id(user_id)
        if user:
            if profile_update.software_background is not None:
                user.software_background = profile_update.software_background
            if profile_update.hardware_background is not None:
                user.hardware_background = profile_update.hardware_background
            await self.db.commit()
            await self.db.refresh(user)
        return user