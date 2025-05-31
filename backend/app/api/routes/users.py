"""
User management API routes.
Handles profile updates, admin functions, and user administration.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from ...db.database import get_db
from ...services.user_management_service import UserManagementService
from ...schemas.user import UserUpdate, UserResponse, UserCreate
from ...schemas.common import SuccessResponse, PaginatedResponse
from ...core.dependencies import get_current_user, require_official
from ...models.user import User
from ...utils.file_handler import file_handler

router = APIRouter()


class PasswordChangeRequest(BaseModel):
    """Schema for password change request"""
    current_password: str
    new_password: str


class RoleUpdateRequest(BaseModel):
    """Schema for role update request"""
    new_role: str


# === PROFILE MANAGEMENT ===

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user profile
    """
    user_service = UserManagementService(db)
    
    user = await user_service.get_user_profile(str(current_user.id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile
    """
    user_service = UserManagementService(db)
    
    updated_user = await user_service.update_user_profile(
        str(current_user.id),
        update_data
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile update failed"
        )
    
    return UserResponse.model_validate(updated_user)


@router.post("/profile/avatar", response_model=UserResponse)
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload user avatar
    """
    user_service = UserManagementService(db)
    
    # Create empty update data for avatar-only update
    update_data = UserUpdate()
    
    updated_user = await user_service.update_user_profile(
        str(current_user.id),
        update_data,
        avatar_file=avatar
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar upload failed"
        )
    
    return UserResponse.model_validate(updated_user)


@router.get("/profile/avatar")
async def get_user_avatar(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user avatar file
    """
    if not current_user.avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found"
        )
    
    # Check if file exists
    file_info = file_handler.get_file_info(current_user.avatar)
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar file not found"
        )
    
    return FileResponse(
        path=current_user.avatar,
        media_type="image/jpeg"
    )


@router.put("/profile/password", response_model=SuccessResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    """
    user_service = UserManagementService(db)
    
    try:
        success = await user_service.change_password(
            str(current_user.id),
            password_data.current_password,
            password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password change failed"
            )
        
        return SuccessResponse(message="Password changed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )


@router.delete("/profile", response_model=SuccessResponse)
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate current user account
    """
    user_service = UserManagementService(db)
    
    success = await user_service.deactivate_user(str(current_user.id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deactivation failed"
        )
    
    return SuccessResponse(message="Account deactivated successfully")


# === SESSION MANAGEMENT ===

@router.get("/sessions", response_model=List[dict])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user active sessions
    """
    user_service = UserManagementService(db)
    
    sessions = await user_service.get_user_sessions(str(current_user.id))
    
    return [
        {
            "id": str(session.id),
            "created_at": session.created_at,
            "expires_at": session.expires_at,
            "is_current": session.token == getattr(current_user, '_token', None)
        }
        for session in sessions
    ]


@router.delete("/sessions/{session_id}", response_model=SuccessResponse)
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke a specific session
    """
    user_service = UserManagementService(db)
    
    success = await user_service.revoke_user_session(
        str(current_user.id),
        session_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return SuccessResponse(message="Session revoked successfully")


@router.delete("/sessions", response_model=SuccessResponse)
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke all user sessions (logout from all devices)
    """
    user_service = UserManagementService(db)
    
    count = await user_service.revoke_all_user_sessions(str(current_user.id))
    
    return SuccessResponse(message=f"Revoked {count} sessions successfully")


# === ADMIN FUNCTIONS ===

@router.get("/", response_model=PaginatedResponse[UserResponse])
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users with filtering (officials only)
    """
    user_service = UserManagementService(db)
    
    offset = (page - 1) * limit
    users, total = await user_service.get_all_users(
        limit=limit,
        offset=offset,
        search=search,
        role=role,
        is_active=is_active
    )
    
    # Calculate pagination info
    pages = (total + limit - 1) // limit
    has_next = page < pages
    has_prev = page > 1
    
    return PaginatedResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (officials only)
    """
    user_service = UserManagementService(db)
    
    user = await user_service.get_user_profile(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    user_data: UserCreate,
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Create user by admin (officials only)
    """
    user_service = UserManagementService(db)
    
    try:
        new_user = await user_service.create_user_by_admin(
            user_data,
            str(current_user.id)
        )
        
        return UserResponse.model_validate(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User creation failed: {str(e)}"
        )


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_data: RoleUpdateRequest,
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user role (officials only)
    """
    user_service = UserManagementService(db)
    
    updated_user = await user_service.update_user_role(
        user_id,
        role_data.new_role,
        str(current_user.id)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(updated_user)


@router.put("/{user_id}/deactivate", response_model=SuccessResponse)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate user account (officials only)
    """
    user_service = UserManagementService(db)
    
    success = await user_service.deactivate_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(message="User deactivated successfully")


@router.put("/{user_id}/reactivate", response_model=SuccessResponse)
async def reactivate_user(
    user_id: str,
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Reactivate user account (officials only)
    """
    user_service = UserManagementService(db)
    
    success = await user_service.reactivate_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(message="User reactivated successfully")


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Permanently delete user (officials only)
    """
    user_service = UserManagementService(db)
    
    success = await user_service.delete_user(
        user_id,
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(message="User deleted successfully")


@router.get("/{user_id}/statistics", response_model=dict)
async def get_user_statistics(
    user_id: str,
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive user statistics (officials only)
    """
    user_service = UserManagementService(db)
    
    stats = await user_service.get_user_statistics(user_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return stats 