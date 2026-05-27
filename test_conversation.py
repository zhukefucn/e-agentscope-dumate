"""
Test conversation API endpoints
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.conversation import Conversation, Message, MessageRole
from app.schemas.conversation import (
    ConversationCreate,
    MessageCreate,
    MessageResponse,
    ConversationResponse
)


def test_models():
    """Test database models"""
    print("Testing models...")
    
    # Test Conversation model
    conv = Conversation(
        id=1,
        title="Test Conversation",
        agent_id="test-agent",
        user_id=1
    )
    print(f"✓ Conversation model: {conv}")
    
    # Test Message model
    msg = Message(
        id=1,
        conversation_id=1,
        role=MessageRole.USER,
        content="Hello, agent!"
    )
    print(f"✓ Message model: {msg}")


def test_schemas():
    """Test Pydantic schemas"""
    print("\nTesting schemas...")
    
    # Test ConversationCreate
    conv_create = ConversationCreate(
        agent_id="test-agent",
        title="New Chat"
    )
    print(f"✓ ConversationCreate: {conv_create}")
    
    # Test MessageCreate
    msg_create = MessageCreate(
        content="Hello!",
        stream=True
    )
    print(f"✓ MessageCreate: {msg_create}")
    
    # Test MessageResponse
    msg_response = MessageResponse(
        id=1,
        role=MessageRole.USER,
        content="Hello!",
        created_at="2024-01-01T00:00:00"
    )
    print(f"✓ MessageResponse: {msg_response}")


async def test_agentscope_client():
    """Test AgentScope client"""
    print("\nTesting AgentScope client...")
    
    from app.services.agentscope_client import AgentScopeClient, MockAgent
    
    # Create client
    client = AgentScopeClient()
    print(f"✓ AgentScopeClient created")
    
    # Test mock agent
    agent = client.create_agent("test-agent", "You are a helpful assistant.")
    print(f"✓ Agent created: {type(agent).__name__}")
    
    # Test send message
    response = await client.send_message(
        agent_id="test-agent",
        message="Hello!",
        conversation_history=[]
    )
    print(f"✓ Send message response: {response[:50]}...")
    
    # Test streaming
    print("✓ Testing streaming...")
    chunks = []
    async for chunk in client.send_message_stream(
        agent_id="test-agent",
        message="Test streaming",
        conversation_history=[]
    ):
        chunks.append(chunk)
    print(f"✓ Streamed {len(chunks)} chunks")


def main():
    """Run all tests"""
    print("=" * 60)
    print("E-AgentScope Conversation Module Tests")
    print("=" * 60)
    
    try:
        test_models()
        test_schemas()
        asyncio.run(test_agentscope_client())
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
