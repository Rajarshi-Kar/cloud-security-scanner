from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Cloud Security Scanner"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg2://scanner:scanner@postgres:5432/scanner"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_SECRET_KEY: str = "change-me-in-env"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5175"]

    UPLOAD_DIR: str = "/app/storage/docker-images"
    REPORTS_DIR: str = "/app/storage/reports"
    CVE_LOOKUP_URL: str = "https://nvd.nist.gov/vuln/detail/"


settings = Settings()
