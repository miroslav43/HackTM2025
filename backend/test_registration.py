#!/usr/bin/env python3
"""
Test script for user registration functionality
"""

import asyncio
import json
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.db.database import async_session_maker

async def test_registration():
    print('Testing user registration...')
    async with async_session_maker() as session:
        try:
            user_service = UserService(session)
            
            user_data = UserCreate(
                first_name='Test',
                last_name='User',
                email='test@example.com',
                password='testpassword123',
                role='citizen'
            )
            
            print(f'Creating user: {user_data.model_dump()}')
            user = await user_service.create_user(user_data)
            print(f'✅ User created successfully: {user.id}')
            
        except Exception as e:
            print(f'❌ Registration failed: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_registration()) 