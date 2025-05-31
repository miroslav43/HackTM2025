"""
Dashboard schemas for statistics, activity tracking, and notifications.
Provides type-safe validation for dashboard-related endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SystemStatus(str, Enum):
    """System status enumeration"""
    ONLINE = "online"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class ActivityType(str, Enum):
    """Activity type enumeration"""
    DOCUMENT_UPLOAD = "document_upload"
    VERIFICATION_COMPLETE = "verification_complete"
    REQUEST_SUBMITTED = "request_submitted"
    PROFILE_UPDATED = "profile_updated"
    LOGIN = "login"
    LOGOUT = "logout"


class ActivityStatus(str, Enum):
    """Activity status enumeration"""
    SUCCESS = "success"
    PENDING = "pending"
    ERROR = "error"


class NotificationType(str, Enum):
    """Notification type enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class DashboardStatsResponse(BaseModel):
    """Schema for dashboard statistics"""
    total_documents: int
    pending_verifications: int
    completed_requests: int
    system_status: SystemStatus
    total_users: Optional[int] = None
    archive_documents: Optional[int] = None

    class Config:
        from_attributes = True


class ActivityItemResponse(BaseModel):
    """Schema for activity item"""
    id: str
    user_id: str
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """Schema for creating notifications"""
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserActivityLog(BaseModel):
    """Schema for logging user activity"""
    action: str = Field(..., min_length=1, max_length=255)
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None 