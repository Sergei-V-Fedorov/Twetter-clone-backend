"""Module for database initialization."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from .database import Base
from .models import Tweet, User


async def init_database(
    engine: AsyncEngine,
    session: AsyncSession,
    drop: bool = False,
) -> None:
    """
    Initialize the database.

    :param engine:
    :param session:
    :param drop:
    :return:
    """
    async with engine.begin() as conn:
        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with session:
        async with session.begin():
            query = select(User)
            users = await session.execute(query)
            if not users.all():
                user1 = User(name="admin", api_key="admin")
                user2 = User(name="sf", api_key="test")
                session.add_all(
                    [
                        user1,
                        user2,
                        Tweet(
                            content="first tweet", author_id=1, likes=[user2]
                        ),
                    ]
                )
