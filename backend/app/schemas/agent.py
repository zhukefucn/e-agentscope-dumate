"""
Agent Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class ModelProvider(str, Enum):
    """Supported model providers"""
    DASHSCOPE = "dashscope"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class AgentBase(BaseModel):
    """Base agent schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Agent名称")
    description: Optional[str] = Field(None, max_length=500, description="Agent描述")
    system_prompt: str = Field(..., min_length=1, description="系统提示词")
    model_provider: str = Field(..., description="模型提供商")
    model_name: str = Field(..., description="模型名称")
    tools: Optional[List[Any]] = Field(default=[], description="工具配置列表")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, le=32000, description="最大token数")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "智能助手",
                "description": "一个友好的AI助手",
                "system_prompt": "你是一个友好、专业的AI助手，致力于帮助用户解决问题。",
                "model_provider": "dashscope",
                "model_name": "qwen-plus",
                "tools": [],
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }


class AgentCreate(AgentBase):
    """Schema for creating a new agent"""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating an existing agent"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Agent名称")
    description: Optional[str] = Field(None, max_length=500, description="Agent描述")
    system_prompt: Optional[str] = Field(None, min_length=1, description="系统提示词")
    model_provider: Optional[str] = Field(None, description="模型提供商")
    model_name: Optional[str] = Field(None, description="模型名称")
    tools: Optional[List[Any]] = Field(None, description="工具配置列表")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(None, ge=1, le=32000, description="最大token数")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "更新后的助手",
                "description": "更新后的描述",
                "temperature": 0.8
            }
        }


class AgentResponse(BaseModel):
    """Schema for agent response"""
    id: int
    name: str
    description: Optional[str]
    system_prompt: str
    model_provider: str
    model_name: str
    tools: Optional[List[Any]]
    temperature: float
    max_tokens: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "智能助手",
                "description": "一个友好的AI助手",
                "system_prompt": "你是一个友好、专业的AI助手，致力于帮助用户解决问题。",
                "model_provider": "dashscope",
                "model_name": "qwen-plus",
                "tools": [],
                "temperature": 0.7,
                "max_tokens": 2000,
                "user_id": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class AgentListResponse(BaseModel):
    """Schema for agent list response"""
    total: int = Field(..., description="总数")
    agents: List[AgentResponse] = Field(..., description="Agent列表")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "agents": [
                    {
                        "id": 1,
                        "name": "智能助手",
                        "description": "一个友好的AI助手",
                        "system_prompt": "你是一个友好、专业的AI助手。",
                        "model_provider": "dashscope",
                        "model_name": "qwen-plus",
                        "tools": [],
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "user_id": 1,
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ]
            }
        }
