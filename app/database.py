from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()

connect_args = {}
pool_kwargs = {}

# SQLite-specific setup
if "sqlite" in settings.sqlalchemy_database_uri:
    connect_args = {"check_same_thread": False}
    # SQLite uses NullPool and doesn't support pool_size/max_overflow
else:
    # PostgreSQL-specific setup
    if settings.db_ssl_mode:
        connect_args["sslmode"] = settings.db_ssl_mode
    pool_kwargs = {"pool_size": 5, "max_overflow": 10, "pool_pre_ping": True}

engine = create_engine(
    settings.sqlalchemy_database_uri,
    connect_args=connect_args,
    **pool_kwargs
)

# Enable foreign keys for SQLite
if "sqlite" in settings.sqlalchemy_database_uri:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
