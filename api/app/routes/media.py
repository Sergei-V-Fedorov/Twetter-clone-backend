from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..dependencies import get_api_key, get_db_session
from . import utils
from .crud import create_media

router = APIRouter(prefix="/medias", tags=["Media"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_api_key)],
    response_model=schemas.MediaResponse,
    responses={
        **utils.FORMATTED_RESPONSES[201],
    },
)
async def upload_media(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    file: Annotated[UploadFile, File(description="Загружаемый файл")],
):
    filename = await utils.save_file(file, chunk_size=1024 * 1024)

    media_id = await create_media(db, filename)
    return schemas.MediaResponse(media_id=media_id)
