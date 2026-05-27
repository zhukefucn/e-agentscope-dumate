"""
Test script for authentication module
"""
import asyncio
from app.core.database import async_session_maker, init_db
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy import select


async def create_test_user():
    """Create a test user"""
    await init_db()
    
    async with async_session_maker() as session:
        # Check if test user exists
        result = await session.execute(select(User).where(User.username == "testuser"))
        if result.scalar_one_or_none():
            print("Test user already exists")
            return
        
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword123"),
            is_active=True,
            is_superuser=False
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        print(f"Test user created: {user}")
        print(f"Username: testuser")
        print(f"Password: testpassword123")


if __name__ == "__main__":
    asyncio.run(create_test_user())
