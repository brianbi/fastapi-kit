from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import NotFoundException, ConflictException


class UserService:
    """用户服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """根据用户名或邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(
                (User.username == identifier) | (User.email == identifier)
            )
        )
        return result.scalar_one_or_none()

    async def get_list(
            self,
            skip: int = 0,
            limit: int = 20
    ) -> tuple[List[User], int]:
        """获取用户列表"""
        # 获取总数
        count_result = await self.db.execute(
            select(func.count()).select_from(User)
        )
        total = count_result.scalar()

        # 获取列表
        result = await self.db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        users = result.scalars().all()

        return list(users), total

    async def create(self, user_in: UserCreate) -> User:
        """创建用户"""
        # 检查邮箱是否存在
        if await self.get_by_email(user_in.email):
            raise ConflictException("Email already registered")

        # 检查用户名是否存在
        if await self.get_by_username(user_in.username):
            raise ConflictException("Username already taken")

        user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, user_in: UserUpdate) -> User:
        """更新用户"""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        update_data = user_in.model_dump(exclude_unset=True)

        # 如果更新密码，需要哈希
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        """删除用户"""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        await self.db.delete(user)
        return True

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = await self.get_by_username_or_email(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user