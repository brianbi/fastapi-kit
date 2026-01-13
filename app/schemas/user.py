from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============ 基础 Schema ============
class UserBase(BaseModel):
    """用户基础 Schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


# ============ 创建 Schema ============
class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=8, max_length=100)


# ============ 更新 Schema ============
class UserUpdate(BaseModel):
    """更新用户"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# ============ 响应 Schema ============
class UserResponse(UserBase):
    """用户响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserInDB(UserResponse):
    """数据库中的用户"""
    hashed_password: str


# ============ 认证 Schema ============
class Token(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token 载荷"""
    sub: int  # user_id
    exp: datetime
    type: str  # access or refresh


class LoginRequest(BaseModel):
    """登录请求"""
    username: str  # 可以是用户名或邮箱
    password: str