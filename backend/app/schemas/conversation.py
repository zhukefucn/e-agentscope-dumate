"""
Conversation Pydantic schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation"""
    agent_id: str = Field(..., description="Agent ID to use for this conversation")
    title: Optional[str] = Field(None, description="Optional title for the conversation")


class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    content: str = Field(..., description="Message content")
    stream: bool = Field(False, description="Whether to use streaming response")


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    id: int
    title: Optional[str]
    agent_id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Schema for conversation list response"""
    id: int
    title: Optional[str]
    agent_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class StreamMessage(BaseModel):
    """Schema for streaming message chunk"""
    type: str = Field(..., description="Event type: 'text', 'done', 'error'")
    content: Optional[str] = Field(None, description="Text content for 'text' type")
    message_id: Optional[int] = Field(None, description="Message ID for 'done' type")
    error: Optional[str] = Field(None, description="Error message for 'error' type")
