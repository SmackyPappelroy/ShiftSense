from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "ShiftSense"
    database_url: str = Field(
        default="postgresql+psycopg://shiftsense:shiftsense@db:5432/shiftsense",
        env="DATABASE_URL",
    )
    jwt_secret: str = Field(default="change-this-secret", env="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60
    file_upload_max_mb: int = 50
    feature_flags_default: str = "energy,predictive,alarms"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
