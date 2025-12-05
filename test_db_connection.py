"""Test database connection"""
import asyncio
from src.core.config import settings
from src.database.connection import _make_async_url, _init_db_if_needed, engine

async def test_connection():
    print("Testing database connection...")
    print(f"NEON_DB_URL configured: {bool(settings.NEON_DB_URL)}")
    
    if settings.NEON_DB_URL:
        # Show first 50 chars of URL (masked)
        url_preview = settings.NEON_DB_URL[:50] + "..." if len(settings.NEON_DB_URL) > 50 else settings.NEON_DB_URL
        print(f"URL preview: {url_preview}")
        
        # Test URL parsing
        clean_url, connect_args = _make_async_url(settings.NEON_DB_URL)
        print(f"Cleaned URL: {clean_url[:80]}...")
        print(f"Connect args: {connect_args}")
        
        # Try to initialize
        _init_db_if_needed()
        
        if engine:
            print("Engine initialized successfully!")
            # Try a simple query
            async with engine.begin() as conn:
                result = await conn.execute("SELECT 1")
                print(f"Test query result: {result.scalar()}")
                print("Database connection successful!")
        else:
            print("Engine is None - initialization failed")
    else:
        print("NEON_DB_URL not set in environment")

if __name__ == "__main__":
    asyncio.run(test_connection())
