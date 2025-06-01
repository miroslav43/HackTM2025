"""
AI Agent API routes - Romanian Civic Information Assistant
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, AgentExecution
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatSessionCreate, ChatSessionUpdate,
    ChatSessionResponse, ChatSessionWithMessages, ChatMessageResponse,
    AgentConfigRequest, AgentExecutionResponse
)
from app.services.chat_service import ChatService
from app.services.agent_service import agent_service
from app.core.dependencies import get_current_user
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to the AI Agent and get a response
    
    This endpoint processes user messages through the Romanian Civic Information Assistant
    which uses multiple tools including query reformulation, TimPark payment automation,
    web search, trusted government sites search, and final response synthesis.
    """
    try:
        # Convert agent config to dict if provided
        agent_config_dict = None
        if request.agent_config:
            agent_config_dict = request.agent_config.dict(exclude_unset=True)
        
        # Process the message with the chat service
        result = await ChatService.process_user_message(
            db=db,
            user_id=current_user.id,
            message_content=request.message,
            session_id=request.session_id,
            agent_config=agent_config_dict,
            create_new_session=request.create_new_session
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process message: {result.get('error', 'Unknown error')}"
            )
        
        # Build response
        session_response = ChatSessionResponse.from_orm(result["session"])
        message_response = ChatMessageResponse.from_orm(result["agent_message"])
        
        agent_execution_response = None
        if result["agent_execution"]:
            agent_execution_response = AgentExecutionResponse.from_orm(result["agent_execution"])
        
        return ChatResponse(
            message=message_response,
            session=session_response,
            agent_execution=agent_execution_response
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/chat/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    include_archived: bool = False,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chat sessions for the current user"""
    sessions = await ChatService.get_user_sessions(
        db, current_user.id, include_archived, limit
    )
    
    # Add message count and last message timestamp to each session
    session_responses = []
    for session in sessions:
        session_dict = session.__dict__.copy()
        
        # Get message count
        message_count = await ChatService.get_message_count(db, session.id)
        
        # Get last message timestamp
        last_message = await ChatService.get_last_message(db, session.id)
        
        session_dict["message_count"] = message_count
        session_dict["last_message_at"] = last_message.timestamp if last_message else None
        
        session_responses.append(ChatSessionResponse(**session_dict))
    
    return session_responses


@router.post("/chat/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat session"""
    session = await ChatService.create_session(db, current_user.id, session_data)
    return ChatSessionResponse.from_orm(session)


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session(
    session_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat session with its messages"""
    session = await ChatService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = await ChatService.get_session_messages(db, session_id, current_user.id, limit)
    
    session_dict = session.__dict__.copy()
    session_dict["message_count"] = len(messages)
    session_dict["last_message_at"] = messages[-1].timestamp if messages else None
    
    return ChatSessionWithMessages(
        **session_dict,
        messages=[ChatMessageResponse.from_orm(msg) for msg in messages]
    )


@router.put("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: int,
    update_data: ChatSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a chat session"""
    session = await ChatService.update_session(db, session_id, current_user.id, update_data)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return ChatSessionResponse.from_orm(session)


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete (archive) a chat session"""
    success = await ChatService.delete_session(db, session_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return {"message": "Chat session archived successfully"}


@router.get("/chat/stats")
async def get_chat_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat statistics for the current user"""
    return await ChatService.get_session_stats(db, current_user.id)


@router.get("/agent/config")
async def get_agent_config():
    """Get the default agent configuration"""
    return {
        "config": agent_service.get_default_config(),
        "tools": agent_service.get_available_tools(),
        "description": "Romanian Civic Information Assistant with 5 specialized tools"
    }


@router.get("/agent/tools")
async def get_agent_tools():
    """Get information about available agent tools"""
    return {
        "tools": agent_service.get_available_tools(),
        "total_tools": len(agent_service.get_available_tools()),
        "description": "AI-powered tools for Romanian civic information and services"
    }


@router.post("/agent/test")
async def test_agent(
    query: str,
    config: Optional[Dict[str, Any]] = None
):
    """
    Test the agent with a custom query and optional configuration
    
    This endpoint allows direct testing of the agent without creating chat sessions.
    Useful for development and debugging.
    """
    try:
        if not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        # Validate config if provided
        if config and not agent_service.validate_config(config):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid agent configuration provided"
            )
        
        # Process query with agent
        result = await agent_service.process_query(
            query=query,
            custom_config=config,
            config_name="api_test"
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent processing failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "query": query,
            "agent_response": result.get("response", ""),
            "reformulated_query": result.get("reformulated_query", ""),
            "tools_used": result.get("tools_used", []),
            "timpark_executed": result.get("timpark_executed", False),
            "processing_time": result.get("processing_time", 0),
            "timestamp": result.get("timestamp", ""),
            "metadata": {
                "config_used": result.get("config_used", ""),
                "search_results_available": bool(result.get("search_results", {}))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent test endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/agent/execution/{execution_id}", response_model=AgentExecutionResponse)
async def get_agent_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific agent execution"""
    execution = await ChatService.get_agent_execution(db, execution_id, current_user.id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent execution not found"
        )
    
    return AgentExecutionResponse.from_orm(execution)


@router.get("/health")
async def agent_health_check():
    """Health check endpoint for the AI agent system"""
    try:
        # Check if agent service is properly initialized
        config = agent_service.get_default_config()
        tools = agent_service.get_available_tools()
        
        # Check environment variables
        env_validation = settings.validate_ai_agent_config()
        
        # Determine overall health status
        is_healthy = bool(agent_service.Agent) and bool(config) and env_validation["fully_configured"]
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "agent_initialized": bool(agent_service.Agent),
            "config_loaded": bool(config),
            "tools_available": len(tools),
            "tools": [tool["name"] for tool in tools],
            "environment": {
                "gemini_key_configured": env_validation["gemini_key_set"],
                "perplexity_key_configured": env_validation["perplexity_key_set"],
                "agent_enabled": env_validation["agent_enabled"],
                "fully_configured": env_validation["fully_configured"]
            },
            "warnings": [] if env_validation["fully_configured"] else [
                "Missing API keys - some agent features may not work properly"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Agent service unhealthy: {str(e)}"
        )


@router.post("/agent/query")
async def direct_agent_query(
    request: Dict[str, Any]
):
    """
    Direct query to the AI agent (for sidebar integration)
    
    This endpoint provides direct access to the agent without database operations,
    ideal for sidebar components that need quick responses.
    
    Expected request format:
    {
        "query": "your question here",
        "config": { /* optional custom config */ }
    }
    """
    try:
        query = request.get("query", "").strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query is required and cannot be empty"
            )
        
        custom_config = request.get("config")
        
        # Validate config if provided
        if custom_config and not agent_service.validate_config(custom_config):
            logger.warning("Invalid config provided, using defaults")
            custom_config = None
        
        # Process query with agent
        result = await agent_service.process_query(
            query=query,
            custom_config=custom_config,
            config_name="sidebar_query"
        )
        
        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Unknown error occurred"),
                "query": query,
                "timestamp": result.get("timestamp", "")
            }
        
        # Return simplified response for sidebar
        return {
            "success": True,
            "query": query,
            "response": result.get("response", ""),
            "reformulated_query": result.get("reformulated_query", ""),
            "tools_used": result.get("tools_used", []),
            "timpark_executed": result.get("timpark_executed", False),
            "processing_time": round(result.get("processing_time", 0), 2),
            "timestamp": result.get("timestamp", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in direct agent query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing failed: {str(e)}"
        )


class AgentQueryRequest(BaseModel):
    query: str
    config: Optional[Dict[str, Any]] = None

class ToolConfigRequest(BaseModel):
    tool_configs: Dict[str, Any]

class ToolConfigResponse(BaseModel):
    success: bool
    updated_tools: Optional[List[str]] = None
    message: str
    error: Optional[str] = None

@router.get("/agent/config/schema")
async def get_agent_config_schema():
    """Get the configuration schema for all tools"""
    try:
        schema = agent_service.get_tool_config_schema()
        return {
            "success": True,
            "schema": schema,
            "description": "Configuration schema for all AI agent tools"
        }
    except Exception as e:
        logger.error(f"Error getting config schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/config/current")
async def get_current_agent_config():
    """Get current configuration for all tools"""
    try:
        current_configs = agent_service.get_current_tool_configs()
        available_models = agent_service.get_available_models()
        
        return {
            "success": True,
            "current_configs": current_configs,
            "available_models": available_models,
            "description": "Current configuration settings for all AI agent tools"
        }
    except Exception as e:
        logger.error(f"Error getting current config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/config/update", response_model=ToolConfigResponse)
async def update_agent_config(request: ToolConfigRequest):
    """Update configuration for specific tools"""
    try:
        result = agent_service.update_tool_config(request.tool_configs)
        
        if result["success"]:
            return ToolConfigResponse(
                success=True,
                updated_tools=result["updated_tools"],
                message=result["message"]
            )
        else:
            return ToolConfigResponse(
                success=False,
                message=result["message"],
                error=result.get("error")
            )
            
    except Exception as e:
        logger.error(f"Error updating agent config: {e}")
        return ToolConfigResponse(
            success=False,
            message="Failed to update configuration",
            error=str(e)
        )

@router.get("/agent/models")
async def get_available_models():
    """Get all available models for each tool type"""
    try:
        models = agent_service.get_available_models()
        return {
            "success": True,
            "models": models,
            "description": "Available AI models for each tool type"
        }
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 