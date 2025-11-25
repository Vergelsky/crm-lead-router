from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.schemas import (
    OperatorCreate, OperatorUpdate, OperatorResponse
)
from app.infrastructure.repositories import OperatorRepository

router = APIRouter(prefix="/operators", tags=["operators"])


@router.post("", response_model=OperatorResponse, status_code=status.HTTP_201_CREATED)
async def create_operator(
    operator_data: OperatorCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать оператора."""
    repo = OperatorRepository(db)
    operator = await repo.create(
        name=operator_data.name,
        is_active=operator_data.is_active,
        max_load=operator_data.max_load
    )
    return operator


@router.get("", response_model=List[OperatorResponse])
async def get_operators(db: AsyncSession = Depends(get_db)):
    """Получить список всех операторов."""
    repo = OperatorRepository(db)
    operators = await repo.get_all()
    return operators


@router.get("/{operator_id}", response_model=OperatorResponse)
async def get_operator(
    operator_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить оператора по ID."""
    repo = OperatorRepository(db)
    operator = await repo.get_by_id(operator_id)
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оператор не найден"
        )
    return operator


@router.patch("/{operator_id}", response_model=OperatorResponse)
async def update_operator(
    operator_id: int,
    operator_data: OperatorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить оператора."""
    repo = OperatorRepository(db)
    operator = await repo.get_by_id(operator_id)
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оператор не найден"
        )
    
    if operator_data.name is not None:
        operator.name = operator_data.name
    if operator_data.is_active is not None:
        operator.is_active = operator_data.is_active
    if operator_data.max_load is not None:
        operator.max_load = operator_data.max_load
    
    operator = await repo.update(operator)
    return operator

