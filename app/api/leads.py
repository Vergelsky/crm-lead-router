from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.schemas import LeadResponse, LeadWithContacts
from app.infrastructure.repositories import LeadRepository

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=List[LeadWithContacts])
async def get_leads(db: AsyncSession = Depends(get_db)):
    """Получить список всех лидов с их обращениями."""
    lead_repo = LeadRepository(db)
    leads = await lead_repo.get_all()
    return leads


@router.get("/{lead_id}", response_model=LeadWithContacts)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить лида по ID с его обращениями."""
    lead_repo = LeadRepository(db)
    lead = await lead_repo.get_by_id(lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Лид не найден"
        )
    return lead

