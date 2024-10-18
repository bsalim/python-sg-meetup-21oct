from typing import Any
from collections.abc import AsyncGenerator
from sqlalchemy import (
    Boolean,
    Column,
    CursorResult,
    DateTime,
    ForeignKey,
    Identity,
    Insert,
    Integer,
    LargeBinary,
    MetaData,
    Select,
    String,
    Table,
    Update,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = str(settings.DATABASE_URL)
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    pool_size=30,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300
)

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

# auth_user = Table(
#     "auth_user",
#     metadata,
#     Column("id", Integer, Identity(), primary_key=True),
#     Column("email", String, nullable=False),
#     Column("password", LargeBinary, nullable=False),
#     Column("is_admin", Boolean, server_default="false", nullable=False),
#     Column("created_at", DateTime, server_default=func.now(), nullable=False),
#     Column("updated_at", DateTime, onupdate=func.now()),
# )

# refresh_tokens = Table(
#     "auth_refresh_token",
#     metadata,
#     Column("uuid", UUID, primary_key=True),
#     Column("user_id", ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False),
#     Column("refresh_token", String, nullable=False),
#     Column("expires_at", DateTime, nullable=False),
#     Column("created_at", DateTime, server_default=func.now(), nullable=False),
#     Column("updated_at", DateTime, onupdate=func.now()),
# )


async def fetch_one(select_query: Select | Insert | Update) -> dict[str, Any] | None:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return cursor.first()._asdict() if cursor.rowcount > 0 else None


async def fetch_all(select_query: Select | Insert | Update) -> list[dict[str, Any]]:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return [r._asdict() for r in cursor.all()]


async def execute(select_query: Insert | Update) -> None:
    async with engine.begin() as conn:
        await conn.execute(select_query)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)

# Dependency
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        # logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        yield session
