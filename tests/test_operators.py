import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_operator(client: AsyncClient):
    """Тест создания оператора."""
    response = await client.post(
        "/api/v1/operators",
        json={
            "name": "Иван Иванов",
            "is_active": True,
            "max_load": 10
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Иван Иванов"
    assert data["is_active"] is True
    assert data["max_load"] == 10
    assert "id" in data


@pytest.mark.asyncio
async def test_get_operators(client: AsyncClient):
    """Тест получения списка операторов."""
    # Создаём оператора
    await client.post(
        "/api/v1/operators",
        json={"name": "Тестовый оператор", "is_active": True, "max_load": 5}
    )
    
    # Получаем список
    response = await client.get("/api/v1/operators")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_operator_by_id(client: AsyncClient):
    """Тест получения оператора по ID."""
    # Создаём оператора
    create_response = await client.post(
        "/api/v1/operators",
        json={"name": "Оператор для поиска", "is_active": True, "max_load": 15}
    )
    operator_id = create_response.json()["id"]
    
    # Получаем по ID
    response = await client.get(f"/api/v1/operators/{operator_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == operator_id
    assert data["name"] == "Оператор для поиска"


@pytest.mark.asyncio
async def test_update_operator(client: AsyncClient):
    """Тест обновления оператора."""
    # Создаём оператора
    create_response = await client.post(
        "/api/v1/operators",
        json={"name": "Старое имя", "is_active": True, "max_load": 10}
    )
    operator_id = create_response.json()["id"]
    
    # Обновляем
    response = await client.patch(
        f"/api/v1/operators/{operator_id}",
        json={"name": "Новое имя", "max_load": 20}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Новое имя"
    assert data["max_load"] == 20


@pytest.mark.asyncio
async def test_get_nonexistent_operator(client: AsyncClient):
    """Тест получения несуществующего оператора."""
    response = await client.get("/api/v1/operators/99999")
    assert response.status_code == 404

