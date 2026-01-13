from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/library"

    LOAN_DAYS_DEFAULT: int = 14
    LOAN_RENEW_MAX: int = 2
    FINE_PER_DAY: float = 0.5

    JWT_SECRET_KEY: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MIN: int = 60               
    JWT_REFRESH_EXPIRES_DAYS: int = 7       


@lru_cache
def get_settings() -> Settings:
    return Settings()
