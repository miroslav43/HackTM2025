"""
FastAPI dependencies for authentication and authorization.
Provides reusable dependency injection for route protection.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ..db.database import get_db
from ..models.user import User
from ..services.user_service import UserService
from .security import verify_token, SecurityException


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token and get payload
        payload = verify_token(credentials.credentials)
        
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
    
    except Exception:
        raise credentials_exception
    
    # Get user from database
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (non-disabled).
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: list[str]):
    """
    Dependency factory to require specific user roles.
    Usage: @app.get("/admin", dependencies=[Depends(require_role(["official"]))])
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


# Commonly used role dependencies
require_citizen = require_role(["citizen"])
require_official = require_role(["official"])
require_admin = require_role(["admin"])
require_citizen_or_official = require_role(["citizen", "official"])


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None
    Useful for endpoints that can work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        # Verify token and get payload
        payload = verify_token(credentials.credentials)
        
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
    
    except Exception:
        return None
    
    # Get user from database
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        return None
    
    return user 