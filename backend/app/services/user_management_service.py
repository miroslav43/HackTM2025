"""
User management service for profile updates, admin functions, and user administration.
Handles extended user operations beyond basic authentication.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, desc
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import UploadFile, HTTPException, status

from ..models.user import User, UserActivity
from ..models.auth_token import AuthToken
from ..schemas.user import UserUpdate, UserResponse, UserCreate
from ..schemas.common import PaginatedResponse
from ..core.security import get_password_hash, verify_password
from ..utils.file_handler import file_handler


class UserManagementService:
    """
    Service class for user management operations
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_profile(self, user_id: str) -> Optional[User]:
        """
        Get user profile by ID
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return None
        
        stmt = select(User).where(User.id == user_uuid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_user_profile(
        self, 
        user_id: str, 
        update_data: UserUpdate, 
        avatar_file: Optional[UploadFile] = None
    ) -> Optional[User]:
        """
        Update user profile information
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return None
        
        # Get current user
        current_user = await self.get_user_profile(user_id)
        if not current_user:
            return None
        
        # Prepare update data
        update_values = {}
        
        if update_data.first_name is not None:
            update_values["first_name"] = update_data.first_name
        
        if update_data.last_name is not None:
            update_values["last_name"] = update_data.last_name
        
        if update_data.phone is not None:
            update_values["phone"] = update_data.phone
        
        if update_data.address is not None:
            update_values["address"] = update_data.address
        
        if update_data.cnp is not None:
            update_values["cnp"] = update_data.cnp
        
        # Handle avatar upload
        if avatar_file:
            try:
                # Delete old avatar if exists
                if current_user.avatar:
                    file_handler.delete_file(current_user.avatar)
                
                # Save new avatar
                avatar_path, _ = await file_handler.save_avatar(avatar_file)
                update_values["avatar"] = avatar_path
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Avatar upload failed: {str(e)}"
                )
        
        if not update_values:
            return current_user
        
        # Update user
        update_values["updated_at"] = datetime.utcnow()
        
        stmt = (
            update(User)
            .where(User.id == user_uuid)
            .values(**update_values)
            .returning(User)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.scalar_one_or_none()
    
    async def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user password
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return False
        
        # Get current user
        user = await self.get_user_profile(user_id)
        if not user:
            return False
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        new_password_hash = get_password_hash(new_password)
        
        stmt = (
            update(User)
            .where(User.id == user_uuid)
            .values(
                password_hash=new_password_hash,
                updated_at=datetime.utcnow()
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate user account
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return False
        
        stmt = (
            update(User)
            .where(User.id == user_uuid)
            .values(
                is_active=False,
                updated_at=datetime.utcnow()
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def reactivate_user(self, user_id: str) -> bool:
        """
        Reactivate user account
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return False
        
        stmt = (
            update(User)
            .where(User.id == user_uuid)
            .values(
                is_active=True,
                updated_at=datetime.utcnow()
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    # === ADMIN FUNCTIONS ===
    
    async def get_all_users(
        self, 
        limit: int = 50, 
        offset: int = 0,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """
        Get all users with filtering (admin only)
        """
        # Build base query
        stmt = select(User)
        count_stmt = select(func.count(User.id))
        
        # Apply filters
        conditions = []
        
        if search:
            search_condition = or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
            conditions.append(search_condition)
        
        if role:
            conditions.append(User.role == role)
        
        if is_active is not None:
            conditions.append(User.is_active == is_active)
        
        # Apply conditions
        if conditions:
            where_clause = and_(*conditions)
            stmt = stmt.where(where_clause)
            count_stmt = count_stmt.where(where_clause)
        
        # Get total count
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        stmt = (
            stmt
            .order_by(desc(User.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        # Execute query
        result = await self.db.execute(stmt)
        users = list(result.scalars().all())
        
        return users, total
    
    async def create_user_by_admin(
        self, 
        user_data: UserCreate, 
        created_by_id: str
    ) -> User:
        """
        Create user by admin (bypass normal registration)
        """
        try:
            admin_uuid = UUID(created_by_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid admin ID"
            )
        
        # Check if email already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        password_hash = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role=user_data.role or "citizen",
            is_active=True,
            email_verified=True  # Admin-created users are auto-verified
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return db_user
    
    async def update_user_role(
        self, 
        user_id: str, 
        new_role: str, 
        updated_by_id: str
    ) -> Optional[User]:
        """
        Update user role (admin only)
        """
        try:
            user_uuid = UUID(user_id)
            admin_uuid = UUID(updated_by_id)
        except ValueError:
            return None
        
        stmt = (
            update(User)
            .where(User.id == user_uuid)
            .values(
                role=new_role,
                updated_at=datetime.utcnow()
            )
            .returning(User)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.scalar_one_or_none()
    
    async def delete_user(self, user_id: str, deleted_by_id: str) -> bool:
        """
        Permanently delete user (admin only)
        """
        try:
            user_uuid = UUID(user_id)
            admin_uuid = UUID(deleted_by_id)
        except ValueError:
            return False
        
        # Get user for cleanup
        user = await self.get_user_profile(user_id)
        if not user:
            return False
        
        # Delete avatar file if exists
        if user.avatar:
            file_handler.delete_file(user.avatar)
        
        # Delete user
        stmt = delete(User).where(User.id == user_uuid)
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    # === SESSION MANAGEMENT ===
    
    async def get_user_sessions(self, user_id: str) -> List[AuthToken]:
        """
        Get active sessions for user
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return []
        
        stmt = (
            select(AuthToken)
            .where(
                and_(
                    AuthToken.user_id == user_uuid,
                    AuthToken.revoked == False,
                    AuthToken.expires_at > datetime.utcnow()
                )
            )
            .order_by(desc(AuthToken.created_at))
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def revoke_user_session(self, user_id: str, token_id: str) -> bool:
        """
        Revoke specific user session
        """
        try:
            user_uuid = UUID(user_id)
            token_uuid = UUID(token_id)
        except ValueError:
            return False
        
        stmt = (
            update(AuthToken)
            .where(
                and_(
                    AuthToken.id == token_uuid,
                    AuthToken.user_id == user_uuid
                )
            )
            .values(revoked=True)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """
        Revoke all sessions for user
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return 0
        
        stmt = (
            update(AuthToken)
            .where(
                and_(
                    AuthToken.user_id == user_uuid,
                    AuthToken.revoked == False
                )
            )
            .values(revoked=True)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    # === UTILITY METHODS ===
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user statistics
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return {}
        
        user = await self.get_user_profile(user_id)
        if not user:
            return {}
        
        # Get activity count
        activity_stmt = select(func.count(UserActivity.id)).where(
            UserActivity.user_id == user_uuid
        )
        activity_result = await self.db.execute(activity_stmt)
        activity_count = activity_result.scalar() or 0
        
        # Get active sessions count
        sessions = await self.get_user_sessions(user_id)
        
        return {
            "user_id": str(user.id),
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "activity_count": activity_count,
            "active_sessions": len(sessions)
        } 