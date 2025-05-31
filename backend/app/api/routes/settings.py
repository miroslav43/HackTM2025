"""
Settings API routes.
Handles user preferences, security settings, and configuration management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ...db.database import get_db
from ...services.settings_service import SettingsService
from ...schemas.common import SuccessResponse
from ...core.dependencies import get_current_user, require_official
from ...models.user import User

router = APIRouter()


class SettingRequest(BaseModel):
    """Schema for setting single value"""
    key: str
    value: str


class SettingsRequest(BaseModel):
    """Schema for setting multiple values"""
    settings: Dict[str, str]


class NotificationSettingsRequest(BaseModel):
    """Schema for notification settings"""
    email_notifications: Optional[bool] = None
    document_updates: Optional[bool] = None
    verification_alerts: Optional[bool] = None
    system_announcements: Optional[bool] = None
    security_alerts: Optional[bool] = None


class PrivacySettingsRequest(BaseModel):
    """Schema for privacy settings"""
    profile_visible: Optional[bool] = None
    activity_tracking: Optional[bool] = None
    data_sharing: Optional[bool] = None
    analytics_opt_in: Optional[bool] = None


class UIPreferencesRequest(BaseModel):
    """Schema for UI preferences"""
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    items_per_page: Optional[int] = None
    compact_view: Optional[bool] = None


class SecuritySettingsRequest(BaseModel):
    """Schema for security settings"""
    two_factor_enabled: Optional[bool] = None
    login_notifications: Optional[bool] = None
    session_timeout: Optional[int] = None
    password_expiry_days: Optional[int] = None
    device_tracking: Optional[bool] = None


# === GENERAL SETTINGS ===

@router.get("/", response_model=Dict[str, str])
async def get_all_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all user settings
    """
    settings_service = SettingsService(db)
    
    settings = await settings_service.get_user_settings(str(current_user.id))
    
    return settings


@router.get("/{key}", response_model=Dict[str, str])
async def get_user_setting(
    key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific user setting
    """
    settings_service = SettingsService(db)
    
    value = await settings_service.get_user_setting(str(current_user.id), key)
    
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    return {key: value}


@router.put("/", response_model=SuccessResponse)
async def set_user_setting(
    setting_request: SettingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Set or update a user setting
    """
    settings_service = SettingsService(db)
    
    success = await settings_service.set_user_setting(
        str(current_user.id),
        setting_request.key,
        setting_request.value
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update setting"
        )
    
    return SuccessResponse(message="Setting updated successfully")


@router.put("/bulk", response_model=SuccessResponse)
async def set_multiple_settings(
    settings_request: SettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Set multiple user settings
    """
    settings_service = SettingsService(db)
    
    updated_count = await settings_service.set_multiple_settings(
        str(current_user.id),
        settings_request.settings
    )
    
    return SuccessResponse(
        message=f"Updated {updated_count} settings successfully"
    )


@router.delete("/{key}", response_model=SuccessResponse)
async def delete_user_setting(
    key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user setting
    """
    settings_service = SettingsService(db)
    
    success = await settings_service.delete_user_setting(str(current_user.id), key)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    return SuccessResponse(message="Setting deleted successfully")


@router.delete("/", response_model=SuccessResponse)
async def delete_all_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete all user settings
    """
    settings_service = SettingsService(db)
    
    deleted_count = await settings_service.delete_all_user_settings(str(current_user.id))
    
    return SuccessResponse(
        message=f"Deleted {deleted_count} settings successfully"
    )


# === NOTIFICATION SETTINGS ===

@router.get("/notifications", response_model=Dict[str, bool])
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get notification settings
    """
    settings_service = SettingsService(db)
    
    settings = await settings_service.get_notification_settings(str(current_user.id))
    
    return settings


@router.put("/notifications", response_model=SuccessResponse)
async def update_notification_settings(
    notification_settings: NotificationSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update notification settings
    """
    settings_service = SettingsService(db)
    
    # Convert to dict, excluding None values
    settings_dict = {
        k: v for k, v in notification_settings.model_dump().items() 
        if v is not None
    }
    
    if not settings_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No settings provided"
        )
    
    success = await settings_service.set_notification_settings(
        str(current_user.id),
        settings_dict
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update notification settings"
        )
    
    return SuccessResponse(message="Notification settings updated successfully")


# === PRIVACY SETTINGS ===

@router.get("/privacy", response_model=Dict[str, Any])
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get privacy settings
    """
    settings_service = SettingsService(db)
    
    settings = await settings_service.get_privacy_settings(str(current_user.id))
    
    return settings


@router.put("/privacy", response_model=SuccessResponse)
async def update_privacy_settings(
    privacy_settings: PrivacySettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update privacy settings
    """
    settings_service = SettingsService(db)
    
    # Convert to dict, excluding None values
    settings_dict = {
        k: v for k, v in privacy_settings.model_dump().items() 
        if v is not None
    }
    
    if not settings_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No settings provided"
        )
    
    success = await settings_service.set_privacy_settings(
        str(current_user.id),
        settings_dict
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update privacy settings"
        )
    
    return SuccessResponse(message="Privacy settings updated successfully")


# === UI PREFERENCES ===

@router.get("/ui", response_model=Dict[str, Any])
async def get_ui_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get UI preferences
    """
    settings_service = SettingsService(db)
    
    preferences = await settings_service.get_ui_preferences(str(current_user.id))
    
    return preferences


@router.put("/ui", response_model=SuccessResponse)
async def update_ui_preferences(
    ui_preferences: UIPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update UI preferences
    """
    settings_service = SettingsService(db)
    
    # Convert to dict, excluding None values
    preferences_dict = {
        k: v for k, v in ui_preferences.model_dump().items() 
        if v is not None
    }
    
    if not preferences_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No preferences provided"
        )
    
    success = await settings_service.set_ui_preferences(
        str(current_user.id),
        preferences_dict
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update UI preferences"
        )
    
    return SuccessResponse(message="UI preferences updated successfully")


# === SECURITY SETTINGS ===

@router.get("/security", response_model=Dict[str, Any])
async def get_security_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get security settings
    """
    settings_service = SettingsService(db)
    
    settings = await settings_service.get_security_settings(str(current_user.id))
    
    return settings


@router.put("/security", response_model=SuccessResponse)
async def update_security_settings(
    security_settings: SecuritySettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update security settings
    """
    settings_service = SettingsService(db)
    
    # Convert to dict, excluding None values
    settings_dict = {
        k: v for k, v in security_settings.model_dump().items() 
        if v is not None
    }
    
    if not settings_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No settings provided"
        )
    
    success = await settings_service.set_security_settings(
        str(current_user.id),
        settings_dict
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update security settings"
        )
    
    return SuccessResponse(message="Security settings updated successfully")


# === SYSTEM SETTINGS (Admin only) ===

@router.get("/system", response_model=Dict[str, Any])
async def get_system_settings(
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system-wide settings (officials only)
    """
    settings_service = SettingsService(db)
    
    settings = await settings_service.get_system_settings()
    
    return settings


# === IMPORT/EXPORT ===

@router.get("/export", response_model=Dict[str, Any])
async def export_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export all user settings
    """
    settings_service = SettingsService(db)
    
    export_data = await settings_service.export_user_settings(str(current_user.id))
    
    return export_data


@router.post("/import", response_model=SuccessResponse)
async def import_user_settings(
    settings_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Import user settings from export data
    """
    settings_service = SettingsService(db)
    
    success = await settings_service.import_user_settings(
        str(current_user.id),
        settings_data
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to import settings"
        )
    
    return SuccessResponse(message="Settings imported successfully") 