from typing import Annotated
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.services.user import UserService
from app.core.security import verify_token
from app.core.exceptions import UnauthorizedException, ForbiddenException

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)

# 数据库会话依赖
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
        db: DBSession,
        token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前用户"""
    token_data = verify_token(token)
    if not token_data or token_data.type != "access":
        raise UnauthorizedException()

    user_service = UserService(db)
    user = await user_service.get_by_id(token_data.sub)

    if not user:
        raise UnauthorizedException()
    if not user.is_active:
        raise ForbiddenException("User is inactive")

    return user


async def get_current_active_superuser(
        current_user: User = Depends(get_current_user)
) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise ForbiddenException("Not enough permissions")
    return current_user


# 类型别名
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentSuperUser = Annotated[User, Depends(get_current_active_superuser)]


# 分页参数依赖
class PaginationParams:
    """分页参数"""

    def __init__(
            self,
            page: int = Query(1, ge=1, description="页码"),
            page_size: int = Query(
                settings.DEFAULT_PAGE_SIZE,
                ge=1,
                le=settings.MAX_PAGE_SIZE,
                description="每页数量"
            )
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size


Pagination = Annotated[PaginationParams, Depends()]