#!/usr/bin/env python3
"""
Script pentru adăugarea câmpului color la tabela document_categories
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Add the current directory to the path to import app modules
sys.path.append('.')

from app.db.database import get_db


async def add_color_column():
    """
    Adaugă câmpul color la tabela document_categories
    """
    async for db in get_db():
        try:
            # Check if column already exists
            check_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'document_categories' 
            AND column_name = 'color';
            """
            result = await db.execute(text(check_sql))
            exists = result.fetchone()
            
            if exists:
                print("✅ Column 'color' already exists in document_categories table")
                return
            
            # Add the color column
            add_column_sql = """
            ALTER TABLE document_categories 
            ADD COLUMN color VARCHAR(7) DEFAULT '#3B82F6';
            """
            await db.execute(text(add_column_sql))
            await db.commit()
            
            print("✅ Successfully added 'color' column to document_categories table")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error adding color column: {e}")
        break  # Only need one session


if __name__ == "__main__":
    print("🔄 Adding color column to document_categories...")
    asyncio.run(add_color_column())
    print("✅ Done!") 