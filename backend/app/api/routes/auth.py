"""
Authentication API routes.
Handles user registration, login, token refresh, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from pydantic import BaseModel

from ...db.database import get_db
from ...services.user_service import UserService
from ...schemas.user import UserCreate, UserLogin, UserResponse, UserProfile
from ...core.security import create_access_token, create_refresh_token, verify_token
from ...core.dependencies import get_current_user
from ...models.user import User

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account
    """
    try:
        user_service = UserService(db)
        
        # Create user
        user = await user_service.create_user(user_data)
        
        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Create response
        user_response = UserResponse.model_validate(user)
        
        return {
            "message": "User registered successfully",
            "user": user_response,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException as e:
        logger.error(f"HTTP error during registration: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=dict)
async def login_user(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user with email and password
    """
    try:
        user_service = UserService(db)
        
        # Authenticate user
        user = await user_service.authenticate_user(
            credentials.email, 
            credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Create response
        user_response = UserResponse.model_validate(user)
        
        return {
            "message": "Login successful",
            "user": user_response,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException as e:
        logger.error(f"HTTP error during login: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=dict)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user still exists
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile information
    """
    return UserProfile.model_validate(current_user)


@router.post("/logout", response_model=dict)
async def logout_user(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (in a full implementation, this would invalidate the token)
    """
    # In a production app, you would:
    # 1. Add token to blacklist
    # 2. Remove from active sessions
    # 3. Log the logout action
    
    return {
        "message": "Logout successful"
    } 