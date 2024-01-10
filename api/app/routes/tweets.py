from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from .. import schemas
from ..dependencies import get_api_key, get_db_session
from ..models import User
from .crud import (
    create_like,
    create_tweet,
    delete_like,
    delete_tweet,
    get_tweets,
)
from .utils import FORMATTED_RESPONSES

router = APIRouter(
    prefix="/tweets",
    tags=["Tweets"],
)


@router.get(
    "",
    response_model=schemas.TweetsList,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_api_key)],
    responses={
        **FORMATTED_RESPONSES[200],
    },
)
async def get_tweets_list(
    db: Annotated[AsyncSession, Depends(get_db_session)]
):
    tweets_orm = await get_tweets(db)
    tweets = [schemas.Tweet.model_validate(tweet) for tweet in tweets_orm]

    return schemas.TweetsList(tweets=tweets)


@router.post(
    "",
    response_model=schemas.TweetResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        **FORMATTED_RESPONSES[201],
    },
)
async def create_new_tweet(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_api_key)],
    tweet: schemas.BaseTweet,
):
    tweet_id = await create_tweet(db, current_user=user, content=tweet)

    return {"tweet_id": tweet_id}


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.OperationStatus,
    responses={
        **FORMATTED_RESPONSES[200],
        **FORMATTED_RESPONSES[400],
        **FORMATTED_RESPONSES[404],
    },
)
async def delete_own_tweet(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_api_key)],
    id: Annotated[int, Path(description="ID твита")],
):
    response = await delete_tweet(db, current_user=user, tweet_id=id)

    if response is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Твит с id# {id} не найден"},
        )
    if response != user.id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Нельзя удалить чужой твит!"},
        )
    return schemas.OperationStatus()


@router.post(
    "/{id}/likes",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.OperationStatus,
    responses={
        **FORMATTED_RESPONSES[201],
        **FORMATTED_RESPONSES[400],
        **FORMATTED_RESPONSES[404],
    },
)
async def make_a_like(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    id: Annotated[int, Path(description="ID твита")],
    user: Annotated[User, Depends(get_api_key)],
):
    tweet_author = await create_like(db, tweet_id=id, current_user=user)
    if tweet_author is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Твит с id# {id} не найден"},
        )
    if tweet_author == user.id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Нельзя поставить лайк самому себе!"},
        )
    return schemas.OperationStatus()


@router.delete(
    "/{id}/likes",
    response_model=schemas.OperationStatus,
    status_code=status.HTTP_200_OK,
    responses={
        **FORMATTED_RESPONSES[200],
        **FORMATTED_RESPONSES[400],
        **FORMATTED_RESPONSES[404],
    },
)
async def delete_likes(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    id: Annotated[int, Path(description="ID твита")],
    user: Annotated[User, Depends(get_api_key)],
):
    tweet_id = await delete_like(db, tweet_id=id, current_user=user)
    if tweet_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Твит с id# {id} не найден"},
        )
    if tweet_id == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Вы ещё не лайкнули твит с id# {id}!"},
        )
    return schemas.OperationStatus()
