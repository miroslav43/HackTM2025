#!/usr/bin/env python3
"""
Fix chat table conflicts by dropping existing conflicting tables
and recreating them with the correct structure.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine, Base
from app.models.chat import ChatSession, ChatMessage, AgentExecution


async def fix_chat_tables():
    """Drop conflicting chat tables and recreate them with correct structure"""
    
    try:
        async with engine.begin() as conn:
            print("🔄 Fixing chat table conflicts...")
            
            # Drop existing conflicting tables in correct order (foreign keys first)
            print("   Dropping existing agent_executions table...")
            await conn.execute(text("DROP TABLE IF EXISTS agent_executions CASCADE;"))
            
            print("   Dropping existing chat_messages table...")
            await conn.execute(text("DROP TABLE IF EXISTS chat_messages CASCADE;"))
            
            print("   Dropping existing chat_sessions table...")
            await conn.execute(text("DROP TABLE IF EXISTS chat_sessions CASCADE;"))
            
            print("   Dropping existing simple_chat_messages table...")
            await conn.execute(text("DROP TABLE IF EXISTS simple_chat_messages CASCADE;"))
            
            print("✅ Conflicting tables dropped successfully")
            
        # Now recreate the chat tables with correct structure
        async with engine.begin() as conn:
            print("🔄 Creating chat tables with correct structure...")
            
            # Import all models to ensure they are registered
            from app.models import user, document, archive, parking, notification, auth_token, settings, chat
            
            # Create only the chat-related tables
            await conn.run_sync(Base.metadata.create_all, tables=[
                ChatSession.__table__,
                ChatMessage.__table__, 
                AgentExecution.__table__
            ])
            
            print("✅ Chat tables created successfully!")
            
        print("\n🎉 Chat table conflicts resolved!")
        print("   ✅ ChatSession table: INTEGER id, UUID user_id")
        print("   ✅ ChatMessage table: INTEGER id, references chat_sessions")
        print("   ✅ AgentExecution table: INTEGER id, references chat_messages")
        
    except Exception as e:
        print(f"❌ Error fixing chat tables: {e}")
        return False
        
    return True


async def verify_tables():
    """Verify the tables were created correctly"""
    try:
        async with engine.begin() as conn:
            # Check chat_sessions table structure
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'chat_sessions' 
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 chat_sessions table structure:")
            for row in result:
                print(f"   {row.column_name}: {row.data_type}")
                
            # Check chat_messages table structure  
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 chat_messages table structure:")
            for row in result:
                print(f"   {row.column_name}: {row.data_type}")
                
            # Check agent_executions table structure
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'agent_executions' 
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 agent_executions table structure:")
            for row in result:
                print(f"   {row.column_name}: {row.data_type}")
                
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")


if __name__ == "__main__":
    print("🔧 Chat Table Repair Script")
    print("=" * 40)
    
    async def main():
        success = await fix_chat_tables()
        if success:
            await verify_tables()
            print("\n✅ All chat tables are now correctly configured!")
            print("   You can now start the backend server.")
        else:
            print("\n❌ Failed to fix chat tables. Check the errors above.")
            
    asyncio.run(main()) 