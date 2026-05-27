"""
Conversation API routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation, Message, MessageRole
from app.schemas.conversation import (
    ConversationCreate,
    MessageCreate,
    MessageResponse,
    ConversationResponse,
    ConversationListResponse,
    StreamMessage
)
from app.services.agentscope_client import agentscope_client
import json
import asyncio

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    # Create conversation
    conversation = Conversation(
        title=conversation_data.title or "New Conversation",
        agent_id=conversation_data.agent_id,
        user_id=current_user.id
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return conversation


@router.get("/conversations", response_model=List[ConversationListResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of conversations for current user"""
    # Query conversations with message count
    query = (
        select(
            Conversation,
            func.count(Message.id).label("message_count")
        )
        .outerjoin(Message)
        .where(Conversation.user_id == current_user.id)
        .group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Build response
    conversations = []
    for row in rows:
        conv, msg_count = row
        conversations.append(
            ConversationListResponse(
                id=conv.id,
                title=conv.title,
                agent_id=conv.agent_id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count
            )
        )
    
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation with messages"""
    query = (
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == current_user.id)
        .options(selectinload(Conversation.messages))
    )
    
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a conversation"""
    # Verify conversation exists and belongs to user
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    conv_result = await db.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return messages


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to conversation and get agent response"""
    # Verify conversation exists and belongs to user
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    conv_result = await db.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get conversation history
    history_query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    history_result = await db.execute(history_query)
    history_messages = history_result.scalars().all()
    
    # Build conversation history for agent
    conversation_history = [
        {"role": msg.role.value, "content": msg.content}
        for msg in history_messages
    ]
    
    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=message_data.content
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    # Check if streaming is requested
    if message_data.stream:
        return StreamingResponse(
            stream_agent_response(
                db=db,
                conversation=conversation,
                conversation_history=conversation_history,
                user_message_content=message_data.content,
                user_message_id=user_message.id
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        # Non-streaming response
        try:
            # Get agent response
            agent_response = await agentscope_client.send_message(
                agent_id=conversation.agent_id,
                message=message_data.content,
                conversation_history=conversation_history
            )
            
            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=agent_response
            )
            db.add(assistant_message)
            
            # Update conversation updated_at
            conversation.updated_at = asyncio.get_event_loop().time()
            
            await db.commit()
            await db.refresh(assistant_message)
            
            return MessageResponse.model_validate(assistant_message)
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get agent response: {str(e)}"
            )


async def stream_agent_response(
    db: AsyncSession,
    conversation: Conversation,
    conversation_history: list,
    user_message_content: str,
    user_message_id: int
):
    """Stream agent response as SSE events"""
    try:
        # Send start event
        yield f"data: {json.dumps({'type': 'start'})}\n\n"
        
        # Stream response from agent
        full_response = []
        async for chunk in agentscope_client.send_message_stream(
            agent_id=conversation.agent_id,
            message=user_message_content,
            conversation_history=conversation_history
        ):
            full_response.append(chunk)
            # Send text chunk
            event_data = StreamMessage(type="text", content=chunk)
            yield f"data: {event_data.model_dump_json()}\n\n"
        
        # Save complete assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content="".join(full_response)
        )
        db.add(assistant_message)
        await db.commit()
        await db.refresh(assistant_message)
        
        # Send done event
        event_data = StreamMessage(type="done", message_id=assistant_message.id)
        yield f"data: {event_data.model_dump_json()}\n\n"
        
    except Exception as e:
        # Send error event
        event_data = StreamMessage(type="error", error=str(e))
        yield f"data: {event_data.model_dump_json()}\n\n"


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    # Verify conversation exists and belongs to user
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Delete conversation (messages will be cascade deleted)
    await db.delete(conversation)
    await db.commit()
    
    # Clear agent from cache
    agentscope_client.clear_agent(conversation.agent_id)
