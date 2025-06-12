import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

@pytest.fixture
async def db_session():
    engine = create_async_engine(
        f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@localhost:5432/test_db"
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()

# tests/test_query_processor.py
import pytest
from app.services.query_processor import QueryProcessor

@pytest.mark.asyncio
async def test_process_queries(db_session):
    processor = QueryProcessor(db_session)
    # Add your test cases here
