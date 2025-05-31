"""
Settings service for user preferences, security settings, and configuration management.
Handles user-specific settings and system configuration.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status

from ..models.user import User
from ..models.settings import UserSettings


class SettingsService:
    """
    Service class for settings management
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get all user settings as key-value pairs
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return {}
        
        stmt = select(UserSettings).where(UserSettings.user_id == user_uuid)
        result = await self.db.execute(stmt)
        settings = list(result.scalars().all())
        
        # Convert to dictionary
        settings_dict = {}
        for setting in settings:
            settings_dict[setting.setting_key] = setting.setting_value
        
        return settings_dict
    
    async def get_user_setting(self, user_id: str, key: str) -> Optional[str]:
        """
        Get a specific user setting by key
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return None
        
        stmt = select(UserSettings).where(
            and_(
                UserSettings.user_id == user_uuid,
                UserSettings.setting_key == key
            )
        )
        result = await self.db.execute(stmt)
        setting = result.scalar_one_or_none()
        
        return setting.setting_value if setting else None
    
    async def set_user_setting(
        self, 
        user_id: str, 
        key: str, 
        value: str
    ) -> bool:
        """
        Set or update a user setting
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return False
        
        # Check if setting already exists
        existing_setting = await self.get_user_setting(user_id, key)
        
        if existing_setting is not None:
            # Update existing setting
            stmt = (
                update(UserSettings)
                .where(
                    and_(
                        UserSettings.user_id == user_uuid,
                        UserSettings.setting_key == key
                    )
                )
                .values(
                    setting_value=value,
                    updated_at=datetime.utcnow()
                )
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            return result.rowcount > 0
        
        else:
            # Create new setting
            new_setting = UserSettings(
                user_id=user_uuid,
                setting_key=key,
                setting_value=value
            )
            
            self.db.add(new_setting)
            await self.db.commit()
            return True
    
    async def delete_user_setting(self, user_id: str, key: str) -> bool:
        """
        Delete a user setting
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return False
        
        stmt = delete(UserSettings).where(
            and_(
                UserSettings.user_id == user_uuid,
                UserSettings.setting_key == key
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def set_multiple_settings(
        self, 
        user_id: str, 
        settings: Dict[str, str]
    ) -> int:
        """
        Set multiple user settings at once
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return 0
        
        updated_count = 0
        
        for key, value in settings.items():
            success = await self.set_user_setting(user_id, key, value)
            if success:
                updated_count += 1
        
        return updated_count
    
    async def delete_all_user_settings(self, user_id: str) -> int:
        """
        Delete all settings for a user
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return 0
        
        stmt = delete(UserSettings).where(UserSettings.user_id == user_uuid)
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    # === PREDEFINED SETTING HELPERS ===
    
    async def get_notification_settings(self, user_id: str) -> Dict[str, bool]:
        """
        Get notification-related settings
        """
        settings = await self.get_user_settings(user_id)
        
        return {
            "email_notifications": settings.get("email_notifications", "true").lower() == "true",
            "document_updates": settings.get("document_updates", "true").lower() == "true",
            "verification_alerts": settings.get("verification_alerts", "true").lower() == "true",
            "system_announcements": settings.get("system_announcements", "true").lower() == "true",
            "security_alerts": settings.get("security_alerts", "true").lower() == "true"
        }
    
    async def set_notification_settings(
        self, 
        user_id: str, 
        settings: Dict[str, bool]
    ) -> bool:
        """
        Update notification settings
        """
        string_settings = {
            key: "true" if value else "false" 
            for key, value in settings.items()
        }
        
        updated = await self.set_multiple_settings(user_id, string_settings)
        return updated > 0
    
    async def get_privacy_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get privacy-related settings
        """
        settings = await self.get_user_settings(user_id)
        
        return {
            "profile_visible": settings.get("profile_visible", "true").lower() == "true",
            "activity_tracking": settings.get("activity_tracking", "true").lower() == "true",
            "data_sharing": settings.get("data_sharing", "false").lower() == "true",
            "analytics_opt_in": settings.get("analytics_opt_in", "false").lower() == "true"
        }
    
    async def set_privacy_settings(
        self, 
        user_id: str, 
        settings: Dict[str, bool]
    ) -> bool:
        """
        Update privacy settings
        """
        string_settings = {
            key: "true" if value else "false" 
            for key, value in settings.items()
        }
        
        updated = await self.set_multiple_settings(user_id, string_settings)
        return updated > 0
    
    async def get_ui_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get UI/UX preferences
        """
        settings = await self.get_user_settings(user_id)
        
        return {
            "theme": settings.get("theme", "light"),
            "language": settings.get("language", "ro"),
            "timezone": settings.get("timezone", "Europe/Bucharest"),
            "date_format": settings.get("date_format", "DD/MM/YYYY"),
            "items_per_page": int(settings.get("items_per_page", "20")),
            "compact_view": settings.get("compact_view", "false").lower() == "true"
        }
    
    async def set_ui_preferences(
        self, 
        user_id: str, 
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Update UI preferences
        """
        # Convert all values to strings
        string_settings = {}
        for key, value in preferences.items():
            if isinstance(value, bool):
                string_settings[key] = "true" if value else "false"
            else:
                string_settings[key] = str(value)
        
        updated = await self.set_multiple_settings(user_id, string_settings)
        return updated > 0
    
    async def get_security_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get security-related settings
        """
        settings = await self.get_user_settings(user_id)
        
        return {
            "two_factor_enabled": settings.get("two_factor_enabled", "false").lower() == "true",
            "login_notifications": settings.get("login_notifications", "true").lower() == "true",
            "session_timeout": int(settings.get("session_timeout", "3600")),  # 1 hour default
            "password_expiry_days": int(settings.get("password_expiry_days", "90")),
            "device_tracking": settings.get("device_tracking", "true").lower() == "true"
        }
    
    async def set_security_settings(
        self, 
        user_id: str, 
        settings: Dict[str, Any]
    ) -> bool:
        """
        Update security settings
        """
        # Convert all values to strings
        string_settings = {}
        for key, value in settings.items():
            if isinstance(value, bool):
                string_settings[key] = "true" if value else "false"
            else:
                string_settings[key] = str(value)
        
        updated = await self.set_multiple_settings(user_id, string_settings)
        return updated > 0
    
    # === SYSTEM-WIDE SETTINGS (Admin only) ===
    
    async def get_system_settings(self) -> Dict[str, Any]:
        """
        Get system-wide settings (for admin users)
        """
        # System settings are stored with user_id as NULL or a special system UUID
        # For now, we'll return default system settings
        return {
            "maintenance_mode": False,
            "max_file_size": "50MB",
            "allowed_file_types": ["pdf", "doc", "docx", "jpg", "png"],
            "registration_enabled": True,
            "email_verification_required": True,
            "max_login_attempts": 5,
            "session_timeout_hours": 24,
            "backup_frequency_hours": 6
        }
    
    async def export_user_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user settings for backup/migration
        """
        settings = await self.get_user_settings(user_id)
        
        return {
            "user_id": user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "settings": settings,
            "organized_settings": {
                "notifications": await self.get_notification_settings(user_id),
                "privacy": await self.get_privacy_settings(user_id),
                "ui_preferences": await self.get_ui_preferences(user_id),
                "security": await self.get_security_settings(user_id)
            }
        }
    
    async def import_user_settings(
        self, 
        user_id: str, 
        settings_data: Dict[str, Any]
    ) -> bool:
        """
        Import user settings from backup/migration data
        """
        if "settings" not in settings_data:
            return False
        
        settings = settings_data["settings"]
        
        # Clear existing settings first
        await self.delete_all_user_settings(user_id)
        
        # Import new settings
        updated = await self.set_multiple_settings(user_id, settings)
        
        return updated > 0 