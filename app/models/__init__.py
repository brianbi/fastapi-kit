# 导入 Base 以便其他地方使用
from app.database import Base

# 导入所有模型，确保它们被注册到 Base.metadata
from app.models.user import User

# 导出所有模型
__all__ = [
    "Base",
    "User",
]