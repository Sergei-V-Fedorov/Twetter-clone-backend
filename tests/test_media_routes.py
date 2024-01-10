import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_tweet(client: AsyncClient):
    """Check for uploading a media file."""

    files = {"file": open("uploaded_image.jpg", "rb")}
    response = await client.post(
        "/api/medias",
        headers={"api-key": "test"},
        files=files,
    )

    assert response.status_code == 201, "Запрос не выполнен"
    assert "result" and "media_id" in response.json(), "Неверный формат ответа"
    assert response.json()["result"], "Неверный результат ответа"
    assert response.json()["media_id"] == 1, "Неправильный id медиа"
