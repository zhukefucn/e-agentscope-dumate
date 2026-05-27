"""
AgentScope client for managing agent conversations
"""
import sys
import os
from typing import AsyncGenerator, Optional, Dict, Any, TYPE_CHECKING
import asyncio
import json

# Add agentscope to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'agentscope-main', 'src'))

from app.core.config import settings
from app.schemas.conversation import MessageRole

try:
    # Import AgentScope components
    from agentscope.agent import Agent
    from agentscope.model import DashScopeChatModel
    from agentscope.message import UserMsg, AssistantMsg, Msg
    from agentscope.credential import DashScopeCredential
    AGENTSCOPE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AgentScope import failed: {e}")
    AGENTSCOPE_AVAILABLE = False
    Agent = None  # Fallback for type hints


class AgentScopeClient:
    """Client for interacting with AgentScope agents"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "qwen-plus"
    ):
        """Initialize AgentScope client
        
        Args:
            api_key: DashScope API key
            model_name: Model name to use
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model_name = model_name
        self._agents: Dict[str, Agent] = {}
        
        if not AGENTSCOPE_AVAILABLE:
            print("Warning: AgentScope not available, using mock mode")
    
    def create_agent(
        self,
        agent_id: str,
        system_prompt: str = "You are a helpful AI assistant.",
        model_name: Optional[str] = None
    ) -> Optional[Any]:
        """Create or get an agent instance
        
        Args:
            agent_id: Unique agent identifier
            system_prompt: System prompt for the agent
            model_name: Model name (optional, uses default if not provided)
            
        Returns:
            Agent instance
        """
        if agent_id in self._agents:
            return self._agents[agent_id]
        
        if not AGENTSCOPE_AVAILABLE:
            # Return mock agent
            return MockAgent(agent_id, system_prompt)
        
        # Create credential
        credential = DashScopeCredential(api_key=self.api_key)
        
        # Create model
        model = DashScopeChatModel(
            credential=credential,
            model_name=model_name or self.model_name
        )
        
        # Create agent
        agent = Agent(
            name=agent_id,
            system_prompt=system_prompt,
            model=model
        )
        
        self._agents[agent_id] = agent
        return agent
    
    async def send_message(
        self,
        agent_id: str,
        message: str,
        conversation_history: list = None,
        system_prompt: str = "You are a helpful AI assistant."
    ) -> str:
        """Send a message to an agent and get response
        
        Args:
            agent_id: Agent identifier
            message: User message
            conversation_history: Previous conversation history
            system_prompt: System prompt for the agent
            
        Returns:
            Agent response
        """
        agent = self.create_agent(agent_id, system_prompt)
        
        # Build message list
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == MessageRole.USER:
                    messages.append(UserMsg(content=msg['content']))
                elif msg['role'] == MessageRole.ASSISTANT:
                    messages.append(AssistantMsg(content=msg['content']))
        
        # Add current message
        messages.append(UserMsg(content=message))
        
        # Get response
        if isinstance(agent, MockAgent):
            response = await agent.reply(messages)
        else:
            response = await agent.reply(messages)
        
        # Extract text content
        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    async def send_message_stream(
        self,
        agent_id: str,
        message: str,
        conversation_history: list = None,
        system_prompt: str = "You are a helpful AI assistant."
    ) -> AsyncGenerator[str, None]:
        """Send a message to an agent and stream response
        
        Args:
            agent_id: Agent identifier
            message: User message
            conversation_history: Previous conversation history
            system_prompt: System prompt for the agent
            
        Yields:
            Response chunks
        """
        agent = self.create_agent(agent_id, system_prompt)
        
        # Build message list
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == MessageRole.USER:
                    messages.append(UserMsg(content=msg['content']))
                elif msg['role'] == MessageRole.ASSISTANT:
                    messages.append(AssistantMsg(content=msg['content']))
        
        # Add current message
        messages.append(UserMsg(content=message))
        
        # Stream response
        if isinstance(agent, MockAgent):
            # Mock streaming
            response = "This is a mock response from AgentScope."
            for char in response:
                yield char
                await asyncio.sleep(0.01)
        else:
            # Real streaming
            async for event in agent.reply_stream(messages):
                # Handle different event types
                if hasattr(event, 'content') and event.content:
                    yield event.content
                elif hasattr(event, 'text') and event.text:
                    yield event.text
    
    def clear_agent(self, agent_id: str):
        """Clear an agent from cache"""
        if agent_id in self._agents:
            del self._agents[agent_id]


class MockAgent:
    """Mock agent for testing when AgentScope is not available"""
    
    def __init__(self, agent_id: str, system_prompt: str):
        self.agent_id = agent_id
        self.system_prompt = system_prompt
    
    async def reply(self, messages: list) -> str:
        """Mock reply method"""
        # Simulate processing
        await asyncio.sleep(0.1)
        
        # Get last user message
        last_msg = None
        for msg in reversed(messages):
            if hasattr(msg, 'content'):
                last_msg = msg.content
                break
        
        # Generate mock response
        return f"[Mock Agent {self.agent_id}] You said: {last_msg}. This is a simulated response."
    
    async def reply_stream(self, messages: list):
        """Mock streaming reply"""
        response = await self.reply(messages)
        for char in response:
            yield type('Event', (), {'content': char})()


# Global client instance
agentscope_client = AgentScopeClient()
