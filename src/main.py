from fastapi import FastAPI
from src.core.config import settings
from src.api.chat import router as chat_router
from src.api.personalization import router as personalization_router
from src.api.translation import router as translation_router
from src.api.profile import router as profile_router

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FastAPI is running!"}

@app.get("/api/v1/config/check")
async def check_config():
    """Check if OpenAI API key is configured (without exposing the key)."""
    from src.core.config import settings
    
    has_openai_key = bool(settings.OPENAI_API_KEY)
    key_preview = None
    key_valid = False
    key_error = None
    
    if has_openai_key:
        key = settings.OPENAI_API_KEY
        key_preview = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
        
        # Test the API key using openai-agents
        try:
            from agents import Agent, Runner
            import os
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
            
            test_agent = Agent(
                name="Test Agent",
                instructions="You are a test agent.",
                model="gpt-3.5-turbo"
            )
            runner = Runner(test_agent)
            # Run a minimal test
            result = runner.run("test")
            key_valid = True
        except Exception as e:
            key_error = str(e)
            if "401" in str(e) or "invalid" in str(e).lower():
                key_error = "Invalid API key"
            elif "429" in str(e) or "quota" in str(e).lower():
                key_error = "Quota exceeded or rate limited"
            else:
                key_error = f"Error: {str(e)[:100]}"
    
    return {
        "openai_configured": has_openai_key,
        "key_preview": key_preview,
        "key_valid": key_valid,
        "key_error": key_error,
        "qdrant_configured": bool(settings.QDRANT_API_KEY),
        "neon_db_configured": bool(settings.NEON_DB_URL),
    }

app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(personalization_router, prefix="/api/v1", tags=["Personalization"])
app.include_router(translation_router, prefix="/api/v1", tags=["Translation"])
app.include_router(profile_router, prefix="/api/v1", tags=["Profile"])
