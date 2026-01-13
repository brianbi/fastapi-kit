import pytest
from app.config import Settings, get_settings


def test_config_singleton():
    """测试配置单例模式"""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2
    assert settings1.APP_NAME == settings2.APP_NAME


def test_config_default_values():
    """测试配置默认值"""
    settings = Settings(_env_file=None)  # 不加载 .env 文件
    
    assert settings.APP_NAME == "FastAPI Starter"
    assert settings.APP_ENV == "development"
    assert settings.DEBUG is True
    assert settings.API_V1_PREFIX == "/api/v1"
    from app.config import BASE_DIR  # 导入真实的 BASE_DIR
    expected_db_path = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'app.db'}"
    # 标准化路径分隔符
    expected_db_path = expected_db_path.replace('\\', '/')
    actual_db_path = settings.DATABASE_URL.replace('\\', '/')
    assert actual_db_path == expected_db_path
    assert settings.FIRST_SUPERUSER_EMAIL == "admin@example.com"
    assert settings.FIRST_SUPERUSER_USERNAME == "admin"


def test_config_properties_with_defaults():
    """测试使用默认值的配置属性"""
    settings = Settings(_env_file=None)  # 不加载 .env 文件
    
    assert settings.is_development is True
    assert settings.is_production is False
    assert len(settings.secret_key_value) >= 32
    assert settings.superuser_password_value == "Admin@123456"

def test_config_properties_with_env():
    """测试使用 .env 文件的配置属性"""
    settings = get_settings()  # 加载 .env 文件
    
    assert settings.is_development is True
    assert settings.is_production is False
    assert len(settings.secret_key_value) >= 32
    # 根据 .env 文件，密码应该是自定义值
    assert settings.superuser_password_value == "MyCustomPassword123!"


def test_cors_origins_parsing():
    """测试 CORS 源解析功能"""
    # 测试逗号分隔字符串
    settings_from_string = Settings(
        _env_file=None,
        CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
    )
    assert "http://localhost:3000" in settings_from_string.CORS_ORIGINS
    assert "http://localhost:8080" in settings_from_string.CORS_ORIGINS
    
    # 测试 JSON 字符串
    settings_from_json = Settings(
        _env_file=None,
        CORS_ORIGINS='["http://localhost:3000", "http://localhost:8080"]'
    )
    assert "http://localhost:3000" in settings_from_json.CORS_ORIGINS
    assert "http://localhost:8080" in settings_from_json.CORS_ORIGINS


def test_production_validation():
    """测试生产环境验证"""
    # 测试无效的生产环境配置
    with pytest.raises(ValueError, match="SECRET_KEY must be changed in production"):
        Settings(
            _env_file=None,
            APP_ENV="production",
            DEBUG=True,
            SECRET_KEY="change-this-secret-key-in-production-min-32-chars"
        )
    
    # 测试有效的生产环境配置
    valid_secret = "a" * 32  # 至少32字符的密钥
    settings = Settings(
        _env_file=None,
        APP_ENV="production",
        DEBUG=False,
        SECRET_KEY=valid_secret
    )
    assert settings.is_production is True
    assert settings.DEBUG is False
