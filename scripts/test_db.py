"""
测试数据库初始化脚本
运行: python -m scripts.test_db
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_database():
    """测试数据库初始化"""
    from app.database import init_db, close_db, db_manager
    from app.models.user import User
    from sqlalchemy import select

    print("=" * 50)
    print("🧪 Testing Database Initialization")
    print("=" * 50)

    try:
        # 1. 初始化数据库
        print("\n1️⃣  Initializing database...")
        await init_db()
        print("   ✅ Database initialized successfully")

        # 2. 测试查询
        print("\n2️⃣  Testing database query...")
        async for session in db_manager.get_session():
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"   ✅ Found {len(users)} user(s) in database")

            for user in users:
                print(f"      - {user.username} ({user.email}) {'👑 Superuser' if user.is_superuser else ''}")

        # 3. 测试创建用户
        print("\n3️⃣  Testing user creation...")
        from app.services.user import UserService
        from app.schemas.user import UserCreate

        async for session in db_manager.get_session():
            user_service = UserService(session)

            # 检查测试用户是否存在
            existing = await user_service.get_by_username("testuser")
            if existing:
                print("   ℹ️  Test user already exists, skipping creation")
            else:
                new_user = await user_service.create(
                    UserCreate(
                        email="test@example.com",
                        username="testuser",
                        password="testpassword123",
                        full_name="Test User"
                    )
                )
                print(f"   ✅ Created test user: {new_user.username}")

        print("\n" + "=" * 50)
        print("✅ All database tests passed!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 关闭数据库连接
        await close_db()
        print("\n👋 Database connection closed")


if __name__ == "__main__":
    asyncio.run(test_database())