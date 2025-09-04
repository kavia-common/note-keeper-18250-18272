"""
Database configuration with SQLAlchemy (async).

Provides async engine, session factory, and Base for models.
"""
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def _create_engine() -> AsyncEngine:
    """Create the async engine based on settings."""
    settings = get_settings()
    database_url = settings.DATABASE_URL

    # Ensure URL is async for SQLite
    if database_url.startswith("sqlite:///") and "+aiosqlite" not in database_url:
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

    engine = create_async_engine(database_url, echo=False, future=True)
    return engine


def get_engine() -> AsyncEngine:
    """Get or create the global async engine."""
    global _engine
    if _engine is None:
        _engine = _create_engine()
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session_factory


# PUBLIC_INTERFACE
async def get_db_session():
    """Async dependency that yields a database session."""
    async_session = get_session_factory()
    async with async_session() as session:
        yield session
