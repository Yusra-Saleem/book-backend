import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory (parent of src)
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "FastAPI RAG Service"
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    NEON_DB_URL: str = os.getenv("NEON_DB_URL", "")
    BETTER_AUTH_API_KEY: str = os.getenv("BETTER_AUTH_API_KEY", "")
    # Allow frontend on localhost:3000 (and 127.0.0.1:3000) to talk to FastAPI on :8000
    # You can override with CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,https://your-domain.com"
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

# Log API key status (without exposing the actual key)
if settings.OPENAI_API_KEY:
    key_preview = settings.OPENAI_API_KEY[:8] + "..." + settings.OPENAI_API_KEY[-4:] if len(settings.OPENAI_API_KEY) > 12 else "***"
    print(f"[OK] OpenAI API key loaded: {key_preview}")
else:
    print("[WARN] Warning: OPENAI_API_KEY not found in environment. Please add it to your .env file.")