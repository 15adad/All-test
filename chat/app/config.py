from pydantic_settings import BaseSettings

# TODO怎么从.env里读配置
class Settings(BaseSettings):
    # 从.env文件中读取数据库连接字符串
    DATABASE_URL: str = "sqlite+aiosqlite:///./chat.db"
    # SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天

    class Config:
        env_file = ".env"


settings = Settings()