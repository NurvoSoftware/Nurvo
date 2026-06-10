"""asyncpg connection pool with jsonb codec registration."""

import json
import logging

import asyncpg

from config import DATABASE_URL

log = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def _init_conn(conn: asyncpg.Connection) -> None:
    # Register jsonb codec so Python dicts/lists can be passed directly
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def init_pool() -> None:
    global _pool
    # asyncpg uses postgresql://, strip the +asyncpg SQLAlchemy prefix if present
    dsn = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    _pool = await asyncpg.create_pool(dsn, init=_init_conn, min_size=1, max_size=5)
    log.info("DB pool initialized")


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized")
    return _pool
