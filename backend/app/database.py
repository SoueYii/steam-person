from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings
import duckdb
import os

# ─── PostgreSQL ──────────────────────────────────────────────────────────
engine = create_async_engine(settings.database_url, pool_size=10, max_overflow=20)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()


# ─── DuckDB (OLAP) ───────────────────────────────────────────────────────
_duckdb_conn: duckdb.DuckDBPyConnection | None = None


def get_olap() -> duckdb.DuckDBPyConnection:
    global _duckdb_conn
    if _duckdb_conn is None:
        db_path = settings.duckdb_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        _duckdb_conn = duckdb.connect(db_path)
    return _duckdb_conn


def close_olap():
    global _duckdb_conn
    if _duckdb_conn:
        _duckdb_conn.close()
        _duckdb_conn = None
