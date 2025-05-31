#!/usr/bin/env python3
"""
Script to add database indexes for better performance
"""

import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Add the app directory to Python path
sys.path.append('.')

from app.db.database import async_session_maker


async def add_performance_indexes():
    """Add indexes to improve query performance"""
    async with async_session_maker() as session:
        try:
            print("🔧 Adding database indexes for better performance...")
            
            # Index for archive_documents table
            indexes = [
                # Index for category_id lookups
                "CREATE INDEX IF NOT EXISTS idx_archive_docs_category_id ON archive_documents(category_id);",
                
                # Index for authority lookups
                "CREATE INDEX IF NOT EXISTS idx_archive_docs_authority ON archive_documents(authority);",
                
                # Index for created_at sorting (used in ORDER BY)
                "CREATE INDEX IF NOT EXISTS idx_archive_docs_created_at ON archive_documents(created_at DESC);",
                
                # Composite index for category + created_at (common query pattern)
                "CREATE INDEX IF NOT EXISTS idx_archive_docs_category_created ON archive_documents(category_id, created_at DESC);",
                
                # Index for document categories
                "CREATE INDEX IF NOT EXISTS idx_document_categories_name ON document_categories(name);",
                
                # Index for users table
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);"
            ]
            
            for index_sql in indexes:
                try:
                    print(f"Creating index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON')[0]}")
                    await session.execute(text(index_sql))
                    await session.commit()
                    print("✅ Index created successfully")
                except Exception as e:
                    print(f"⚠️  Index creation skipped: {str(e)}")
                    await session.rollback()
            
            print("🎯 Database indexes optimization complete!")
            
        except Exception as e:
            print(f"❌ Error adding indexes: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(add_performance_indexes()) 