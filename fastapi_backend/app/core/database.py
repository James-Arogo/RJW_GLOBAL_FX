"""Database connection and session management."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


def _ensure_runtime_columns(sync_conn):
    """Add lightweight runtime columns for local SQLite environments."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(sync_conn)

    runtime_columns = {
        "trades": {
            "leverage": "ALTER TABLE trades ADD COLUMN leverage NUMERIC(6, 2) NOT NULL DEFAULT 1.0",
            "margin_required_kes": "ALTER TABLE trades ADD COLUMN margin_required_kes NUMERIC(12, 2)",
            "notional_value_kes": "ALTER TABLE trades ADD COLUMN notional_value_kes NUMERIC(12, 2)",
            "quantity_units": "ALTER TABLE trades ADD COLUMN quantity_units NUMERIC(18, 8)",
            "liquidation_price": "ALTER TABLE trades ADD COLUMN liquidation_price NUMERIC(15, 6)",
        },
        "deposit_transactions": {
            "transaction_type": "ALTER TABLE deposit_transactions ADD COLUMN transaction_type VARCHAR(20) NOT NULL DEFAULT 'DEPOSIT'",
            "provider_reference": "ALTER TABLE deposit_transactions ADD COLUMN provider_reference VARCHAR(120)",
            "checkout_url": "ALTER TABLE deposit_transactions ADD COLUMN checkout_url VARCHAR(255)",
            "provider_status": "ALTER TABLE deposit_transactions ADD COLUMN provider_status VARCHAR(50)",
        },
    }

    for table_name, columns in runtime_columns.items():
        if not inspector.has_table(table_name):
            continue

        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        for column_name, ddl in columns.items():
            if column_name not in existing_columns:
                sync_conn.execute(text(ddl))


async def get_db() -> AsyncSession:
    """Get database session dependency."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_runtime_columns)


async def close_db():
    """Close database connection."""
    await engine.dispose()
