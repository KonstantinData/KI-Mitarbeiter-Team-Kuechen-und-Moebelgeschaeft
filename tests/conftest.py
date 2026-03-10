"""Pytest Fixtures für alle Tests."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.main import app
from src.db.models.base import Base

# In-Memory SQLite für Tests (kein PostgreSQL nötig)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Erstellt eine Test-Datenbank-Engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        # SQLite unterstützt kein pgvector — KnowledgeChunk-Embedding überspringen
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Gibt eine Test-Datenbank-Session zurück (wird nach jedem Test zurückgerollt)."""
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client():
    """HTTP-Test-Client für FastAPI."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
