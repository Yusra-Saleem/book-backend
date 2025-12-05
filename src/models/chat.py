from typing import List, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    query: str
    selected_text: Optional[str] = None
    current_page: Optional[str] = None  # Current page path
    user_id: Optional[str] = None
    conversation_history: Optional[List[Message]] = None  # Previous messages

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    conversation_history: List[Message]  # Full history including this response
