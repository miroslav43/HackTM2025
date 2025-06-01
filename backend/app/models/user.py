"""
User model for authentication and profile management.
Supports citizen and official roles with profile data and activity tracking.
"""

from sqlalchemy import Column, String, DateTime, Text, CheckConstraint, Boolean, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
import uuid
from enum import Enum

from ..db.database import Base


class UserRole(str, Enum):
    """User role enumeration"""
    CITIZEN = "citizen"
    OFFICIAL = "official"


class User(Base):
    """
    User model for authentication and profile management
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="citizen")
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    date_of_birth = Column(Date)
    cnp = Column(String(13))  # Romanian personal numeric code
    avatar = Column(Text)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Add check constraint for role
    __table_args__ = (
        CheckConstraint("role IN ('citizen', 'official')", name='users_role_check'),
    )
    
    # Add this relationship to existing relationships section
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class UserActivity(Base):
    """
    User activity tracking model
    """
    __tablename__ = "user_activity"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    details = Column(Text)
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, action={self.action})>" 