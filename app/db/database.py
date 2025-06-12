from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import text
from ..core.config import settings
from ..core.logging import logger

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.connection_string = (
            f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
    
    def get_engine(self):
        if self.engine is None:
            try:
                self.engine = create_async_engine(
                    self.connection_string,
                    poolclass=QueuePool,
                    pool_size=20,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=1800,
                    echo=settings.debug
                )
                logger.info("Database engine created successfully")
            except Exception as e:
                logger.error(f"Failed to create database engine: {e}")
                raise
        return self.engine
    
    async def get_session(self) -> AsyncSession:
        engine = self.get_engine()
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        return async_session()
    
    async def test_connection(self) -> bool:
        """Test the database connection"""
        try:
            engine = self.get_engine()
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

db_manager = DatabaseManager()
