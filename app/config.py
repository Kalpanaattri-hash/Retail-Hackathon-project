from functools import lru_cache
from typing import Optional, Set
from urllib.parse import quote_plus

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Sales Analytics Chatbot"
    app_env: str = "development"
    log_level: str = "INFO"

    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # SQLite (fallback)
    database_url: str = "sqlite:///./sales_analytics.db"
    
    # PostgreSQL / RDS (optional)
    db_host: Optional[str] = None
    db_port: int = 5432
    db_name: str = "salesdb"
    db_user: str = "postgres"
    db_password: Optional[SecretStr] = None
    db_ssl_mode: str = "require"

    allowed_tables: str = "sales,products,customers"
    max_result_rows: int = 100
    memory_size: int = 5

    @property
    def sqlalchemy_database_uri(self) -> str:
        # If RDS details provided, use PostgreSQL
        if self.db_host and self.db_password:
            password = self.db_password.get_secret_value() if isinstance(self.db_password, SecretStr) else self.db_password
            return f"postgresql+psycopg2://{self.db_user}:{quote_plus(password)}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode={self.db_ssl_mode}"
        # Otherwise fallback to SQLite
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
