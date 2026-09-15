"""Application configuration.

All configuration comes from environment variables (or a local .env file),
never hard-coded values. The app fails fast at import time if a required
secret such as DATABASE_URL or API_KEY is missing.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Required (no defaults) -> app refuses to start if unset.
    database_url: str
    api_key: str

    # Optional with sensible defaults.
    log_level: str = "INFO"
    app_port: int = 8000
    db_statement_timeout_ms: int = 2000
    stuck_processing_minutes: int = 15
    dashboard_recent_limit: int = 10


settings = Settings()  # fails fast if DATABASE_URL / API_KEY missing (intended)
