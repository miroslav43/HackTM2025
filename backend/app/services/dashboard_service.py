"""
Dashboard service for managing user dashboard data and statistics.
Handles activity logging, notifications, system metrics, and analytics.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, update, delete
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from ..models.user import User, UserActivity
from ..models.document import Document, ArchiveDocument
from ..models.notification import SystemNotification
from ..schemas.dashboard import (
    DashboardStatsResponse, ActivityItemResponse, NotificationCreate,
    NotificationResponse, UserActivityLog, SystemStatus, ActivityType
)


class DashboardService:
    """
    Service class for dashboard-related business logic
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_stats(self, user_id: str, is_official: bool = False) -> DashboardStatsResponse:
        """
        Get dashboard statistics for user or system-wide for officials
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        if is_official:
            # System-wide statistics for officials
            total_documents_stmt = select(func.count(Document.id))
            pending_verifications_stmt = select(func.count(Document.id)).where(
                Document.status == "pending"
            )
            total_users_stmt = select(func.count(User.id))
            archive_documents_stmt = select(func.count(ArchiveDocument.id))
            
            # Execute queries
            total_documents_result = await self.db.execute(total_documents_stmt)
            pending_result = await self.db.execute(pending_verifications_stmt)
            total_users_result = await self.db.execute(total_users_stmt)
            archive_result = await self.db.execute(archive_documents_stmt)
            
            total_documents = total_documents_result.scalar() or 0
            pending_verifications = pending_result.scalar() or 0
            total_users = total_users_result.scalar() or 0
            archive_documents = archive_result.scalar() or 0
            
            # Calculate completed requests (verified + rejected documents)
            completed_stmt = select(func.count(Document.id)).where(
                Document.status.in_(["verified", "rejected"])
            )
            completed_result = await self.db.execute(completed_stmt)
            completed_requests = completed_result.scalar() or 0
            
            return DashboardStatsResponse(
                total_documents=total_documents,
                pending_verifications=pending_verifications,
                completed_requests=completed_requests,
                system_status=SystemStatus.ONLINE,
                total_users=total_users,
                archive_documents=archive_documents
            )
        
        else:
            # User-specific statistics
            user_documents_stmt = select(func.count(Document.id)).where(
                Document.user_id == user_uuid
            )
            user_pending_stmt = select(func.count(Document.id)).where(
                and_(Document.user_id == user_uuid, Document.status == "pending")
            )
            user_completed_stmt = select(func.count(Document.id)).where(
                and_(Document.user_id == user_uuid, Document.status.in_(["verified", "rejected"]))
            )
            
            # Execute queries
            total_result = await self.db.execute(user_documents_stmt)
            pending_result = await self.db.execute(user_pending_stmt)
            completed_result = await self.db.execute(user_completed_stmt)
            
            total_documents = total_result.scalar() or 0
            pending_verifications = pending_result.scalar() or 0
            completed_requests = completed_result.scalar() or 0
            
            return DashboardStatsResponse(
                total_documents=total_documents,
                pending_verifications=pending_verifications,
                completed_requests=completed_requests,
                system_status=SystemStatus.ONLINE
            )
    
    async def log_user_activity(
        self, 
        user_id: str, 
        activity_data: UserActivityLog,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserActivity:
        """
        Log user activity for tracking and analytics
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        db_activity = UserActivity(
            user_id=user_uuid,
            action=activity_data.action,
            details=activity_data.details,
            ip_address=ip_address or activity_data.ip_address,
            user_agent=user_agent or activity_data.user_agent
        )
        
        self.db.add(db_activity)
        await self.db.commit()
        await self.db.refresh(db_activity)
        
        return db_activity
    
    async def get_user_activities(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[UserActivity]:
        """
        Get recent user activities
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return []
        
        stmt = (
            select(UserActivity)
            .where(UserActivity.user_id == user_uuid)
            .order_by(desc(UserActivity.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_system_activities(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[UserActivity]:
        """
        Get system-wide activities (for officials)
        """
        stmt = (
            select(UserActivity)
            .order_by(desc(UserActivity.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    # === NOTIFICATIONS ===
    
    async def create_notification(
        self, 
        user_id: str, 
        notification_data: NotificationCreate
    ) -> SystemNotification:
        """
        Create a new notification for a user
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        db_notification = SystemNotification(
            user_id=user_uuid,
            type=notification_data.type.value,
            title=notification_data.title,
            message=notification_data.message
        )
        
        self.db.add(db_notification)
        await self.db.commit()
        await self.db.refresh(db_notification)
        
        return db_notification
    
    async def get_user_notifications(
        self, 
        user_id: str, 
        unread_only: bool = False,
        limit: int = 50, 
        offset: int = 0
    ) -> List[SystemNotification]:
        """
        Get notifications for a specific user
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return []
        
        stmt = select(SystemNotification).where(SystemNotification.user_id == user_uuid)
        
        if unread_only:
            stmt = stmt.where(SystemNotification.read_at.is_(None))
        
        stmt = (
            stmt
            .order_by(desc(SystemNotification.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark a notification as read
        """
        try:
            notif_uuid = UUID(notification_id)
            user_uuid = UUID(user_id)
        except ValueError:
            return False
        
        stmt = (
            update(SystemNotification)
            .where(
                and_(
                    SystemNotification.id == notif_uuid,
                    SystemNotification.user_id == user_uuid
                )
            )
            .values(read_at=datetime.utcnow())
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def mark_all_notifications_read(self, user_id: str) -> int:
        """
        Mark all notifications as read for a user
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return 0
        
        stmt = (
            update(SystemNotification)
            .where(
                and_(
                    SystemNotification.user_id == user_uuid,
                    SystemNotification.read_at.is_(None)
                )
            )
            .values(read_at=datetime.utcnow())
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """
        Delete a notification
        """
        try:
            notif_uuid = UUID(notification_id)
            user_uuid = UUID(user_id)
        except ValueError:
            return False
        
        stmt = delete(SystemNotification).where(
            and_(
                SystemNotification.id == notif_uuid,
                SystemNotification.user_id == user_uuid
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def get_notification_count(self, user_id: str, unread_only: bool = True) -> int:
        """
        Get notification count for a user
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return 0
        
        stmt = select(func.count(SystemNotification.id)).where(
            SystemNotification.user_id == user_uuid
        )
        
        if unread_only:
            stmt = stmt.where(SystemNotification.read_at.is_(None))
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    # === ANALYTICS ===
    
    async def get_activity_analytics(
        self, 
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get activity analytics for user or system-wide
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(UserActivity).where(UserActivity.created_at >= start_date)
        
        if user_id:
            try:
                user_uuid = UUID(user_id)
                stmt = stmt.where(UserActivity.user_id == user_uuid)
            except ValueError:
                pass
        
        result = await self.db.execute(stmt)
        activities = result.scalars().all()
        
        # Analyze activities
        action_counts = {}
        daily_counts = {}
        
        for activity in activities:
            # Count by action
            action = activity.action
            action_counts[action] = action_counts.get(action, 0) + 1
            
            # Count by day
            day = activity.created_at.date().isoformat()
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        return {
            "total_activities": len(activities),
            "action_breakdown": action_counts,
            "daily_activity": daily_counts,
            "period_days": days
        } 