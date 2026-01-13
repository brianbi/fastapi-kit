# FastAPI Starter Kit

基于 **FastAPI 0.128.0** 的现代化 API 模板，提供完整的开箱即用解决方案。

## ✨ 特性

- 🔐 **JWT 认证** (Access + Refresh Token)
- 👥 **用户管理** CRUD 操作
- 📄 **自动分页** 支持
- 🗃️ **SQLAlchemy 2.0** 异步 ORM
- 🧪 **完整测试** 覆盖
- 📝 **自动 OpenAPI** 文档
- 📊 **健康检查** 接口
- 🔁 **GZip** 压缩中间件
- 🔄 **Redis** 缓存支持
- 📁 **文件上传** 功能
- 📧 **邮件发送** 集成
- 🔒 **权限管理** (RBAC)
- 🛡️ **请求验证** 和错误处理
- 🏷️ **类型提示** 完整支持
- 🚀 **异步性能** 优化

## 🛠️ 技术栈

- **FastAPI**: 0.128.0
- **Python**: 3.11+
- **SQLAlchemy**: 2.0.37 (异步)
- **Pydantic**: 2.10.4
- **Database**: SQLite (默认), PostgreSQL (可选)
- **缓存**: Redis (可选)
- **中间件**: CORS, GZip, Logging
- **测试**: pytest

## 🚀 快速开始

### 本地开发

```bash
# 1. 克隆项目
# git clone <repository-url>

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖 (推荐使用 uv)
pip install uv
uv pip install -r requirements.txt

# 或者直接使用 pip
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件以满足您的需求

# 5. 初始化数据库 (可选)
alembic upgrade head

# 6. 启动服务
uvicorn app.main:app --reload
```

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d

# 查看服务日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📊 API 文档

启动服务后，可以通过以下地址访问 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ 项目结构

```
fastapi-kit/
├── app/
│   ├── api/v1/           # API 路由
│   ├── core/             # 核心功能模块
│   ├── models/           # 数据模型
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # 业务逻辑
│   ├── config.py         # 应用配置
│   ├── database.py       # 数据库配置
│   ├── dependencies.py   # 依赖注入
│   └── main.py           # 应用入口
├── alembic/              # 数据库迁移
├── tests/                # 测试文件
├── scripts/              # 脚本文件
├── .env.example          # 环境变量示例
├── docker-compose.yml    # Docker 配置
├── Dockerfile            # Docker 构建文件
├── requirements.txt      # Python 依赖
└── README.md
```

## 🧪 测试

运行单元测试：

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app

# 运行特定测试文件
pytest tests/test_users.py
```

## 🔧 配置

所有配置都可以通过 `.env` 文件或环境变量进行自定义。主要配置项包括：

- `APP_NAME`: 应用名称
- `APP_ENV`: 环境 (development/staging/production)
- `DEBUG`: 调试模式
- `SECRET_KEY`: JWT 密钥
- `DATABASE_URL`: 数据库连接字符串
- `REDIS_URL`: Redis 连接字符串
- `FIRST_SUPERUSER_*`: 首个超级管理员账户信息

## 🚢 部署

### 生产环境部署

1. 设置环境变量
   ```bash
   export APP_ENV=production
   export DEBUG=false
   export SECRET_KEY=your-production-secret-key
   # ... 其他环境变量
   ```

2. 使用 Uvicorn 启动
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. 或使用 Gunicorn
   ```bash
   gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4
   ```

## 📋 功能清单

| 功能 | 状态 | 描述 |
|------|------|------|
| ✅ 用户注册/登录 | 完成 | 支持邮箱/用户名注册和登录 |
| ✅ JWT 认证 | 完成 | Access + Refresh Token 机制 |
| ✅ 刷新令牌 | 完成 | 自动刷新过期的访问令牌 |
| ✅ 异步数据库 | 完成 | 基于 SQLAlchemy 2.0 的异步 ORM |
| ✅ 分页支持 | 完成 | 自动分页和元数据返回 |
| ✅ CORS 配置 | 完成 | 支持跨域请求 |
| ✅ Docker 支持 | 完成 | 完整的 Docker 部署方案 |
| ✅ 单元测试 | 完成 | 完整的测试覆盖 |
| ✅ 环境变量管理 | 完成 | 通过 Pydantic Settings 管理配置 |
| ✅ 邮件发送 | 完成 | 集成邮件发送功能 |
| ✅ 文件上传 | 完成 | 支持文件上传和管理 |
| ✅ Redis 缓存 | 完成 | 集成 Redis 缓存机制 |
| ✅ 日志系统 | 完成 | 结构化日志记录 |
| ✅ 权限管理 | 完成 | 基于角色的访问控制 (RBAC) |
| ✅ 健康检查 | 完成 | 系统状态监控接口 |
| ✅ 错误处理 | 完成 | 统一的异常处理机制 |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目！

## 📄 许可证

该项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。