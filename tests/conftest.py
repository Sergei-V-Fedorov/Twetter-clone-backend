import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
import pytest_asyncio.plugin
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..api.app.database import Base
from ..api.app.dependencies import get_db_session
from ..api.app.main import app
from ..api.app.models import Tweet, User

# Создаем подключение к тестовой БД
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/test_db"

engine = create_async_engine(DATABASE_URL)
test_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Возвращает сессию тестовой БД
async def get_test_db() -> AsyncGenerator[AsyncClient, None]:
    async with test_session() as session:
        yield session


# Переписывает зависимости боевого приложения
app.dependency_overrides[get_db_session] = get_test_db


@pytest_asyncio.fixture()
async def init_test_db():
    """Fixture for initialization of the database."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with test_session() as session:
        async with session.begin():
            user1 = User(name="admin", api_key="admin")
            user2 = User(name="sf", api_key="test")
            user3 = User(name="ElonMusk", api_key="Elon1234", followers=[user2])
            session.add_all(
                [
                    user1,
                    user2,
                    user3,
                    Tweet(content="first tweet", author_id=1, likes=[user2]),
                ]
            )


@pytest_asyncio.fixture()
async def client(init_test_db) -> AsyncGenerator[AsyncClient, None]:
    """Fixture returning async client for test cases."""

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create async event loop on the base current event loop policy."""

    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
