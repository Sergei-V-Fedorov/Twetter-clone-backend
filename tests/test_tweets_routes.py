import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_authorization_when_get_tweets_list(client: AsyncClient):
    """Check for authorization for getting a list of tweets."""

    response = await client.get("/api/tweets", headers={"api-key": "incorrect-key"})
    assert response.status_code == 401, "Ошибка авторизации"
    assert "detail" in response.json(), "Неверный формат ответа"
    assert (
        response.json()["detail"] == "Access is denied for unauthorized users"
    ), "Неверное сообщение об ошибке"


@pytest.mark.asyncio
async def test_get_tweets_list(client: AsyncClient):
    """Check for getting the tweets list."""

    response = await client.get("/api/tweets", headers={"api-key": "test"})
    assert response.status_code == 200, "Запрос не выполнен"
    assert "result" and "tweets" in response.json(), "Неверный формат ответа"
    assert response.json()["result"], "Неверный результат ответа"
    assert isinstance(response.json()["tweets"], list), "Неверный формат данных"
    if response.json()["tweets"]:
        assert list(response.json()["tweets"][0].keys()) == [
            "id",
            "content",
            "attachments",
            "author",
            "likes",
        ], "Неверный формат данных"


@pytest.mark.asyncio
@pytest.mark.parametrize("route", ["/api/tweets", "/api/tweets/1/likes"])
async def test_authorization_for_post_methods(client: AsyncClient, route: str):
    """Check for authorization for posting a tweet and a like."""

    response = await client.post(route, headers={"api-key": "incorrect-key"})
    assert response.status_code == 401, "Ошибка авторизации"
    assert "detail" in response.json(), "Неверный формат ответа"
    assert (
        response.json()["detail"] == "Access is denied for unauthorized users"
    ), "Неверное сообщение об ошибке"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data",
    [
        {"tweet_data": "test"},
        {"tweet_data": "test", "tweet_media_ids": [1]},
    ],
)
async def test_post_tweet(client: AsyncClient, data: dict):
    """
    Check for correct posting a tweet.

    Case 1: posting without media.
    Case 2: posting with media list.
    """

    response = await client.post("/api/tweets", headers={"api-key": "test"}, json=data)
    assert response.status_code == 201, "Запрос не выполнен"
    assert "result" and "tweet_id" in response.json(), "Неверный формат ответа"
    assert response.json()["result"], "Неверный результат ответа"
    assert response.json()["tweet_id"] == 2, "Неправильный id твита"


@pytest.mark.asyncio
@pytest.mark.parametrize("route", ["/api/tweets/1", "/api/tweets/1/likes"])
async def test_authorization_for_delete_methods(client: AsyncClient, route: str):
    """Check authorization for deleting a tweet or a like."""

    response = await client.delete(route, headers={"api-key": "incorrect-key"})
    assert response.status_code == 401, "Ошибка авторизации"
    assert "detail" in response.json(), "Неверный формат ответа"
    assert (
        response.json()["detail"] == "Access is denied for unauthorized users"
    ), "Неверное сообщение об ошибке"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("route", "header"),
    [
        ("/api/tweets/1", {"api-key": "admin"}),
        ("/api/tweets/1/likes", {"api-key": "test"}),
    ],
)
async def test_correct_delete_methods(client: AsyncClient, route: str, header: dict):
    """Check for status 200 when deleting own tweet or like."""

    response = await client.delete(route, headers=header)
    assert response.status_code == 200, "Запрос не выполнен"
    assert "result" in response.json(), "Неверный формат ответа"
    assert response.json()["result"], "Неверный результат ответа"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("route", "header"),
    [
        ("/api/tweets/1", {"api-key": "test"}),
        ("/api/tweets/1/likes", {"api-key": "Elon1234"}),
    ],
)
async def test_delete_methods_with_bad_request(
    client: AsyncClient, route: str, header: dict
):
    """
    Check for status 400 when call delete methods.

    Case 1: Delete someone else tweet.
    Case2: Delete a like, if someone didn't post a like before that.
    """

    response = await client.delete(route, headers=header)
    assert response.status_code == 400, "Неправильные параметры запроса"
    assert "message" in response.json(), "Неверный формат ответа"


@pytest.mark.asyncio
async def test_delete_nonexistent_tweet(client: AsyncClient):
    """Check status 404 if trying to delete a nonexistent tweet."""

    response = await client.delete("/api/tweets/2", headers={"api-key": "test"})
    assert response.status_code == 404, "Удаление несуществующего твита"
    assert "message" in response.json(), "Неверный формат ответа"
    assert "не найден" in response.json()["message"], "Неправильное сообщение"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("route", "header"),
    [
        ("/api/tweets/2", {"api-key": "test"}),
        ("/api/tweets/2/likes", {"api-key": "test"}),
    ],
)
async def test_delete_methods_on_nonexistent_item(
    client: AsyncClient, route: str, header: dict
):
    """
    Check status 404 if trying to delete a nonexistent item.

    Case 1: Deleting a nonexistent tweet.
    Case 2: Deleting a like from nonexistent tweet.
    """

    response = await client.delete(route, headers=header)
    assert response.status_code == 404, "Удаление несуществующего объекта"
    assert "message" in response.json(), "Неверный формат ответа"
    assert "не найден" in response.json()["message"], "Неправильное сообщение"


@pytest.mark.asyncio
async def test_post_like(client: AsyncClient):
    """Check for liking a tweet."""

    response = await client.post("/api/tweets/1/likes", headers={"api-key": "Elon1234"})
    assert response.status_code == 201, "Запрос не выполнен"
    assert "result" in response.json(), "Неверный формат ответа"
    assert response.json()["result"], "Неверный результат ответа"


@pytest.mark.asyncio
async def test_like_own_tweet(client: AsyncClient):
    """Check for liking own tweet."""

    response = await client.post("/api/tweets/1/likes", headers={"api-key": "admin"})
    assert response.status_code == 400, "Неправильные параметры запроса"
    assert "message" in response.json(), "Неверный формат ответа"
    assert (
        "Нельзя поставить лайк" in response.json()["message"]
    ), "Неверный результат ответа"


@pytest.mark.asyncio
async def test_like_nonexistent_tweet(client: AsyncClient):
    """Check status 404 if trying to like a nonexistent tweet."""

    response = await client.post("/api/tweets/2/likes", headers={"api-key": "test"})
    assert response.status_code == 404, "Запрос на несуществующий твит"
    assert "message" in response.json(), "Неверный формат ответа"
    assert "не найден" in response.json()["message"], "Неправильное сообщение"
