"""
Pydantic schemas for AI Agent Chat functionality
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid


class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message"""
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: int
    session_id: int
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    processing_time: Optional[int] = None
    tools_used: Optional[List[str]] = None
    agent_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session"""
    title: Optional[str] = None


class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session"""
    title: Optional[str] = None
    is_archived: Optional[bool] = None


class ChatSessionResponse(BaseModel):
    """Schema for chat session response"""
    id: int
    user_id: Union[str, uuid.UUID]  # Accept both string and UUID
    title: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    is_archived: bool
    message_count: Optional[int] = 0
    last_message_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSessionResponse):
    """Schema for chat session with messages"""
    messages: List[ChatMessageResponse] = []


class AgentConfigRequest(BaseModel):
    """Schema for agent configuration request"""
    query_processing: Optional[Dict[str, Any]] = None
    timpark_payment: Optional[Dict[str, Any]] = None
    web_search: Optional[Dict[str, Any]] = None
    trusted_sites_search: Optional[Dict[str, Any]] = None
    final_response_generation: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None


class AgentExecutionResponse(BaseModel):
    """Schema for agent execution response"""
    id: int
    message_id: int
    original_question: str
    reformulated_query: Optional[str]
    config_used: Dict[str, Any]
    execution_time: Optional[int]
    tools_executed: Optional[List[str]]
    workflow_stopped_early: bool
    timpark_result: Optional[Dict[str, Any]]
    web_search_result: Optional[str]
    trusted_sites_result: Optional[Dict[str, Any]]
    final_response: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for sending a chat message with optional configuration"""
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[int] = None
    agent_config: Optional[AgentConfigRequest] = None
    create_new_session: bool = False


class ChatResponse(BaseModel):
    """Schema for chat response"""
    message: ChatMessageResponse
    session: ChatSessionResponse
    agent_execution: Optional[AgentExecutionResponse] = None 