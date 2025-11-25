from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.schemas import (
    SourceCreate, SourceUpdate, SourceResponse, SourceDistributionConfig,
    OperatorSourceWeightResponse
)
from app.infrastructure.repositories import (
    SourceRepository, OperatorSourceWeightRepository
)

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: SourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать источник."""
    repo = SourceRepository(db)
    # Проверяем, не существует ли уже источник с таким именем
    existing = await repo.get_by_name(source_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Источник с таким именем уже существует"
        )
    
    source = await repo.create(
        name=source_data.name,
        description=source_data.description
    )
    return source


@router.get("", response_model=List[SourceResponse])
async def get_sources(db: AsyncSession = Depends(get_db)):
    """Получить список всех источников."""
    repo = SourceRepository(db)
    sources = await repo.get_all()
    return sources


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить источник по ID."""
    repo = SourceRepository(db)
    source = await repo.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Источник не найден"
        )
    return source


@router.patch("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source_data: SourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить источник."""
    repo = SourceRepository(db)
    source = await repo.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Источник не найден"
        )
    
    if source_data.name is not None:
        # Проверяем уникальность имени
        existing = await repo.get_by_name(source_data.name)
        if existing and existing.id != source_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Источник с таким именем уже существует"
            )
        source.name = source_data.name
    
    if source_data.description is not None:
        source.description = source_data.description
    
    source = await repo.update(source)
    return source


@router.post(
    "/{source_id}/distribution",
    response_model=List[OperatorSourceWeightResponse],
    status_code=status.HTTP_201_CREATED
)
async def set_source_distribution(
    source_id: int,
    config: SourceDistributionConfig,
    db: AsyncSession = Depends(get_db)
):
    """Настроить распределение операторов для источника."""
    source_repo = SourceRepository(db)
    source = await source_repo.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Источник не найден"
        )
    
    weight_repo = OperatorSourceWeightRepository(db)
    created_weights = []
    
    for weight_data in config.operator_weights:
        if weight_data.source_id != source_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"source_id в весе должен совпадать с source_id в URL ({source_id})"
            )
        
        weight = await weight_repo.create(
            operator_id=weight_data.operator_id,
            source_id=weight_data.source_id,
            weight=weight_data.weight
        )
        created_weights.append(weight)
    
    return created_weights


@router.get(
    "/{source_id}/distribution",
    response_model=List[OperatorSourceWeightResponse]
)
async def get_source_distribution(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить конфигурацию распределения для источника."""
    source_repo = SourceRepository(db)
    source = await source_repo.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Источник не найден"
        )
    
    weight_repo = OperatorSourceWeightRepository(db)
    weights = await weight_repo.get_weights_for_source(source_id)
    return weights

