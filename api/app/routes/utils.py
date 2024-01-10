import os

import aiofiles
from fastapi import UploadFile, status

from .. import schemas
from ..models import User


async def get_formatted_user(user_orm: User) -> schemas.UserResponse:
    user_out: schemas.UserOut = schemas.UserOut.model_validate(user_orm)

    return schemas.UserResponse(user=user_out)


async def save_file(
    file: UploadFile,
    chunk_size: int,
) -> str:
    fname = os.path.join("./images", file.filename)
    async with aiofiles.open(fname, mode="wb") as f:
        while content := await file.read(chunk_size):
            await f.write(content)
    await file.close()

    return fname


FORMATTED_RESPONSES = {
    200: {status.HTTP_200_OK: {"description": "Успешный запрос"}},
    201: {status.HTTP_201_CREATED: {"description": "Объект создан"}},
    400: {
        status.HTTP_400_BAD_REQUEST: {
            "model": schemas.ResponseMessage,
            "description": "Неправильные параметры запроса",
        }
    },
    404: {
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.ResponseMessage,
            "description": "Объект не найден",
        }
    },
    422: {
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Ошибка валидации данных запроса"
        }
    },
}
