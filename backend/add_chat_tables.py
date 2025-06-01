"""
Migration script to add AI Chat tables to the database
Run this script after updating the models to add the new chat functionality.
"""

import asyncio
import asyncpg
from app.core.config import settings
from app.db.database import create_tables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Add chat tables to the database"""
    try:
        logger.info("🔄 Starting chat tables migration...")
        
        # Create all tables (will only create new ones)
        await create_tables()
        
        logger.info("✅ Chat tables migration completed successfully!")
        logger.info("📊 New tables added:")
        logger.info("   - chat_sessions (for managing chat conversations)")
        logger.info("   - chat_messages (for storing individual messages)")
        logger.info("   - agent_executions (for tracking AI agent processing details)")
        logger.info("   - Updated users table with chat_sessions relationship")
        
        # Test database connection
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        # Check if tables were created
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('chat_sessions', 'chat_messages', 'agent_executions')
            ORDER BY table_name;
        """)
        
        logger.info("📋 Verified tables in database:")
        for table in tables:
            logger.info(f"   ✓ {table['table_name']}")
        
        await conn.close()
        
        if len(tables) == 3:
            logger.info("🎉 All chat tables successfully created!")
        else:
            logger.warning(f"⚠️  Expected 3 tables, found {len(tables)}")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 