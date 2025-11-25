from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# Операторы
class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = Field(default=10, ge=1)


class OperatorCreate(OperatorBase):
    pass


class OperatorUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    max_load: Optional[int] = Field(None, ge=1)


class OperatorResponse(OperatorBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# Источники
class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SourceResponse(SourceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# Веса операторов по источникам
class OperatorSourceWeightBase(BaseModel):
    operator_id: int
    source_id: int
    weight: int = Field(default=1, ge=1)


class OperatorSourceWeightCreate(OperatorSourceWeightBase):
    pass


class OperatorSourceWeightResponse(OperatorSourceWeightBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# Настройка распределения для источника
class SourceDistributionConfig(BaseModel):
    """Конфигурация распределения операторов для источника."""
    operator_weights: List[OperatorSourceWeightCreate]


# Лиды
class LeadBase(BaseModel):
    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Обращения
class ContactBase(BaseModel):
    source_id: int
    message: Optional[str] = None


class ContactCreate(ContactBase):
    """Создание обращения с автоматическим определением лида."""
    # Идентификаторы для поиска/создания лида
    lead_external_id: Optional[str] = None
    lead_phone: Optional[str] = None
    lead_email: Optional[str] = None
    lead_name: Optional[str] = None


class ContactResponse(ContactBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    lead_id: int
    operator_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContactWithDetails(ContactResponse):
    """Обращение с деталями лида, оператора и источника."""
    model_config = ConfigDict(from_attributes=True)
    
    lead: LeadResponse
    operator: Optional[OperatorResponse] = None
    source: SourceResponse


# Статистика
class DistributionStats(BaseModel):
    """Статистика распределения обращений."""
    source_id: int
    source_name: str
    operator_id: Optional[int]
    operator_name: Optional[str]
    contacts_count: int


class LeadWithContacts(LeadResponse):
    """Лид с его обращениями."""
    model_config = ConfigDict(from_attributes=True)
    
    contacts: List[ContactResponse]

