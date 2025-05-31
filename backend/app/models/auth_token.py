"""
Authentication token model for session management.
Tracks JWT tokens, refresh tokens, and user sessions.
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from ..db.database import Base


class AuthToken(Base):
    """
    Authentication token model for JWT session management
    """
    __tablename__ = "auth_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(Text, nullable=False, unique=True, index=True)
    token_type = Column(String(20), nullable=False, default="access")  # access, refresh
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    
    # Session tracking
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(Text)
    device_info = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.current_timestamp())
    revoked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuthToken(id={self.id}, user_id={self.user_id}, type={self.token_type}, revoked={self.revoked})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not revoked and not expired)"""
        return not self.revoked and not self.is_expired 