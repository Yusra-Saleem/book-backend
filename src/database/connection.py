from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Lazy initialization - don't create engine at import time to prevent hanging
engine = None
AsyncSessionLocal = None


def _make_async_url(url: str) -> tuple[str, dict]:
    """
    Ensure the database URL uses an async driver and extract SSL parameters.

    Neon typically provides URLs like:
      postgres://user:pass@host/db?sslmode=require
    or:
      postgresql://user:pass@host/db?sslmode=require

    For SQLAlchemy asyncio with asyncpg, we need:
      postgresql+asyncpg://user:pass@host/db
    
    Returns:
      tuple: (cleaned_url, connect_args_dict)
    """
    if not url:
        return "", {}

    # Parse and remove sslmode from URL
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Extract sslmode if present
    sslmode = query_params.pop('sslmode', ['require'])[0] if 'sslmode' in query_params else None
    
    # Build connect_args for asyncpg
    connect_args = {}
    if sslmode in ('require', 'verify-ca', 'verify-full'):
        # asyncpg expects ssl=True (boolean) or an SSLContext object
        # For Neon DB with sslmode=require, we just need ssl=True
        import ssl
        connect_args['ssl'] = ssl.create_default_context()
    
    # Rebuild URL without sslmode
    new_query = urlencode(query_params, doseq=True)
    parsed = parsed._replace(query=new_query)
    clean_url = urlunparse(parsed)
    
    # Convert to asyncpg driver
    if "+asyncpg" in clean_url:
        return clean_url, connect_args

    if clean_url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + clean_url[len("postgresql://") :], connect_args

    if clean_url.startswith("postgres://"):
        # Alias often used by Neon; normalize to postgresql+asyncpg
        return "postgresql+asyncpg://" + clean_url[len("postgres://") :], connect_args

    # Fallback: return as-is (for non-Postgres drivers)
    return clean_url, connect_args


def _init_db_if_needed():
    """Initialize database connection only when needed, not at import time."""
    global engine, AsyncSessionLocal
    
    if engine is not None:
        return  # Already initialized
    
    async_db_url, connect_args = _make_async_url(settings.NEON_DB_URL)
    
    if not async_db_url:
        # No database URL configured - database features disabled
        return
    
    try:
        # Create engine with settings to prevent hanging
        engine = create_async_engine(
            async_db_url,
            echo=False,  # Disable echo to reduce startup noise
            pool_pre_ping=True,  # Verify connections before using
            connect_args=connect_args,  # Pass SSL and other connection args
        )

        # Create a sessionmaker bound to the engine for async sessions
        AsyncSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    except Exception as e:
        # If engine creation fails, log but don't crash
        print(f"Warning: Could not initialize database connection: {e}")
        print("Database features will be disabled. Set NEON_DB_URL to enable.")


async def get_db():
    """Get database session, initializing connection if needed."""
    _init_db_if_needed()
    
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Async database session is not configured. "
            "Please set a valid NEON_DB_URL (e.g. postgresql://... from Neon) in your .env file."
        )

    async with AsyncSessionLocal() as session:
        yield session
