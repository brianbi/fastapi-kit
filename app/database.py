"""
数据库模块

SQLAlchemy 2.0+ 异步数据库连接管理
"""

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 命名约定
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(AsyncAttrs, DeclarativeBase):
    """SQLAlchemy 声明式基类"""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class DatabaseManager:
    """数据库连接管理器"""

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("Database not initialized")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        return self._session_factory

    def init(self, database_url: str | None = None) -> None:
        """初始化数据库连接"""
        url = database_url or settings.DATABASE_URL

        # SQLite 需要确保目录存在
        if url.startswith("sqlite"):
            db_path = url.split("///")[-1]
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # 引擎配置
        engine_kwargs: dict = {
            "echo": settings.DATABASE_ECHO,
            "future": True,
            "pool_pre_ping": True,
        }

        # 非 SQLite 连接池配置
        if not url.startswith("sqlite"):
            engine_kwargs.update({
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "pool_recycle": settings.DATABASE_POOL_RECYCLE,
            })

        self._engine = create_async_engine(url, **engine_kwargs)

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def create_tables(self) -> None:
        """创建所有表"""
        from app.models import user  # noqa: F401

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """删除所有表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def check_connection(self) -> bool:
        """检查数据库连接"""
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """关闭连接"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取会话"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


# 全局实例
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """依赖注入函数"""
    async for session in db_manager.get_session():
        yield session


async def init_db() -> None:
    """初始化数据库"""
    import logging

    logger = logging.getLogger(__name__)

    db_manager.init()
    await db_manager.create_tables()
    logger.info("Database tables created")

    await _create_first_superuser()


async def _create_first_superuser() -> None:
    """创建初始超级管理员"""
    import logging

    from sqlalchemy import select

    from app.core.security import get_password_hash
    from app.models.user import User

    logger = logging.getLogger(__name__)

    async for session in db_manager.get_session():
        result = await session.execute(
            select(User).where(User.is_superuser == True)  # noqa: E712
        )
        if result.scalar_one_or_none():
            logger.info("Superuser already exists")
            return

        superuser = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username=settings.FIRST_SUPERUSER_USERNAME,
            hashed_password=get_password_hash(settings.superuser_password_value),
            full_name="Administrator",
            is_active=True,
            is_superuser=True,
        )
        session.add(superuser)
        await session.commit()
        logger.info("Superuser created: %s", settings.FIRST_SUPERUSER_USERNAME)


async def close_db() -> None:
    """关闭数据库"""
    await db_manager.close()