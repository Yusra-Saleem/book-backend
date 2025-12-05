import uuid
from pydantic import BaseModel

class PersonalizationRequest(BaseModel):
    chapter_content: str
    user_id: uuid.UUID

class PersonalizationResponse(BaseModel):
    personalized_content: str

class TranslationRequest(BaseModel):
    chapter_content: str

class TranslationResponse(BaseModel):
    translated_content: str
