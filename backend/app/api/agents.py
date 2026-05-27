"""
Agent API routes
"""
import json
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.agent import Agent
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentListResponse
)

router = APIRouter()


def parse_tools(tools_str: str) -> List[Any]:
    """Parse tools JSON string to list"""
    if not tools_str:
        return []
    try:
        return json.loads(tools_str)
    except json.JSONDecodeError:
        return []


def serialize_tools(tools: List[Any]) -> str:
    """Serialize tools list to JSON string"""
    if not tools:
        return "[]"
    return json.dumps(tools, ensure_ascii=False)


@router.get("/", response_model=AgentListResponse, summary="获取Agent列表")
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的所有Agent列表
    
    - **skip**: 跳过的记录数（分页）
    - **limit**: 返回的最大记录数
    """
    # Get total count
    count_query = select(func.count()).select_from(Agent).where(Agent.user_id == current_user.id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get agents
    query = select(Agent).where(Agent.user_id == current_user.id).offset(skip).limit(limit).order_by(Agent.created_at.desc())
    result = await db.execute(query)
    agents = result.scalars().all()
    
    # Convert tools JSON string to list
    agent_responses = []
    for agent in agents:
        agent_dict = {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "system_prompt": agent.system_prompt,
            "model_provider": agent.model_provider,
            "model_name": agent.model_name,
            "tools": parse_tools(agent.tools),
            "temperature": agent.temperature,
            "max_tokens": agent.max_tokens,
            "user_id": agent.user_id,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at
        }
        agent_responses.append(AgentResponse(**agent_dict))
    
    return AgentListResponse(total=total, agents=agent_responses)


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED, summary="创建新Agent")
async def create_agent(
    agent_create: AgentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的Agent
    
    - **name**: Agent名称
    - **description**: Agent描述
    - **system_prompt**: 系统提示词
    - **model_provider**: 模型提供商 (dashscope/openai/deepseek/ollama/custom)
    - **model_name**: 模型名称
    - **tools**: 工具配置列表
    - **temperature**: 温度参数 (0.0-2.0)
    - **max_tokens**: 最大token数
    """
    # Create new agent
    agent = Agent(
        name=agent_create.name,
        description=agent_create.description,
        system_prompt=agent_create.system_prompt,
        model_provider=agent_create.model_provider,
        model_name=agent_create.model_name,
        tools=serialize_tools(agent_create.tools),
        temperature=agent_create.temperature,
        max_tokens=agent_create.max_tokens,
        user_id=current_user.id
    )
    
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    # Return response
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        model_provider=agent.model_provider,
        model_name=agent.model_name,
        tools=parse_tools(agent.tools),
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        user_id=agent.user_id,
        created_at=agent.created_at,
        updated_at=agent.updated_at
    )


@router.get("/{agent_id}", response_model=AgentResponse, summary="获取Agent详情")
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取单个Agent的详细信息
    
    - **agent_id**: Agent ID
    """
    query = select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id)
    result = await db.execute(query)
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        model_provider=agent.model_provider,
        model_name=agent.model_name,
        tools=parse_tools(agent.tools),
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        user_id=agent.user_id,
        created_at=agent.created_at,
        updated_at=agent.updated_at
    )


@router.put("/{agent_id}", response_model=AgentResponse, summary="更新Agent")
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新Agent信息
    
    - **agent_id**: Agent ID
    - **name**: Agent名称（可选）
    - **description**: Agent描述（可选）
    - **system_prompt**: 系统提示词（可选）
    - **model_provider**: 模型提供商（可选）
    - **model_name**: 模型名称（可选）
    - **tools**: 工具配置列表（可选）
    - **temperature**: 温度参数（可选）
    - **max_tokens**: 最大token数（可选）
    """
    query = select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id)
    result = await db.execute(query)
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )
    
    # Update fields
    update_data = agent_update.model_dump(exclude_unset=True)
    
    if "tools" in update_data:
        update_data["tools"] = serialize_tools(update_data["tools"])
    
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    await db.commit()
    await db.refresh(agent)
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        model_provider=agent.model_provider,
        model_name=agent.model_name,
        tools=parse_tools(agent.tools),
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        user_id=agent.user_id,
        created_at=agent.created_at,
        updated_at=agent.updated_at
    )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除Agent")
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除指定的Agent
    
    - **agent_id**: Agent ID
    """
    query = select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id)
    result = await db.execute(query)
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )
    
    await db.delete(agent)
    await db.commit()
    
    return None
