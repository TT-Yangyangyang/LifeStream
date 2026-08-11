from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# 继承 BaseSettings，代表这是一组从环境变量或文件自动读取的配置
# 实例化 Settings() 时，它会自动去 .env 中找 DATABASE_URL（大小写不敏感）并赋值。
class Settings(BaseSettings):
    database_url: str    #声明了你需要的配置项，比如 DATABASE_URL=postgresql://...

    model_config = SettingsConfigDict(
        env_file=".env",             #从项目根目录的 .env 文件读取配置。
        env_file_encoding="utf-8",   #文件编码。
        extra="ignore",              #里有多余的配置项，不报错，忽略它们。
    )

    cors_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()