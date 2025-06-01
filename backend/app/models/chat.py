"""
Chat models for AI Agent conversations
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class ChatSession(Base):
    """AI Agent chat session model"""
    __tablename__ = "chat_sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)  # Auto-generated or user-set title
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual chat message model"""
    __tablename__ = "chat_messages"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Agent-specific metadata
    agent_metadata = Column(JSON, nullable=True)  # Store agent config, tools used, etc.
    processing_time = Column(Integer, nullable=True)  # Processing time in milliseconds
    tools_used = Column(JSON, nullable=True)  # List of tools used for this response
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class AgentExecution(Base):
    """Track agent execution details and results"""
    __tablename__ = "agent_executions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=False)
    
    # Query details
    original_question = Column(Text, nullable=False)
    reformulated_query = Column(Text, nullable=True)
    
    # Agent configuration used
    config_used = Column(JSON, nullable=False)
    
    # Tool results
    timpark_result = Column(JSON, nullable=True)
    web_search_result = Column(Text, nullable=True)
    trusted_sites_result = Column(JSON, nullable=True)
    final_response = Column(Text, nullable=True)
    
    # Execution metadata
    execution_time = Column(Integer, nullable=True)  # Total execution time in milliseconds
    tools_executed = Column(JSON, nullable=True)  # List of tools that were actually executed
    workflow_stopped_early = Column(Boolean, default=False)  # If TimPark payment stopped workflow
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    message = relationship("ChatMessage") 