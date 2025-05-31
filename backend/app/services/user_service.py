"""
User service for business logic related to user management.
Handles user creation, authentication, profile updates, and queries.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from uuid import UUID
import asyncio

from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..core.security import get_password_hash, verify_password
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user-related business logic
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user account
        """
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        password_hash = get_password_hash(user_data.password)
        
        # Create user
        db_user = User(
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role=user_data.role or "citizen"
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        # Send welcome email asynchronously (don't wait for it)
        asyncio.create_task(self._send_welcome_email_async(db_user))
        
        return db_user
    
    async def _send_welcome_email_async(self, user: User):
        """Send welcome email asynchronously with timeout"""
        try:
            from ..utils.email_service import email_service
            user_name = f"{user.first_name} {user.last_name}".strip() or user.email
            
            # Add timeout to prevent hanging
            await asyncio.wait_for(
                email_service.send_welcome_email(
                    user_email=user.email,
                    user_name=user_name,
                    user_role=user.role
                ),
                timeout=5.0  # 5 second timeout
            )
            logger.info(f"Welcome email sent to {user.email}")
            
        except asyncio.TimeoutError:
            logger.warning(f"Email sending timed out for {user.email}")
        except Exception as e:
            # Log email error but don't affect the user creation
            logger.warning(f"Failed to send welcome email to {user.email}: {e}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        """
        try:
            uuid_obj = UUID(user_id)
        except ValueError:
            return None
            
        stmt = select(User).where(User.id == uuid_obj)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        """
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        Update user profile information
        """
        try:
            uuid_obj = UUID(user_id)
        except ValueError:
            return None
        
        # Create update dictionary with only provided fields
        update_data = {
            key: value 
            for key, value in user_data.model_dump().items() 
            if value is not None
        }
        
        if not update_data:
            # No fields to update, return current user
            return await self.get_user_by_id(user_id)
        
        stmt = (
            update(User)
            .where(User.id == uuid_obj)
            .values(**update_data)
            .returning(User)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.scalar_one_or_none()
    
    async def get_users_by_role(self, role: UserRole, limit: int = 100) -> List[User]:
        """
        Get users by role with pagination
        """
        stmt = (
            select(User)
            .where(User.role == role.value)
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Soft delete user (if needed) or hard delete
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        return True 