import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_leads(client: AsyncClient):
    """Тест получения списка лидов."""
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
    
    # Создаём обращение (это создаст лида)
    await client.post(
        "/api/v1/contacts",
        json={
            "source_id": source_id,
            "lead_phone": "+79001234571",
            "lead_name": "Тестовый лид"
        }
    )
    
    # Получаем список лидов
    response = await client.get("/api/v1/leads")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "contacts" in data[0]  # Лиды должны содержать обращения


@pytest.mark.asyncio
async def test_get_lead_by_id(client: AsyncClient):
    """Тест получения лида по ID."""
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
    contact_response = await client.post(
        "/api/v1/contacts",
        json={
            "source_id": source_id,
            "lead_phone": "+79001234572",
            "lead_name": "Лид для поиска"
        }
    )
    lead_id = contact_response.json()["lead"]["id"]
    
    # Получаем лида по ID
    response = await client.get(f"/api/v1/leads/{lead_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lead_id
    assert data["phone"] == "+79001234572"
    assert "contacts" in data
    assert len(data["contacts"]) > 0


@pytest.mark.asyncio
async def test_lead_deduplication(client: AsyncClient):
    """Тест дедупликации лидов (один лид с несколькими обращениями)."""
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
    
    phone = "+79001234573"
    
    # Создаём первое обращение
    contact1_response = await client.post(
        "/api/v1/contacts",
        json={
            "source_id": source_id,
            "lead_phone": phone,
            "lead_name": "Один лид"
        }
    )
    lead_id_1 = contact1_response.json()["lead"]["id"]
    
    # Создаём второе обращение с тем же телефоном
    contact2_response = await client.post(
        "/api/v1/contacts",
        json={
            "source_id": source_id,
            "lead_phone": phone,
            "lead_name": "Тот же лид"
        }
    )
    lead_id_2 = contact2_response.json()["lead"]["id"]
    
    # Оба обращения должны быть связаны с одним лидом
    assert lead_id_1 == lead_id_2
    
    # Проверяем, что у лида два обращения
    response = await client.get(f"/api/v1/leads/{lead_id_1}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["contacts"]) == 2

