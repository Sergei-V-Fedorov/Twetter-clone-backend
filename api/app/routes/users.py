from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from .. import schemas
from ..dependencies import get_api_key, get_db_session
from ..models import User
from .crud import create_follow_by_user, delete_follow_by_user, get_user_by_id
from .utils import FORMATTED_RESPONSES, get_formatted_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        **FORMATTED_RESPONSES[200],
    },
)
async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_api_key)],
):
    user_orm: User = await get_user_by_id(db=db, user_id=user.id)

    return await get_formatted_user(user_orm)


@router.get(
    "/{id}",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_api_key)],
    responses={
        **FORMATTED_RESPONSES[200],
        **FORMATTED_RESPONSES[404],
    },
)
async def get_user_profile(
    id: Annotated[int, Path(description="ID пользователя в базе данных")],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    user_orm: User | None = await get_user_by_id(db=db, user_id=id)
    if user_orm is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Пользователь с id# {id} не найден"},
        )

    return await get_formatted_user(user_orm)


@router.post(
    "/{id}/follow",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.OperationStatus,
    responses={
        **FORMATTED_RESPONSES[201],
        **FORMATTED_RESPONSES[400],
        **FORMATTED_RESPONSES[404],
    },
)
async def follow_by_user(
    id: Annotated[int, Path(description="ID пользователя в базе данных")],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_api_key)],
):
    if id == user.id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Вы не можете подписаться на самого себя!"},
        )

    result = await create_follow_by_user(db, current_user=user, follower_id=id)

    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Пользователь с id# {id} не найден"},
        )
    if result == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": f"Вы уже подписаны на пользователя с id# {id}"
            },
        )

    return schemas.OperationStatus()


@router.delete(
    "/{id}/follow",
    status_code=status.HTTP_200_OK,
    response_model=schemas.OperationStatus,
    responses={
        **FORMATTED_RESPONSES[200],
        **FORMATTED_RESPONSES[400],
        **FORMATTED_RESPONSES[404],
    },
)
async def unfollow(
    id: Annotated[int, Path(description="ID пользователя в базе данных")],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_api_key)],
):
    result = await delete_follow_by_user(db, current_user=user, follower_id=id)

    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Пользователь с id# {id} не найден"},
        )

    if result == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Вы не подписаны на пользователя с id# {id}"},
        )

    return schemas.OperationStatus()
