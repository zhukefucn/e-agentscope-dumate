"""
Test script for Agent API endpoints
"""
import asyncio
import sys
from sqlalchemy import select
from app.core.database import async_session_maker, init_db
from app.models.user import User
from app.models.agent import Agent


async def create_test_user():
    """Create a test user for testing"""
    async with async_session_maker() as session:
        # Check if test user exists
        result = await session.execute(select(User).where(User.username == "testuser"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"Test user already exists: {existing_user.username} (ID: {existing_user.id})")
            return existing_user
        
        # Create new test user (using pre-hashed password for testing)
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA/7.J6LlZy",  # "testpassword123"
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"Created test user: {user.username} (ID: {user.id})")
        return user


async def test_agent_crud():
    """Test Agent CRUD operations"""
    print("\n" + "="*60)
    print("Testing Agent CRUD Operations")
    print("="*60)
    
    # Initialize database
    await init_db()
    
    # Create test user
    user = await create_test_user()
    
    async with async_session_maker() as session:
        # Test 1: Create Agent
        print("\n1. Creating test agent...")
        agent = Agent(
            name="智能助手",
            description="一个友好的AI助手",
            system_prompt="你是一个友好、专业的AI助手，致力于帮助用户解决问题。",
            model_provider="dashscope",
            model_name="qwen-plus",
            tools='[{"name": "search", "description": "搜索工具"}]',
            temperature=0.7,
            max_tokens=2000,
            user_id=user.id
        )
        session.add(agent)
        await session.commit()
        await session.refresh(agent)
        print(f"   [OK] Created agent: {agent.name} (ID: {agent.id})")
        
        # Test 2: Read Agent
        print("\n2. Reading agent...")
        result = await session.execute(select(Agent).where(Agent.id == agent.id))
        fetched_agent = result.scalar_one_or_none()
        if fetched_agent:
            print(f"   [OK] Fetched agent: {fetched_agent.name}")
            print(f"        - Model: {fetched_agent.model_provider}/{fetched_agent.model_name}")
            print(f"        - Temperature: {fetched_agent.temperature}")
            print(f"        - Max Tokens: {fetched_agent.max_tokens}")
        else:
            print("   [FAIL] Failed to fetch agent")
            return False
        
        # Test 3: Update Agent
        print("\n3. Updating agent...")
        fetched_agent.name = "更新后的智能助手"
        fetched_agent.temperature = 0.8
        await session.commit()
        await session.refresh(fetched_agent)
        print(f"   [OK] Updated agent name: {fetched_agent.name}")
        print(f"   [OK] Updated temperature: {fetched_agent.temperature}")
        
        # Test 4: List Agents
        print("\n4. Listing all agents for user...")
        result = await session.execute(
            select(Agent).where(Agent.user_id == user.id).order_by(Agent.created_at.desc())
        )
        agents = result.scalars().all()
        print(f"   [OK] Found {len(agents)} agent(s)")
        for a in agents:
            print(f"        - {a.name} (ID: {a.id}, Model: {a.model_provider}/{a.model_name})")
        
        # Test 5: Delete Agent
        print("\n5. Deleting agent...")
        await session.delete(fetched_agent)
        await session.commit()
        
        # Verify deletion
        result = await session.execute(select(Agent).where(Agent.id == agent.id))
        deleted = result.scalar_one_or_none()
        if deleted is None:
            print("   [OK] Agent deleted successfully")
        else:
            print("   [FAIL] Failed to delete agent")
            return False
    
    print("\n" + "="*60)
    print("[SUCCESS] All tests passed!")
    print("="*60)
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_agent_crud())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
