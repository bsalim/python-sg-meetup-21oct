from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_ALG: str = 'sha-256'
    JWT_SECRET: str
    SECRET_KEY: str
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()