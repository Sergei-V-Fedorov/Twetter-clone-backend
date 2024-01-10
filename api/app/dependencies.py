"""Dependencies applied to all API."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session
from .models import User


async def get_db_session():
    """
    Return instance of async session.

    Yields:
        instance of async session
    """
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


async def get_api_key(
    api_key: Annotated[
        str,
        Header(
            description="Ключ для авторизации пользователя",
            alias="api-key",
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """
    Check if user with api-key exists in database.

    Args:
        api_key (str): User api-key passed in header.
        db (AsyncSession): async session instance.

    Raises:
        HTTPException: if there are no user with such api_key.

    Returns:
        User: user instance or 404 status code.

    """
    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access is denied for unauthorized users",
        )

    return user
