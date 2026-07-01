from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://steam:steam123@localhost:5432/steam"
    sync_database_url: str = "postgresql://steam:steam123@localhost:5432/steam"
    redis_url: str = "redis://localhost:6379/0"
    duckdb_path: str = "/data/steam_olap.duckdb"
    csv_dir: str = "/data"
    steam_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
