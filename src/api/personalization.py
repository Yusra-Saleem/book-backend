from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.content_adaptor import ContentAdaptor
from src.models.personalization import PersonalizationRequest, PersonalizationResponse
from src.models.user import UserInDB
from src.services.auth_service import get_user_by_id
from src.database.connection import get_db

router = APIRouter()
content_adaptor = ContentAdaptor()


@router.post("/personalize", response_model=PersonalizationResponse)
async def personalize(
    request: PersonalizationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Personalize textbook content for a user.
    Loads user profile from Neon DB using user_id.
    """
    # Load user profile from database
    user_profile = await get_user_by_id(request.user_id, db)
    
    if not user_profile:
        # Fallback to minimal profile if user not found
        user_profile = UserInDB(
            username=str(request.user_id),
            email=None,
            full_name=None,
            password="",
            software_background=None,
            hardware_background=None,
            hashed_password="",
        )

    personalized_content = await content_adaptor.personalize_content(
        request.chapter_content, user_profile
    )
    return PersonalizationResponse(personalized_content=personalized_content)

