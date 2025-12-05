"""
Initialize Neon DB tables.
Run this script once to create the users table.
"""
import asyncio
from sqlalchemy import text
from src.database.connection import _init_db_if_needed, engine
from src.database.models import Base
from src.core.config import settings

async def init_db():
    """Create all tables in the database."""
    if not settings.NEON_DB_URL:
        print("⚠️  NEON_DB_URL not set. Skipping database initialization.")
        return
    
    print("Initializing database...")
    _init_db_if_needed()
    
    if engine is None:
        print("❌ Database engine not initialized. Check your NEON_DB_URL.")
        return
    
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created successfully!")
            
            # Verify users table exists
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
            )
            exists = result.scalar()
            if exists:
                print("✅ Users table verified!")
            else:
                print("⚠️  Users table not found after creation.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("Make sure your NEON_DB_URL is correct and the database is accessible.")

if __name__ == "__main__":
    asyncio.run(init_db())

