"""
Database connection setup.

Uses SQLAlchemy 2.0 DeclarativeBase instead of deprecated declarative_base().
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

# Determine if using SQLite or PostgreSQL
is_sqlite = "sqlite" in settings.DATABASE_URL.lower()

# Configure engine with appropriate settings
engine_kwargs = {
    "pool_pre_ping": True,  # Verify connections before using
}

# SQLite-specific configuration
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL-specific configuration
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 3600,
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base class."""
    pass
from app.db import models # Ensure models are registered before creating tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Yield a database session; auto-closes on exit."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
