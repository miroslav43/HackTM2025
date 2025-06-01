"""
Notification and activity models for user interactions.
Includes chat messages, system notifications, and requests.
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, CheckConstraint, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func, text

from ..db.database import Base


class SimpleChatMessage(Base):
    """
    Simple chat messages between users and basic assistant (legacy)
    Note: For AI Agent conversations, use ChatMessage from models.chat
    """
    __tablename__ = "simple_chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    session_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Add check constraint for role
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name='simple_chat_messages_role_check'),
    )


class SystemNotification(Base):
    """
    System notifications for users
    """
    __tablename__ = "system_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    read_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Add check constraint for type
    __table_args__ = (
        CheckConstraint("type IN ('info', 'warning', 'error', 'success')", name='system_notifications_type_check'),
    )


class Request(Base):
    """
    User requests for government services
    """
    __tablename__ = "requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), server_default="pending")
    priority = Column(String(20), server_default="normal")
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    documents = Column(JSONB)  # IDs of attached documents
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp())
    completed_at = Column(DateTime)
    
    # Add check constraints
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'in_progress', 'approved', 'rejected')", name='requests_status_check'),
        CheckConstraint("priority IN ('low', 'normal', 'high', 'urgent')", name='requests_priority_check'),
    )


# Note: UserActivity is defined in user.py to avoid duplication
# Note: UserSettings is defined in settings.py to avoid conflicts 