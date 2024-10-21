from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    ENCRYPTION_KEY: str
    SECRET_KEY: str
    # DATABASE_URL: PostgresDsn
    CORS_ORIGINS: str
    CORS_HEADERS: str

    def _comma_separated_values(self, value: str) -> List[str]:
        return [v.strip() for v in value.split(",")]
    
    @field_validator("CORS_ORIGINS")
    def parse_cors_origins(cls, value: str) -> List[str]:
        return cls._comma_separated_values(cls, value)

    @field_validator("CORS_HEADERS")
    def parse_cors_headers(cls, value: str) -> List[str]:
        return cls._comma_separated_values(cls, value)

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()