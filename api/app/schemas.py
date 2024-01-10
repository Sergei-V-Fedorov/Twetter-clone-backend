from pydantic import BaseModel, ConfigDict, Field


class OperationStatus(BaseModel):
    result: bool = Field(
        default=True,
        description="Результат ответа",
    )


class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(description="ID пользователя в базе данных", examples=[1])
    name: str = Field(description="Имя пользователя", examples=["Peter Pan"])


class UserLikes(BaseUser):
    id: int = Field(
        alias="user_id",
        description="ID пользователя в базе данных",
    )


class UserOut(BaseUser):
    followers: list[BaseUser] | None = Field(
        default=[],
        description="Список пользователей, \
        которые подписаны на данного пользователя",
        examples=[
            [{"id": 3, "name": "Wendy"}, {"id": 4, "name": "Captain Hook"}]
        ],
    )

    following: list[BaseUser] | None = Field(
        default=[],
        description="Список пользователей, \
        на которых подписан данный пользователь",
        examples=[[{"id": 2, "name": "Barrie J.M."}]],
    )


class UserResponse(OperationStatus):
    user: UserOut


class BaseTweet(BaseModel):
    tweet_data: str = Field(description="Текст твита")
    tweet_media_ids: list[int] = Field(
        default=[], description="Список ID файлов или пустой список"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"tweet_data": "Мой первый твит", "tweet_media_ids": []},
                {"tweet_data": "Мой второй твит"},
                {"tweet_data": "Мой третий твит", "tweet_media_ids": [1]},
                {
                    "tweet_data": "Мой четвертый твит",
                    "tweet_media_ids": [1, 2],
                },
            ]
        }
    }


class Tweet(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(description="ID твита", examples=[1])
    content: str = Field(
        description="Содержание твита",
        examples=[
            "Вы просто подумайте о чем-нибудь хорошем, \
            ваши мысли сделают вас легкими и вы взлетите."
        ],
    )
    attachments: list[str] = Field(
        default=[],
        description="Список имен присоединенных файлов",
        examples=[["./path/Neverland.png"]],
    )
    author: BaseUser = Field(
        description="Автор твита",
    )
    likes: list[UserLikes] = Field(
        default=[],
        description="Список пользователей, поставивших лайк твиту",
        examples=[
            [
                {"user_id": 3, "name": "Wendy"},
                {"user_id": 4, "name": "Captain Hook"},
            ]
        ],
    )


class TweetsList(OperationStatus):
    tweets: list[Tweet]


class TweetResponse(OperationStatus):
    tweet_id: int = Field(
        description="ID опубликованного твита",
    )


class MediaPath(BaseModel):
    path: list[str] | None


class MediaORM(MediaPath):
    model_config = ConfigDict(from_attributes=True)
    media_id: int = Field(alias="id")


class MediaResponse(OperationStatus):
    media_id: int = Field(
        description="ID файла в базе данных",
    )


class ResponseMessage(OperationStatus):
    result: str = Field(default=False, description="Результат ответа")
    message: str = Field(
        description="Сообщение об ошибке", examples=["Что-то пошло не так :("]
    )
