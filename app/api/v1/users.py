from math import ceil
from fastapi import APIRouter

from app.dependencies import DBSession, CurrentUser, CurrentSuperUser, Pagination
from app.services.user import UserService
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import PaginatedResponse, MessageResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def get_users(
        db: DBSession,
        pagination: Pagination,
        current_user: CurrentSuperUser  # 仅管理员可访问
):
    """获取用户列表（管理员）"""
    user_service = UserService(db)
    users, total = await user_service.get_list(
        skip=pagination.skip,
        limit=pagination.page_size
    )

    return PaginatedResponse(
        items=users,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=ceil(total / pagination.page_size)
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: int,
        db: DBSession,
        current_user: CurrentUser
):
    """获取用户详情"""
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
        user_in: UserUpdate,
        db: DBSession,
        current_user: CurrentUser
):
    """更新当前用户信息"""
    user_service = UserService(db)
    user = await user_service.update(current_user.id, user_in)
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
        user_id: int,
        db: DBSession,
        current_user: CurrentSuperUser  # 仅管理员可删除
):
    """删除用户（管理员）"""
    user_service = UserService(db)
    await user_service.delete(user_id)
    return MessageResponse(message="User deleted successfully")