from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.schemas import (
    ContactCreate, ContactResponse, ContactWithDetails, LeadWithContacts,
    DistributionStats
)
from app.infrastructure.repositories import (
    LeadRepository, ContactRepository, SourceRepository
)
from app.services.distribution_service import DistributionService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=ContactWithDetails, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Зарегистрировать обращение лида.
    
    Система автоматически:
    1. Найдёт или создаст лида по предоставленным данным
    2. Выберет оператора с учётом весов и лимитов
    3. Создаст обращение
    """
    # Проверяем существование источника
    source_repo = SourceRepository(db)
    source = await source_repo.get_by_id(contact_data.source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Источник не найден"
        )
    
    # Находим или создаём лида
    lead_repo = LeadRepository(db)
    lead = await lead_repo.find_or_create(
        external_id=contact_data.lead_external_id,
        phone=contact_data.lead_phone,
        email=contact_data.lead_email,
        name=contact_data.lead_name
    )
    
    # Выбираем оператора
    distribution_service = DistributionService(db)
    operator = await distribution_service.select_operator(contact_data.source_id)
    
    # Создаём обращение
    contact_repo = ContactRepository(db)
    contact = await contact_repo.create(
        lead_id=lead.id,
        source_id=contact_data.source_id,
        operator_id=operator.id if operator else None,
        message=contact_data.message,
        status="active"
    )
    
    # Загружаем связанные данные для ответа
    contact = await contact_repo.get_by_id(contact.id)
    return contact


@router.get("", response_model=List[ContactWithDetails])
async def get_contacts(db: AsyncSession = Depends(get_db)):
    """Получить список всех обращений."""
    contact_repo = ContactRepository(db)
    contacts = await contact_repo.get_all()
    return contacts


@router.get("/{contact_id}", response_model=ContactWithDetails)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить обращение по ID."""
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_by_id(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Обращение не найдено"
        )
    return contact


@router.get("/stats/distribution", response_model=List[DistributionStats])
async def get_distribution_stats(db: AsyncSession = Depends(get_db)):
    """Получить статистику распределения обращений по операторам и источникам."""
    contact_repo = ContactRepository(db)
    stats = await contact_repo.get_distribution_stats()
    return [
        DistributionStats(**stat) for stat in stats
    ]

