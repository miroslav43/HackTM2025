#!/usr/bin/env python3
"""
Migration script to add OCR-related columns to document_analysis table.
This adds the missing columns for the OCR integration feature.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import logging

# Import app config
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    """Add OCR-related columns to document_analysis table."""
    
    # Use the app's database configuration
    database_url = settings.database_url
    
    # Configure SSL for cloud databases
    connect_args = {}
    if "neon.tech" in database_url or "sslmode=require" in database_url:
        connect_args = {
            "ssl": True,
            "server_settings": {
                "application_name": "romanian_admin_platform",
            }
        }
    
    logger.info(f"Connecting to database: {database_url.split('@')[0]}@****")
    
    engine = create_async_engine(
        database_url,
        connect_args=connect_args,
        pool_size=1,  # Small pool for migration
        max_overflow=0
    )
    
    try:
        async with engine.begin() as conn:
            logger.info("Starting migration: Adding OCR columns to document_analysis table")
            
            # Check if columns already exist
            check_columns_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'document_analysis' 
            AND column_name IN ('confidence_score', 'transcribed_text', 'processing_method');
            """
            
            result = await conn.execute(text(check_columns_sql))
            existing_columns = [row[0] for row in result.fetchall()]
            
            logger.info(f"Existing OCR columns: {existing_columns}")
            
            # Add missing columns
            migrations = []
            
            if 'confidence_score' not in existing_columns:
                migrations.append(
                    "ALTER TABLE document_analysis ADD COLUMN confidence_score VARCHAR;"
                )
                logger.info("Will add confidence_score column")
            
            if 'transcribed_text' not in existing_columns:
                migrations.append(
                    "ALTER TABLE document_analysis ADD COLUMN transcribed_text TEXT;"
                )
                logger.info("Will add transcribed_text column")
            
            if 'processing_method' not in existing_columns:
                migrations.append(
                    "ALTER TABLE document_analysis ADD COLUMN processing_method VARCHAR(50) DEFAULT 'gemini_ocr';"
                )
                logger.info("Will add processing_method column")
            
            # Execute migrations
            for migration_sql in migrations:
                logger.info(f"Executing: {migration_sql}")
                await conn.execute(text(migration_sql))
            
            if migrations:
                logger.info(f"Successfully added {len(migrations)} columns to document_analysis table")
                logger.info("Migration completed successfully!")
            else:
                logger.info("All OCR columns already exist, no migration needed")
                
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration()) 