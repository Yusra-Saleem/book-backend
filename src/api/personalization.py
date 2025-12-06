from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.content_adaptor import ContentAdaptor
from src.models.personalization import PersonalizationRequest, PersonalizationResponse
from src.models.user import UserInDB
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
    Creates a user profile based on user_id.
    """
    # Create a basic user profile from the request
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

