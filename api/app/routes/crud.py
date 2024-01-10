from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import schemas
from ..models import Media, Tweet, User


async def get_user_by_id(
    db: AsyncSession,
    user_id: int,
) -> User | None:
    query = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.followers), selectinload(User.following))
    )
    result = await db.execute(query)
    return result.scalar()


async def create_follow_by_user(
    db: AsyncSession, current_user: User, follower_id: int
) -> int | None:
    follower: User | None = await get_user_by_id(db=db, user_id=follower_id)
    if follower is None:
        return None
    if current_user in await follower.awaitable_attrs.followers:
        return 0
    follower.followers.append(current_user)
    await db.commit()
    return follower_id


async def delete_follow_by_user(
    db: AsyncSession, current_user: User, follower_id: int
) -> int | None:
    follower: User | None = await get_user_by_id(db=db, user_id=follower_id)
    if follower is None:
        return None
    if current_user not in await follower.awaitable_attrs.followers:
        return 0
    follower.followers.remove(current_user)
    await db.commit()
    return follower_id


async def get_tweet_by_id(db: AsyncSession, tweet_id: int) -> Tweet | None:
    query = select(Tweet).where(Tweet.id == tweet_id)
    result = await db.execute(query)
    return result.scalar()


async def get_tweets(db: AsyncSession) -> list[Tweet]:
    query = select(Tweet).options(
        selectinload(Tweet.likes),
        selectinload(Tweet.author),
        selectinload(Tweet.medias),
    )
    result = await db.execute(query)

    return result.scalars().unique().all()


async def create_like(
    db: AsyncSession, current_user: User, tweet_id: int
) -> int | None:
    tweet: Tweet | None = await get_tweet_by_id(db=db, tweet_id=tweet_id)
    if tweet is None:
        return None

    likes = await tweet.awaitable_attrs.likes
    # if current user is not tweet author and not in like list, add him there
    if tweet.author_id != current_user.id and current_user not in likes:
        likes.append(current_user)
        await db.commit()

    return tweet.author_id


async def delete_like(
    db: AsyncSession, current_user: User, tweet_id: int
) -> int | None:
    tweet: Tweet | None = await get_tweet_by_id(db=db, tweet_id=tweet_id)
    if tweet is None:
        return None
    likes = await tweet.awaitable_attrs.likes
    if current_user not in likes:
        return 0
    likes.remove(current_user)
    await db.commit()
    return tweet_id


async def create_tweet(
    db: AsyncSession,
    current_user: User,
    content: schemas.BaseTweet,
) -> int:
    # create a Tweet instance
    tweet = Tweet(
        content=content.tweet_data,
        author=current_user,
    )

    # if list of media exists, append it
    if content.tweet_media_ids:
        media_list = await get_attachments(db, content.tweet_media_ids)
        tweet.medias = media_list
        tweet.attachments = [media.path for media in media_list]

    db.add(tweet)
    await db.commit()

    return await tweet.awaitable_attrs.id


async def delete_tweet(
    db: AsyncSession, current_user: User, tweet_id: int
) -> int | None:
    tweet: Tweet | None = await get_tweet_by_id(db=db, tweet_id=tweet_id)
    if tweet is None:
        return None
    if tweet.author_id != current_user.id:
        return tweet.author_id
    await db.delete(tweet)
    await db.commit()
    return tweet.author_id


async def create_media(
    db: AsyncSession,
    path: str,
) -> int:
    media = Media(path=path)
    db.add(media)
    await db.commit()
    return media.id


async def get_medias(
    db: AsyncSession,
) -> list[Media]:
    query = select(Media)
    media_list = await db.execute(query)
    return media_list.scalars().unique().all()


async def get_media_by_id(db: AsyncSession, media_id: int) -> Media | None:
    query = select(Media).where(Media.id == media_id)
    media = await db.execute(query)
    return media.scalar()


async def get_attachments(db: AsyncSession, media_ids: list[int]):
    query = select(Media).where(Media.id.in_(media_ids))
    result = await db.execute(query)
    return result.scalars().unique().all()
