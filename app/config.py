"""
应用配置模块

使用 Pydantic Settings V2 管理配置
"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Self

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    应用配置

    支持从环境变量和 .env 文件加载配置
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_nested_delimiter="__",
        validate_default=True,
    )

    # ============ 应用 ============
    APP_NAME: str = "FastAPI Starter"
    APP_ENV: Annotated[str, Field(pattern=r"^(development|staging|production)$")] = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ============ 服务器 ============
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True

    # ============ 安全 ============
    SECRET_KEY: SecretStr = Field(
        default=SecretStr("change-this-secret-key-in-production-min-32-chars"),
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ============ 数据库 ============
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/app.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 3600

    # ============ 超级管理员 ============
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_PASSWORD: SecretStr = Field(
        default=SecretStr("Admin@123456"),
    )

    # ============ Redis ============
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    # ============ CORS ============
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # ============ 分页 ============
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ============ 日志 ============
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    # ============ 验证器 ============

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list[str]) -> list[str]:
        """解析 CORS origins"""
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @model_validator(mode="after")
    def validate_production(self) -> Self:
        """生产环境验证"""
        if self.APP_ENV == "production":
            secret = self.SECRET_KEY.get_secret_value()
            if "change" in secret.lower() or len(secret) < 32:
                raise ValueError("SECRET_KEY must be changed in production (min 32 chars)")
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
        return self

    # ============ 属性 ============

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def secret_key_value(self) -> str:
        """获取 SECRET_KEY 值"""
        return self.SECRET_KEY.get_secret_value()

    @property
    def superuser_password_value(self) -> str:
        """获取超级管理员密码"""
        return self.FIRST_SUPERUSER_PASSWORD.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()