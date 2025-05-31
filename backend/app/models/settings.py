"""
User settings model for storing user preferences and configuration.
Supports flexible key-value storage with JSON values.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship

from ..db.database import Base


class UserSettings(Base):
    """
    User settings model for storing preferences and configuration
    """
    __tablename__ = "user_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(100), nullable=False)
    value = Column(JSONB, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships
    user = relationship("User")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'key', name='unique_user_setting'),
    )
    
    def __repr__(self):
        return f"<UserSettings(id={self.id}, user_id={self.user_id}, key={self.key})>" 