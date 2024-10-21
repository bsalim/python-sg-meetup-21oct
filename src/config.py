from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    ENCRYPTION_KEY: str
    SECRET_KEY: str
    # DATABASE_URL: PostgresDsn
    CORS_ORIGINS: str
    CORS_HEADERS: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()