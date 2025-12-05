from fastapi import APIRouter
from src.services.translator import Translator
from src.models.personalization import TranslationRequest, TranslationResponse

router = APIRouter()
translator = Translator()

@router.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    translated_content = await translator.translate_content(request.chapter_content)
    return TranslationResponse(translated_content=translated_content)
