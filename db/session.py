from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from core.config import get_settings

settings = get_settings()

# Create async engine and sessionmaker
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session and ensure it is closed afterwards."""
    async with async_session() as session:
        yield session
