# ============ 构建阶段 ============
FROM python:3.12-slim AS builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv (更快的包管理器)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 复制依赖文件
COPY requirements.txt .

# 安装依赖到虚拟环境
RUN ~/.cargo/bin/uv venv /opt/venv
RUN ~/.cargo/bin/uv pip install --python /opt/venv/bin/python -r requirements.txt

# ============ 运行阶段 ============
FROM python:3.12-slim

WORKDIR /app

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 设置环境变量
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 创建非 root 用户
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]