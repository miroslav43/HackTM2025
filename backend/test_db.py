#!/usr/bin/env python3
"""
Database connection test script
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.db.database import check_database_connection, create_tables

async def test_database():
    """Test database connection and table creation"""
    print("🔍 Testing database connection...")
    print(f"Database URL (masked): {settings.database_url.split('@')[0]}@****")
    
    # Test basic connection
    connection_ok = await check_database_connection()
    if connection_ok:
        print("✅ Database connection successful!")
        
        # Test table creation
        try:
            print("🔧 Testing table creation...")
            await create_tables()
            print("✅ Database tables created/verified successfully!")
            return True
        except Exception as e:
            print(f"❌ Table creation failed: {e}")
            return False
    else:
        print("❌ Database connection failed!")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_database())
    sys.exit(0 if result else 1) 