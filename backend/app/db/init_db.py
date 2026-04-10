"""
Database initialization and migration script.
Uses structured logging instead of print().
"""
from sqlalchemy import inspect, text

from app.db.database import engine, Base
from app.db import models
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def init_db():
    """Initialize database by creating all tables."""
    logger.info("Initializing database...")
    db_display = settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL
    logger.info("Database: %s", db_display)

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    verify_tables()


def verify_tables():
    """Verify that all expected tables are created."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected_tables = [
        "users",
        "resumes",
        "skill_analyses",
        "learning_roadmaps",
        "notifications",
        "chat_history",
        "courses",
    ]

    logger.info("Found %d tables in database", len(tables))

    for table in expected_tables:
        if table in tables:
            columns = inspector.get_columns(table)
            logger.info("  ✓ %s (%d columns)", table, len(columns))
        else:
            logger.warning("  ✗ %s — MISSING", table)


def test_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            if "sqlite" in settings.DATABASE_URL.lower():
                result = conn.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()[0]
                logger.info("SQLite connected (v%s)", version)
            else:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info("PostgreSQL connected (%s)", version.split(",")[0])
            return True
    except Exception as exc:
        logger.error("Database connection failed: %s", exc)
        return False


if __name__ == "__main__":
    if test_connection():
        init_db()
    else:
        exit(1)
