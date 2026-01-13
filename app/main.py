"""
FastAPI 0.128.0 应用入口

新版本特性:
- 改进的 lifespan 上下文管理
- 更好的类型提示支持
- 性能优化
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import AppException
from app.database import close_db, init_db

# 日志配置
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    应用生命周期管理

    FastAPI 0.128.0 推荐使用 lifespan 替代已废弃的 on_event
    """
    # ===== 启动 =====
    logger.info("🚀 Starting %s v%s", settings.APP_NAME, "2.0.0")
    logger.info("📍 Environment: %s", settings.APP_ENV)

    try:
        await init_db()
        logger.info("✅ Database connected")
    except Exception as e:
        logger.exception("❌ Database connection failed: %s", e)
        raise

    logger.info("📖 API Docs: http://%s:%s/docs", settings.HOST, settings.PORT)
    logger.info("🎉 Application ready!")

    yield

    # ===== 关闭 =====
    logger.info("👋 Shutting down...")
    await close_db()
    logger.info("✅ Cleanup complete")


def create_application() -> FastAPI:
    """
    应用工厂函数

    使用工厂模式创建应用，便于测试和配置
    """
    application = FastAPI(
        title=settings.APP_NAME,
        description="""
## 🚀 FastAPI Starter Kit v2.0

基于 **FastAPI 0.128.0** 的现代化 API 模板

### ✨ 特性
- 🔐 JWT 认证 (Access + Refresh Token)
- 👥 用户管理 CRUD
- 📄 自动分页
- 🗃️ SQLAlchemy 2.0 异步 ORM
- 🧪 完整测试覆盖
- 📝 自动 OpenAPI 文档

### 🔗 相关链接
- [FastAPI 文档](https://fastapi.tiangolo.com)
- [项目仓库](https://github.com/yourname/fastapi-starter)
        """,
        version="2.0.0",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if not settings.is_production else None,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        # FastAPI 0.128.0 新增选项
        separate_input_output_schemas=True,  # 分离输入输出 Schema
        redirect_slashes=True,
    )

    # 注册组件
    _register_middlewares(application)
    _register_exception_handlers(application)
    _register_routers(application)

    return application


def _register_middlewares(app: FastAPI) -> None:
    """注册中间件（按顺序，外层先执行）"""

    # GZip 压缩
    app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=5)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page", "X-Page-Size", "X-Request-ID"],
    )


def _register_exception_handlers(app: FastAPI) -> None:
    """注册异常处理器"""

    @app.exception_handler(AppException)
    async def app_exception_handler(
            request: Request,
            exc: AppException,
    ) -> ORJSONResponse:
        """自定义应用异常"""
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request,
            exc: RequestValidationError,
    ) -> ORJSONResponse:
        """请求验证错误"""
        errors = [
            {
                "field": ".".join(str(x) for x in err["loc"]),
                "message": err["msg"],
                "type": err["type"],
            }
            for err in exc.errors()
        ]
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": 422,
                    "message": "Validation Error",
                    "details": errors,
                },
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
            request: Request,
            exc: StarletteHTTPException,
    ) -> ORJSONResponse:
        """HTTP 异常"""
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
            request: Request,
            exc: Exception,
    ) -> ORJSONResponse:
        """未处理异常"""
        logger.exception("Unhandled exception: %s", exc)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": 500,
                    "message": str(exc) if settings.DEBUG else "Internal Server Error",
                },
            },
        )


def _register_routers(app: FastAPI) -> None:
    """注册路由"""

    # API v1
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # 根路由
    @app.get(
        "/",
        tags=["Root"],
        summary="API 信息",
        response_class=ORJSONResponse,
    )
    async def root() -> dict[str, Any]:
        """返回 API 基本信息"""
        return {
            "name": settings.APP_NAME,
            "version": "2.0.0",
            "fastapi_version": "0.128.0",
            "python_version": "3.11+",
            "docs": "/docs" if not settings.is_production else None,
            "openapi": f"{settings.API_V1_PREFIX}/openapi.json" if not settings.is_production else None,
        }

    @app.get(
        "/health",
        tags=["Health"],
        summary="健康检查",
        response_class=ORJSONResponse,
    )
    async def health() -> dict[str, Any]:
        """系统健康检查"""
        from app.database import db_manager

        db_healthy = await db_manager.check_connection()

        return {
            "status": "healthy" if db_healthy else "degraded",
            "checks": {
                "database": "ok" if db_healthy else "error",
            },
            "version": "2.0.0",
        }

    @app.get(
        "/ping",
        tags=["Health"],
        summary="Ping",
    )
    async def ping() -> dict[str, str]:
        """简单 ping 检查"""
        return {"ping": "pong"}


# 创建应用实例
app = create_application()

# ============ 开发服务器入口 ============
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )