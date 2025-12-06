"""
Simple authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import get_db
from src.services.simple_auth_service import SimpleAuthService
from src.models.user import UserCreate, UserInDB
from pydantic import BaseModel

router = APIRouter()


class SignupRequest(BaseModel):
    email: str
    password: str
    username: str
    software_background: str = None
    hardware_background: str = None


class SigninRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Register user
    user = await SimpleAuthService.register_user(
        db=db,
        email=request.email,
        password=request.password,
        username=request.username,
        software_background=request.software_background,
        hardware_background=request.hardware_background,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create token
    access_token = SimpleAuthService.create_access_token(
        data={"sub": user.email, "user_id": user.username}
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "software_background": user.software_background,
            "hardware_background": user.hardware_background,
        }
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    request: SigninRequest,
    db: AsyncSession = Depends(get_db)
):
    """Sign in a user."""
    result = await SimpleAuthService.authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return AuthResponse(**result)


@router.get("/me")
async def get_current_user(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user."""
    # Verify token
    payload = SimpleAuthService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = await SimpleAuthService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "software_background": user.software_background,
        "hardware_background": user.hardware_background,
    }
