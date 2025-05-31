"""
Dashboard API routes.
Handles dashboard statistics, activity tracking, and notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...db.database import get_db
from ...services.dashboard_service import DashboardService
from ...schemas.dashboard import (
    DashboardStatsResponse, ActivityItemResponse, NotificationCreate,
    NotificationResponse, UserActivityLog
)
from ...schemas.common import SuccessResponse, PaginatedResponse
from ...core.dependencies import get_current_user, require_official
from ...models.user import User

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard statistics
    """
    dashboard_service = DashboardService(db)
    
    is_official = current_user.role == "official"
    
    stats = await dashboard_service.get_dashboard_stats(
        str(current_user.id), 
        is_official=is_official
    )
    
    return stats


@router.post("/activity/log", response_model=SuccessResponse)
async def log_activity(
    activity_data: UserActivityLog,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Log user activity
    """
    dashboard_service = DashboardService(db)
    
    # Extract client info
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    await dashboard_service.log_user_activity(
        str(current_user.id),
        activity_data,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    return SuccessResponse(message="Activity logged successfully")


@router.get("/activity", response_model=List[ActivityItemResponse])
async def get_user_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user activities
    """
    dashboard_service = DashboardService(db)
    
    offset = (page - 1) * limit
    activities = await dashboard_service.get_user_activities(
        str(current_user.id),
        limit=limit,
        offset=offset
    )
    
    return [ActivityItemResponse.model_validate(activity) for activity in activities]


@router.get("/activity/system", response_model=List[ActivityItemResponse])
async def get_system_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system-wide activities (officials only)
    """
    dashboard_service = DashboardService(db)
    
    offset = (page - 1) * limit
    activities = await dashboard_service.get_system_activities(
        limit=limit,
        offset=offset
    )
    
    return [ActivityItemResponse.model_validate(activity) for activity in activities]


@router.get("/analytics", response_model=dict)
async def get_activity_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get activity analytics for charts
    """
    dashboard_service = DashboardService(db)
    
    # Officials can see system analytics, users see only their own
    user_id = None if current_user.role == "official" else str(current_user.id)
    
    analytics = await dashboard_service.get_activity_analytics(
        user_id=user_id,
        days=days
    )
    
    return analytics


# === NOTIFICATIONS ===

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user notifications
    """
    dashboard_service = DashboardService(db)
    
    offset = (page - 1) * limit
    notifications = await dashboard_service.get_user_notifications(
        str(current_user.id),
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    return [NotificationResponse.model_validate(notif) for notif in notifications]


@router.get("/notifications/count", response_model=dict)
async def get_notification_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get notification counts
    """
    dashboard_service = DashboardService(db)
    
    unread_count = await dashboard_service.get_notification_count(
        str(current_user.id), 
        unread_only=True
    )
    total_count = await dashboard_service.get_notification_count(
        str(current_user.id), 
        unread_only=False
    )
    
    return {
        "unread": unread_count,
        "total": total_count
    }


@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    target_user_id: str = Query(...),
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a notification for a user (officials only)
    """
    dashboard_service = DashboardService(db)
    
    notification = await dashboard_service.create_notification(
        target_user_id,
        notification_data
    )
    
    return NotificationResponse.model_validate(notification)


@router.put("/notifications/{notification_id}/read", response_model=SuccessResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a notification as read
    """
    dashboard_service = DashboardService(db)
    
    success = await dashboard_service.mark_notification_read(
        notification_id,
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return SuccessResponse(message="Notification marked as read")


@router.put("/notifications/read-all", response_model=SuccessResponse)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark all notifications as read
    """
    dashboard_service = DashboardService(db)
    
    count = await dashboard_service.mark_all_notifications_read(str(current_user.id))
    
    return SuccessResponse(message=f"Marked {count} notifications as read")


@router.delete("/notifications/{notification_id}", response_model=SuccessResponse)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a notification
    """
    dashboard_service = DashboardService(db)
    
    success = await dashboard_service.delete_notification(
        notification_id,
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return SuccessResponse(message="Notification deleted successfully") 