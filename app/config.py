from functools import lru_cache
from typing import Optional, Set
from urllib.parse import quote_plus

from pydantic import BaseSettings, Field, SecretStr


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    app_name: str = "Sales Analytics Chatbot"
    app_env: str = "development"
    log_level: str = "INFO"

    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    database_url: str = "sqlite:///./sales_analytics.db"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "salesdb"
    db_user: str = "postgres"
    db_password: SecretStr = Field(default=SecretStr("postgres"))
    db_ssl_mode: str = "require"

    allowed_tables: str = "sales,products,customers"
    max_result_rows: int = 100
    memory_size: int = 5

    @property
    def sqlalchemy_database_uri(self) -> str:
        return self.database_url

    @property
    def allowed_tables_set(self) -> Set[str]:
        return {table.strip().lower() for table in self.allowed_tables.split(",") if table.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
