#!/usr/bin/env python3
"""
Script to update a user's role to 'official' for testing purposes
"""

import asyncio
import sys
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

# Add the app directory to Python path
sys.path.append('.')

from app.db.database import async_session_maker
from app.models.user import User


async def update_user_role(email: str, role: str = "official"):
    """Update user role by email"""
    async with async_session_maker() as session:
        try:
            # Update user role
            stmt = (
                update(User)
                .where(User.email == email)
                .values(role=role)
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount > 0:
                print(f"✅ Updated user {email} role to {role}")
                return True
            else:
                print(f"❌ User {email} not found")
                return False
                
        except Exception as e:
            await session.rollback()
            print(f"❌ Error updating user role: {e}")
            return False


async def main():
    """Main function"""
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "admin@test.com"
    
    success = await update_user_role(email)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 