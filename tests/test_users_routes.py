import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize("route", ["/api/users/me", "/api/users/1"])
async def test_authorization_for_get_methods(client: AsyncClient, route: str):
    """Check for authorization for getting a current user and a user profile."""

    response = await client.get(route, headers={"api-key": "incorrect-key"})
    assert response.status_code == 401, "Ошибка авторизации"
    assert "detail" in response.json(), "Неверный формат ответа"
    assert response.json()["detail"] == "Access is denied for unauthorized users"


@pytest.mark.asyncio
@pytest.mark.parametrize("route", ["/api/users/me", "/api/users/2"])
async def test_get_current_user(client: AsyncClient, route: str):
    """Check for getting current user."""

    response = await client.get(route, headers={"api-key": "test"})
    assert response.status_code == 200, "Запрос не выполнен"
    assert "result" and "user" in response.json(), "Неверный формат ответа"
    assert response.json()["result"], "Неверный результат ответа"
    if response.json()["user"]:
        assert list(response.json()["user"].keys()) == [
            "id",
            "name",
            "followers",
            "following",
        ], "Неверный формат данных"
    assert (
        response.json()["user"]["id"] == 2
    ), "Возвращен пользователь с неправильным id"


@pytest.mark.asyncio
async def test_get_absent_profile(client: AsyncClient):
    """Check for getting absent user profile."""

    response = await client.get("/api/users/4", headers={"api-key": "test"})
    assert response.status_code == 404, "Операция с несуществующим объектом"
    assert "message" in response.json(), "Неверный формат ответа"
    assert "не найден" in response.json()["message"], "Неправильное сообщение"


@pytest.mark.asyncio
async def test_authorization_when_post_follow(client: AsyncClient):
    """Check for access denied for unauthorized users."""

    response = await client.post(
        "/api/users/1/follow", headers={"api-key": "incorrect-key"}
    )
    assert response.status_code == 401, "Ошибка авторизации"
    assert "detail" in response.json(), "Неверный формат ответа"
    assert response.json()["detail"] == "Access is denied for unauthorized users"


@pytest.mark.asyncio
async def test_correct_post_follow(client: AsyncClient):
    """Check to follow with correct data."""

    response = await client.post("/api/users/1/follow", headers={"api-key": "test"})
    assert response.status_code == 201, "Запрос не выполнен"
    assert "result" in response.json(), "Неверный формат ответа"
    assert response.json()["result"], "Неверный результат ответа"


@pytest.mark.asyncio
async def test_follow_by_absent_user(client: AsyncClient):
    """Check status 404 if trying to follow by absent user."""

    response = await client.post("/api/users/4/follow", headers={"api-key": "test"})
    assert response.status_code == 404, "Операция с несуществующим объектом"
    assert "message" in response.json(), "Неверный формат ответа"
    assert "не найден" in response.json()["message"], "Неправильное сообщение"


@pytest.mark.asyncio
async def test_follow_oneself(client: AsyncClient):
    """Check status 400 if trying to follow by oneself."""

    response = await client.post("/api/users/2/follow", headers={"api-key": "test"})
    assert response.status_code == 400, "Неправильные параметры запроса"
    assert "message" in response.json(), "Неверный формат ответа"
    assert (
        response.json()["message"] == "Вы не можете подписаться на самого себя!"
    ), "Неверное сообщение об ошибке"


@pytest.mark.asyncio
async def test_follow_once_more(client: AsyncClient):
    """Check status 400 if trying to follow once more."""

    response = await client.post("/api/users/3/follow", headers={"api-key": "test"})
    assert response.status_code == 400, "Неправильные параметры запроса"
    assert "message" in response.json(), "Неверный формат ответа"
    assert (
        "Вы уже подписаны" in response.json()["message"]
    ), "Неверное сообщение об ошибке"


@pytest.mark.asyncio
async def test_authorization_when_delete_follow(client: AsyncClient):
    """Check for access denied for unauthorized users."""

    response = await client.delete(
        "/api/users/3/follow", headers={"api-key": "incorrect-key"}
    )
    assert response.status_code == 401, "Ошибка авторизации"
    assert "detail" in response.json(), "Неверный формат ответа"
    assert (
        response.json()["detail"] == "Access is denied for unauthorized users"
    ), "Неверное сообщение об ошибке"


@pytest.mark.asyncio
async def test_success_unfollow(client: AsyncClient):
    """Check for unfollow with correct data."""

    response = await client.delete("/api/users/3/follow", headers={"api-key": "test"})
    assert response.status_code == 200, "Запрос не выполнен"
    assert "result" in response.json(), "Неверный формат ответа"
    assert response.json()["result"], "Неверный результат ответа"


@pytest.mark.asyncio
async def test_unfollow_absent_user(client: AsyncClient):
    """Check status 404 if trying to unfollow on absent user."""

    response = await client.delete("/api/users/4/follow", headers={"api-key": "test"})
    assert response.status_code == 404, "Операция с несуществующим объектом"
    assert "message" in response.json(), "Неверный формат ответа"
    assert "не найден" in response.json()["message"], "Неправильное сообщение"


@pytest.mark.asyncio
async def test_bad_request_when_unfollow(client: AsyncClient):
    """Check for 400 status when unfollow user, someone doesn't follow."""

    response = await client.delete("/api/users/1/follow", headers={"api-key": "test"})
    assert response.status_code == 400, "Неправильные параметры запроса"
    assert "message" in response.json(), "Неверный формат ответа"
    assert "Вы не подписаны" in response.json()["message"], "Неверный результат ответа"
