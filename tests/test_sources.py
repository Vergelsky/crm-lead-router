import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_source(client: AsyncClient):
    """Тест создания источника."""
    response = await client.post(
        "/api/v1/sources",
        json={
            "name": "Telegram Bot #1",
            "description": "Основной бот"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Telegram Bot #1"
    assert data["description"] == "Основной бот"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_sources(client: AsyncClient):
    """Тест получения списка источников."""
    # Создаём источник
    await client.post(
        "/api/v1/sources",
        json={"name": "Тестовый источник", "description": "Описание"}
    )
    
    # Получаем список
    response = await client.get("/api/v1/sources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_set_source_distribution(client: AsyncClient):
    """Тест настройки распределения для источника."""
    # Создаём операторов
    op1_response = await client.post(
        "/api/v1/operators",
        json={"name": "Оператор 1", "is_active": True, "max_load": 10}
    )
    op2_response = await client.post(
        "/api/v1/operators",
        json={"name": "Оператор 2", "is_active": True, "max_load": 10}
    )
    op1_id = op1_response.json()["id"]
    op2_id = op2_response.json()["id"]
    
    # Создаём источник
    source_response = await client.post(
        "/api/v1/sources",
        json={"name": "Бот для распределения"}
    )
    source_id = source_response.json()["id"]
    
    # Настраиваем распределение
    response = await client.post(
        f"/api/v1/sources/{source_id}/distribution",
        json={
            "operator_weights": [
                {"operator_id": op1_id, "source_id": source_id, "weight": 10},
                {"operator_id": op2_id, "source_id": source_id, "weight": 30}
            ]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_source_distribution(client: AsyncClient):
    """Тест получения конфигурации распределения."""
    # Создаём оператора и источник
    op_response = await client.post(
        "/api/v1/operators",
        json={"name": "Оператор", "is_active": True, "max_load": 10}
    )
    op_id = op_response.json()["id"]
    
    source_response = await client.post(
        "/api/v1/sources",
        json={"name": "Источник"}
    )
    source_id = source_response.json()["id"]
    
    # Настраиваем распределение
    await client.post(
        f"/api/v1/sources/{source_id}/distribution",
        json={
            "operator_weights": [
                {"operator_id": op_id, "source_id": source_id, "weight": 50}
            ]
        }
    )
    
    # Получаем конфигурацию
    response = await client.get(f"/api/v1/sources/{source_id}/distribution")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["operator_id"] == op_id
    assert data[0]["weight"] == 50

