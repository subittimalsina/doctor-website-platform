from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Doctor Website Platform"
    secret_key: str = "change-me-for-production"
    database_url: str = "sqlite:///./doctor_platform.db"
    ai_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    support_email: str = "support@doctor-portal.local"
    doctor_name: str = "Dr. Alex Morgan"
    clinic_name: str = "CityCare Clinic"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
