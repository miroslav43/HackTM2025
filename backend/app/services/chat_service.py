"""
Chat Service - Handles chat sessions, messages, and AI Agent integration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime
import uuid

from app.models.chat import ChatSession, ChatMessage, AgentExecution
from app.models.user import User
from app.schemas.chat import (
    ChatSessionCreate, ChatSessionUpdate, ChatMessageCreate,
    ChatSessionResponse, ChatMessageResponse, AgentExecutionResponse
)
from app.services.agent_service import agent_service

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat sessions and AI agent interactions"""
    
    @staticmethod
    async def create_session(db: AsyncSession, user_id: Union[str, uuid.UUID], session_data: ChatSessionCreate) -> ChatSession:
        """Create a new chat session"""
        # Convert string to UUID if necessary
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
            
        db_session = ChatSession(
            user_id=user_id,
            title=session_data.title
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        
        logger.info(f"Created chat session {db_session.id} for user {user_id}")
        return db_session
    
    @staticmethod
    async def get_session(db: AsyncSession, session_id: int, user_id: Union[str, uuid.UUID]) -> Optional[ChatSession]:
        """Get a chat session by ID for a specific user"""
        # Convert string to UUID if necessary
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
            
        stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_archived == False
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_sessions(
        db: AsyncSession, 
        user_id: Union[str, uuid.UUID], 
        include_archived: bool = False,
        limit: int = 50
    ) -> List[ChatSession]:
        """Get all chat sessions for a user"""
        # Convert string to UUID if necessary
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
            
        stmt = select(ChatSession).where(ChatSession.user_id == user_id)
        
        if not include_archived:
            stmt = stmt.where(ChatSession.is_archived == False)
        
        stmt = stmt.order_by(desc(ChatSession.updated_at)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def update_session(
        db: AsyncSession, 
        session_id: int, 
        user_id: Union[str, uuid.UUID], 
        update_data: ChatSessionUpdate
    ) -> Optional[ChatSession]:
        """Update a chat session"""
        session = await ChatService.get_session(db, session_id, user_id)
        if not session:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(session, field, value)
        
        session.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"Updated chat session {session_id}")
        return session
    
    @staticmethod
    async def delete_session(db: AsyncSession, session_id: int, user_id: Union[str, uuid.UUID]) -> bool:
        """Delete a chat session (archive it)"""
        session = await ChatService.get_session(db, session_id, user_id)
        if not session:
            return False
        
        session.is_archived = True
        session.updated_at = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Archived chat session {session_id}")
        return True
    
    @staticmethod
    async def add_message(
        db: AsyncSession,
        session_id: int,
        user_id: Union[str, uuid.UUID],
        role: str,
        content: str,
        processing_time: Optional[int] = None,
        tools_used: Optional[List[str]] = None,
        agent_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ChatMessage]:
        """Add a message to a chat session"""
        # Verify session belongs to user
        session = await ChatService.get_session(db, session_id, user_id)
        if not session:
            logger.warning(f"Session {session_id} not found for user {user_id}")
            return None
        
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            processing_time=processing_time,
            tools_used=tools_used,
            agent_metadata=agent_metadata
        )
        
        db.add(message)
        
        # Update session's updated_at timestamp
        session.updated_at = datetime.utcnow()
        
        # Auto-generate session title if this is the first user message
        if not session.title and role == "user":
            # Use first 50 characters of the message as title
            title = content[:50].strip()
            if len(content) > 50:
                title += "..."
            session.title = title
        
        await db.commit()
        await db.refresh(message)
        
        logger.info(f"Added {role} message to session {session_id}")
        return message
    
    @staticmethod
    async def get_session_messages(
        db: AsyncSession, 
        session_id: int, 
        user_id: Union[str, uuid.UUID],
        limit: int = 100
    ) -> List[ChatMessage]:
        """Get messages for a chat session"""
        # Verify session belongs to user
        session = await ChatService.get_session(db, session_id, user_id)
        if not session:
            return []
        
        stmt = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_message_count(db: AsyncSession, session_id: int) -> int:
        """Get the number of messages in a session"""
        stmt = select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session_id)
        result = await db.execute(stmt)
        return result.scalar() or 0
    
    @staticmethod
    async def get_last_message(db: AsyncSession, session_id: int) -> Optional[ChatMessage]:
        """Get the last message in a session"""
        stmt = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        ).order_by(desc(ChatMessage.timestamp)).limit(1)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_agent_execution(
        db: AsyncSession,
        message_id: int,
        agent_result: Dict[str, Any]
    ) -> AgentExecution:
        """Create an agent execution record"""
        # Handle config_used - can be string or dict
        config_used = agent_result.get("config_used", {})
        if isinstance(config_used, str):
            config_used = {"config_name": config_used}
        elif not isinstance(config_used, dict):
            config_used = {}
            
        execution = AgentExecution(
            message_id=message_id,
            original_question=agent_result.get("original_question", ""),
            reformulated_query=agent_result.get("reformulated_query"),
            config_used=config_used,
            execution_time=agent_result.get("execution_time"),
            tools_executed=agent_result.get("tools_executed", []),
            workflow_stopped_early=agent_result.get("workflow_stopped_early", False),
            timpark_result=agent_result.get("timpark_result"),
            web_search_result=agent_result.get("web_search_result"),
            trusted_sites_result=agent_result.get("trusted_sites_result"),
            final_response=agent_result.get("final_response")
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        logger.info(f"Created agent execution record for message {message_id}")
        return execution
    
    @staticmethod
    async def get_agent_execution(
        db: AsyncSession, 
        execution_id: int, 
        user_id: Union[str, uuid.UUID]
    ) -> Optional[AgentExecution]:
        """Get an agent execution by ID for a specific user"""
        # Convert string to UUID if necessary
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        stmt = select(AgentExecution).join(ChatMessage).join(ChatSession).where(
            AgentExecution.id == execution_id,
            ChatSession.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def process_user_message(
        db: AsyncSession,
        user_id: Union[str, uuid.UUID],
        message_content: str,
        session_id: Optional[int] = None,
        agent_config: Optional[Dict[str, Any]] = None,
        create_new_session: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user message with the AI agent
        
        Returns:
            Dictionary with session, user message, agent response, and execution details
        """
        try:
            # Convert string to UUID if necessary
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
                
            # Handle session creation/retrieval
            if create_new_session or not session_id:
                # Create new session
                session = await ChatService.create_session(
                    db, user_id, ChatSessionCreate(title=None)
                )
                session_id = session.id
            else:
                # Use existing session
                session = await ChatService.get_session(db, session_id, user_id)
                if not session:
                    # Session not found, create new one
                    session = await ChatService.create_session(
                        db, user_id, ChatSessionCreate(title=None)
                    )
                    session_id = session.id
            
            # Add user message
            user_message = await ChatService.add_message(
                db, session_id, user_id, "user", message_content
            )
            
            if not user_message:
                raise Exception("Failed to create user message")
            
            # Process with AI agent
            logger.info(f"Processing query with agent: {message_content[:50]}...")
            agent_result = await agent_service.process_query(
                query=message_content,
                custom_config=agent_config,
                config_name=f"session_{session_id}"
            )
            
            # Determine the response content
            if agent_result.get("error"):
                response_content = f"Îmi pare rău, a apărut o eroare în procesarea solicitării: {agent_result['error']}"
                tools_used = []
                processing_time = agent_result.get("execution_time", 0)
            else:
                # Use final response if available, otherwise combine available results
                if agent_result.get("final_response"):
                    response_content = agent_result["final_response"]
                elif agent_result.get("timpark_result", {}).get("tool_activated"):
                    # TimPark payment was executed
                    timpark_result = agent_result["timpark_result"]
                    response_content = f"✅ {timpark_result.get('message', 'Plata parcării a fost procesată cu succes!')}"
                    if timpark_result.get('automation_result', {}).get('success'):
                        response_content += "\n\n🚗 Automatizarea plății a fost executată cu succes!"
                elif agent_result.get("web_search_result"):
                    response_content = agent_result["web_search_result"]
                else:
                    response_content = "Am procesat cererea ta, dar nu am putut genera un răspuns complet."
                
                tools_used = agent_result.get("tools_executed", [])
                processing_time = agent_result.get("execution_time", 0)
            
            # Add agent response message
            agent_message = await ChatService.add_message(
                db=db,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response_content,
                processing_time=processing_time,
                tools_used=tools_used,
                agent_metadata={
                    "agent_version": "romanian_civic_assistant_v1.0",
                    "tools_executed": tools_used,
                    "workflow_stopped_early": agent_result.get("workflow_stopped_early", False)
                }
            )
            
            # Create agent execution record if agent processed successfully
            agent_execution = None
            if not agent_result.get("error"):
                agent_execution = await ChatService.create_agent_execution(
                    db, agent_message.id, agent_result
                )
            
            # Refresh session data
            await db.refresh(session)
            
            return {
                "success": True,
                "session": session,
                "user_message": user_message,
                "agent_message": agent_message,
                "agent_execution": agent_execution,
                "agent_result": agent_result
            }
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            
            # Try to add error message if we have a session
            if 'session_id' in locals() and session_id:
                try:
                    await ChatService.add_message(
                        db, session_id, user_id, "assistant",
                        f"Îmi pare rău, a apărut o eroare în procesarea cererii tale: {str(e)}"
                    )
                except:
                    logger.error("Failed to add error message to session")
            
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id if 'session_id' in locals() else None
            }
    
    @staticmethod
    async def get_session_stats(db: AsyncSession, user_id: Union[str, uuid.UUID]) -> Dict[str, Any]:
        """Get chat statistics for a user"""
        # Convert string to UUID if necessary
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        # Get total sessions
        total_sessions_stmt = select(func.count(ChatSession.id)).where(
            ChatSession.user_id == user_id,
            ChatSession.is_archived == False
        )
        total_sessions_result = await db.execute(total_sessions_stmt)
        total_sessions = total_sessions_result.scalar() or 0
        
        # Get total messages
        total_messages_stmt = select(func.count(ChatMessage.id)).join(ChatSession).where(
            ChatSession.user_id == user_id,
            ChatSession.is_archived == False
        )
        total_messages_result = await db.execute(total_messages_stmt)
        total_messages = total_messages_result.scalar() or 0
        
        # Get recent activity (today)
        recent_sessions_stmt = select(func.count(ChatSession.id)).where(
            ChatSession.user_id == user_id,
            ChatSession.is_archived == False,
            ChatSession.updated_at >= datetime.utcnow().date()
        )
        recent_sessions_result = await db.execute(recent_sessions_stmt)
        recent_sessions = recent_sessions_result.scalar() or 0
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "recent_sessions": recent_sessions
        } 