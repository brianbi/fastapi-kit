from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import DBSession, CurrentUser
from app.services.user import UserService
from app.schemas.user import Token, UserCreate, UserResponse
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.exceptions import UnauthorizedException, BadRequestException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register(
        user_in: UserCreate,
        db: DBSession
):
    """用户注册"""
    user_service = UserService(db)
    user = await user_service.create(user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
        db: DBSession,
        form_data: OAuth2PasswordRequestForm = Depends()
):
    """用户登录"""
    user_service = UserService(db)
    user = await user_service.authenticate(
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise UnauthorizedException("Incorrect username or password")

    if not user.is_active:
        raise UnauthorizedException("User is inactive")

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
        db: DBSession,
        refresh_token: str
):
    """刷新令牌"""
    token_data = verify_token(refresh_token)

    if not token_data or token_data.type != "refresh":
        raise BadRequestException("Invalid refresh token")

    user_service = UserService(db)
    user = await user_service.get_by_id(token_data.sub)

    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """获取当前用户信息"""
    return current_user