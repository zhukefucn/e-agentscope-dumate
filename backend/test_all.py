"""
E-AgentScope 完整功能测试脚本
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.core.database import async_session_maker
from app.api.auth import register, login
from app.api.agents import create_agent, get_agents
from app.schemas.user import UserCreate, UserLogin
from app.schemas.agent import AgentCreate
from app.models.user import User


async def test_all():
    """测试所有功能"""
    print("=" * 60)
    print("E-AgentScope 功能测试")
    print("=" * 60)
    
    async with async_session_maker() as db:
        # 1. 测试用户注册
        print("\n1. 测试用户注册...")
        try:
            user_create = UserCreate(
                username="testuser",
                email="test@example.com",
                password="test123456"
            )
            user = await register(user_create, db)
            print(f"   注册成功: {user.username} ({user.email})")
        except Exception as e:
            print(f"   注册失败: {e}")
            return
        
        # 2. 测试用户登录
        print("\n2. 测试用户登录...")
        try:
            user_login = UserLogin(username="testuser", password="test123456")
            token = await login(user_login, db)
            print(f"   登录成功，Token: {token.access_token[:30]}...")
        except Exception as e:
            print(f"   登录失败: {e}")
            return
        
        # 3. 测试创建Agent
        print("\n3. 测试创建Agent...")
        try:
            agent_create = AgentCreate(
                name="智能助手",
                description="一个友好的AI助手",
                system_prompt="你是一个友好的AI助手，乐于帮助用户解决问题。",
                model_provider="dashscope",
                model_name="qwen-plus",
                tools=["Read", "Write"],
                temperature=0.7,
                max_tokens=2000
            )
            agent = await create_agent(agent_create, user, db)
            print(f"   Agent创建成功: {agent.name} (ID: {agent.id})")
        except Exception as e:
            print(f"   Agent创建失败: {e}")
            return
        
        # 4. 测试获取Agent列表
        print("\n4. 测试获取Agent列表...")
        try:
            from sqlalchemy import select
            from app.models.agent import Agent
            query = select(Agent).where(Agent.user_id == user.id)
            result = await db.execute(query)
            agents = result.scalars().all()
            print(f"   获取成功，共 {len(agents)} 个Agent")
            for a in agents:
                print(f"   - {a.name}: {a.description}")
        except Exception as e:
            print(f"   获取失败: {e}")
            import traceback
            traceback.print_exc()
            return
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_all())
