"""
Database configuration and session management.
Uses async SQLAlchemy with PostgreSQL and asyncpg driver.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import logging
import ssl
from ..core.config import settings
from sqlalchemy import text

# Set up logging
logger = logging.getLogger(__name__)


# Create async engine with proper SSL configuration for Neon
def create_database_engine():
    """Create database engine with proper configuration"""
    database_url = settings.database_url
    connect_args = {}
    
    # Configure SSL for cloud databases like Neon
    if "neon.tech" in database_url or "sslmode=require" in database_url:
        # For asyncpg, we need to set ssl=True in connect_args
        connect_args = {
            "ssl": True,
            "server_settings": {
                "application_name": "romanian_admin_platform",
            }
        }
        # Clean the URL to use asyncpg format
        database_url = database_url.replace("?sslmode=require", "")
        if "?" in database_url:
            database_url += "&ssl=true"
        else:
            database_url += "?ssl=true"
    
    logger.info(f"Connecting to database: {database_url.split('@')[0]}@****")
    
    return create_async_engine(
        database_url,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        future=True,
        connect_args=connect_args,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections every 30 minutes
    )


engine = create_database_engine()

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models
    """
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables with error handling for development
    """
    # Skip database initialization if configured
    if settings.SKIP_DB_INIT:
        logger.info("Skipping database initialization (SKIP_DB_INIT=True)")
        return
    
    try:
        # Import all models to ensure they are registered
        from ..models import user, document, archive, parking, notification, auth_token, settings as settings_models
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified successfully")
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        if settings.ENVIRONMENT == "development":
            logger.warning("⚠️  Database not available - continuing in development mode")
            logger.warning("   To connect to database, ensure PostgreSQL is running and configured")
            logger.warning(f"   Expected database URL: {settings.database_url.split('@')[0]}@****")
            return
        else:
            # In production, database is required
            raise e


async def check_database_connection() -> bool:
    """
    Check if database connection is available
    """
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False 