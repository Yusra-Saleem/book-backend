"""
Simple authentication service using JWT and bcrypt.
No external auth provider needed - just basic username/password.
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models import User as UserModel
from src.models.user import User, UserCreate, UserInDB
from src.core.config import settings


class SimpleAuthService:
    """Simple JWT-based authentication service."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify a JWT token and return its payload."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    async def register_user(
        db: AsyncSession,
        email: str,
        password: str,
        username: str,
        software_background: Optional[str] = None,
        hardware_background: Optional[str] = None,
    ) -> Optional[UserInDB]:
        """Register a new user."""
        # Check if user already exists
        result = await db.execute(select(UserModel).filter(UserModel.email == email))
        existing_user = result.scalars().first()
        
        if existing_user:
            return None  # User already exists
        
        # Hash password
        hashed_password = SimpleAuthService.hash_password(password)
        
        # Create new user
        new_user = UserModel(
            username=username,
            email=email,
            hashed_password=hashed_password,
            software_background=software_background,
            hardware_background=hardware_background,
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return UserInDB(
            username=new_user.username,
            email=new_user.email,
            hashed_password=new_user.hashed_password,
            full_name=new_user.full_name,
            password="",
            software_background=new_user.software_background,
            hardware_background=new_user.hardware_background,
        )
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> Optional[dict]:
        """Authenticate a user and return token if successful."""
        result = await db.execute(select(UserModel).filter(UserModel.email == email))
        user = result.scalars().first()
        
        if not user:
            return None
        
        if not SimpleAuthService.verify_password(password, user.hashed_password):
            return None
        
        # Create token
        access_token = SimpleAuthService.create_access_token(
            data={"sub": user.email, "user_id": user.username}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "software_background": user.software_background,
                "hardware_background": user.hardware_background,
            }
        }
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserInDB]:
        """Get a user by email."""
        result = await db.execute(select(UserModel).filter(UserModel.email == email))
        user = result.scalars().first()
        
        if not user:
            return None
        
        return UserInDB(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            password="",
            software_background=user.software_background,
            hardware_background=user.hardware_background,
        )
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[UserInDB]:
        """Get a user by username."""
        result = await db.execute(select(UserModel).filter(UserModel.username == username))
        user = result.scalars().first()
        
        if not user:
            return None
        
        return UserInDB(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            password="",
            software_background=user.software_background,
            hardware_background=user.hardware_background,
        )
