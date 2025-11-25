import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_contact_with_auto_distribution(client: AsyncClient):
    """Тест создания обращения с автоматическим распределением."""
    # Создаём оператора
    op_response = await client.post(
        "/api/v1/operators",
        json={"name": "Оператор для теста", "is_active": True, "max_load": 10}
    )
    op_id = op_response.json()["id"]
    
    # Создаём источник
    source_response = await client.post(
        "/api/v1/sources",
        json={"name": "Тестовый бот"}
    )
    source_id = source_response.json()["id"]
    
    # Настраиваем распределение
    await client.post(
        f"/api/v1/sources/{source_id}/distribution",
        json={
            "operator_weights": [
                {"operator_id": op_id, "source_id": source_id, "weight": 100}
            ]
        }
    )
    
    # Создаём обращение
    response = await client.post(
        "/api/v1/contacts",
        json={
            "source_id": source_id,
            "lead_phone": "+79001234567",
            "lead_name": "Тестовый лид",
            "message": "Тестовое сообщение"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["source_id"] == source_id
    assert data["operator_id"] == op_id  # Оператор должен быть назначен
    assert "lead" in data
    assert data["lead"]["phone"] == "+79001234567"
    assert data["lead"]["name"] == "Тестовый лид"


@pytest.mark.asyncio
async def test_create_contact_without_operator(client: AsyncClient):
    """Тест создания обращения без доступных операторов."""
    # Создаём источник без операторов
    source_response = await client.post(
        "/api/v1/sources",
        json={"name": "Бот без операторов"}
    )
    source_id = source_response.json()["id"]
    
    # Создаём обращение (оператор не будет назначен)
    response = await client.post(
        "/api/v1/contacts",
        json={
            "source_id": source_id,
            "lead_phone": "+79001234568",
            "lead_name": "Лид без оператора"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["operator_id"] is None  # Оператор не назначен


@pytest.mark.asyncio
async def test_get_contacts(client: AsyncClient):
    """Тест получения списка обращений."""
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
    
    await client.post(
        f"/api/v1/sources/{source_id}/distribution",
        json={
            "operator_weights": [
                {"operator_id": op_id, "source_id": source_id, "weight": 100}
            ]
        }
    )
    
    # Создаём обращение
    await client.post(
        "/api/v1/contacts",
        json={
            "source_id": source_id,
            "lead_phone": "+79001234569"
        }
    )
    
    # Получаем список
    response = await client.get("/api/v1/contacts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_distribution_stats(client: AsyncClient):
    """Тест получения статистики распределения."""
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
    
    await client.post(
        f"/api/v1/sources/{source_id}/distribution",
        json={
            "operator_weights": [
                {"operator_id": op_id, "source_id": source_id, "weight": 100}
            ]
        }
    )
    
    # Создаём обращение
    await client.post(
        "/api/v1/contacts",
        json={
            "source_id": source_id,
            "lead_phone": "+79001234570"
        }
    )
    
    # Получаем статистику
    response = await client.get("/api/v1/contacts/stats/distribution")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

