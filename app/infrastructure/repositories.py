from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models import (
    Operator, Source, OperatorSourceWeight, Lead, Contact
)


class OperatorRepository:
    """Репозиторий для работы с операторами."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, name: str, is_active: bool = True, max_load: int = 10) -> Operator:
        """Создать оператора."""
        operator = Operator(name=name, is_active=is_active, max_load=max_load)
        self.session.add(operator)
        await self.session.commit()
        await self.session.refresh(operator)
        return operator
    
    async def get_by_id(self, operator_id: int) -> Optional[Operator]:
        """Получить оператора по ID."""
        result = await self.session.execute(
            select(Operator).where(Operator.id == operator_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Operator]:
        """Получить всех операторов."""
        result = await self.session.execute(select(Operator))
        return list(result.scalars().all())
    
    async def update(self, operator: Operator) -> Operator:
        """Обновить оператора."""
        await self.session.commit()
        await self.session.refresh(operator)
        return operator
    
    async def get_active_operators_for_source(
        self, source_id: int
    ) -> List[Operator]:
        """Получить активных операторов для источника с их весами."""
        result = await self.session.execute(
            select(Operator)
            .join(OperatorSourceWeight)
            .where(
                and_(
                    OperatorSourceWeight.source_id == source_id,
                    Operator.is_active == True
                )
            )
            .options(selectinload(Operator.source_weights))
        )
        return list(result.scalars().all())
    
    async def get_operator_load(self, operator_id: int) -> int:
        """Получить текущую нагрузку оператора (количество активных обращений)."""
        result = await self.session.execute(
            select(func.count(Contact.id))
            .where(
                and_(
                    Contact.operator_id == operator_id,
                    Contact.status == "active"
                )
            )
        )
        return result.scalar() or 0


class SourceRepository:
    """Репозиторий для работы с источниками."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, name: str, description: Optional[str] = None) -> Source:
        """Создать источник."""
        source = Source(name=name, description=description)
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return source
    
    async def get_by_id(self, source_id: int) -> Optional[Source]:
        """Получить источник по ID."""
        result = await self.session.execute(
            select(Source).where(Source.id == source_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Source]:
        """Получить источник по имени."""
        result = await self.session.execute(
            select(Source).where(Source.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Source]:
        """Получить все источники."""
        result = await self.session.execute(select(Source))
        return list(result.scalars().all())
    
    async def update(self, source: Source) -> Source:
        """Обновить источник."""
        await self.session.commit()
        await self.session.refresh(source)
        return source


class OperatorSourceWeightRepository:
    """Репозиторий для работы с весами операторов по источникам."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self, operator_id: int, source_id: int, weight: int
    ) -> OperatorSourceWeight:
        """Создать или обновить вес оператора для источника."""
        # Проверяем, существует ли уже такая связь
        result = await self.session.execute(
            select(OperatorSourceWeight).where(
                and_(
                    OperatorSourceWeight.operator_id == operator_id,
                    OperatorSourceWeight.source_id == source_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.weight = weight
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        
        weight_obj = OperatorSourceWeight(
            operator_id=operator_id,
            source_id=source_id,
            weight=weight
        )
        self.session.add(weight_obj)
        await self.session.commit()
        await self.session.refresh(weight_obj)
        return weight_obj
    
    async def get_weights_for_source(
        self, source_id: int
    ) -> List[OperatorSourceWeight]:
        """Получить все веса операторов для источника."""
        result = await self.session.execute(
            select(OperatorSourceWeight)
            .where(OperatorSourceWeight.source_id == source_id)
            .options(
                selectinload(OperatorSourceWeight.operator),
                selectinload(OperatorSourceWeight.source)
            )
        )
        return list(result.scalars().all())
    
    async def delete(self, weight_id: int) -> bool:
        """Удалить вес."""
        result = await self.session.execute(
            select(OperatorSourceWeight).where(OperatorSourceWeight.id == weight_id)
        )
        weight = result.scalar_one_or_none()
        if weight:
            await self.session.delete(weight)
            await self.session.commit()
            return True
        return False


class LeadRepository:
    """Репозиторий для работы с лидами."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        external_id: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None
    ) -> Lead:
        """Создать лида."""
        lead = Lead(
            external_id=external_id,
            phone=phone,
            email=email,
            name=name
        )
        self.session.add(lead)
        await self.session.commit()
        await self.session.refresh(lead)
        return lead
    
    async def find_or_create(
        self,
        external_id: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None
    ) -> Lead:
        """Найти существующего лида или создать нового."""
        # Ищем по external_id, phone или email
        conditions = []
        if external_id:
            conditions.append(Lead.external_id == external_id)
        if phone:
            conditions.append(Lead.phone == phone)
        if email:
            conditions.append(Lead.email == email)
        
        if conditions:
            result = await self.session.execute(
                select(Lead).where(
                    and_(*conditions)
                )
            )
            lead = result.scalar_one_or_none()
            if lead:
                # Обновляем данные, если они изменились
                if name and not lead.name:
                    lead.name = name
                if phone and not lead.phone:
                    lead.phone = phone
                if email and not lead.email:
                    lead.email = email
                if external_id and not lead.external_id:
                    lead.external_id = external_id
                await self.session.commit()
                await self.session.refresh(lead)
                return lead
        
        # Создаём нового лида
        return await self.create(
            external_id=external_id,
            phone=phone,
            email=email,
            name=name
        )
    
    async def get_by_id(self, lead_id: int) -> Optional[Lead]:
        """Получить лида по ID."""
        result = await self.session.execute(
            select(Lead)
            .where(Lead.id == lead_id)
            .options(selectinload(Lead.contacts))
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Lead]:
        """Получить всех лидов."""
        result = await self.session.execute(
            select(Lead).options(selectinload(Lead.contacts))
        )
        return list(result.scalars().all())


class ContactRepository:
    """Репозиторий для работы с обращениями."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        lead_id: int,
        source_id: int,
        operator_id: Optional[int] = None,
        message: Optional[str] = None,
        status: str = "active"
    ) -> Contact:
        """Создать обращение."""
        contact = Contact(
            lead_id=lead_id,
            source_id=source_id,
            operator_id=operator_id,
            message=message,
            status=status
        )
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact
    
    async def get_by_id(self, contact_id: int) -> Optional[Contact]:
        """Получить обращение по ID."""
        result = await self.session.execute(
            select(Contact)
            .where(Contact.id == contact_id)
            .options(
                selectinload(Contact.lead),
                selectinload(Contact.operator),
                selectinload(Contact.source)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Contact]:
        """Получить все обращения."""
        result = await self.session.execute(
            select(Contact)
            .options(
                selectinload(Contact.lead),
                selectinload(Contact.operator),
                selectinload(Contact.source)
            )
        )
        return list(result.scalars().all())
    
    async def get_distribution_stats(self) -> List[dict]:
        """Получить статистику распределения обращений."""
        result = await self.session.execute(
            select(
                Source.id.label("source_id"),
                Source.name.label("source_name"),
                Operator.id.label("operator_id"),
                Operator.name.label("operator_name"),
                func.count(Contact.id).label("contacts_count")
            )
            .select_from(Contact)
            .join(Source, Contact.source_id == Source.id)
            .outerjoin(Operator, Contact.operator_id == Operator.id)
            .group_by(Source.id, Source.name, Operator.id, Operator.name)
        )
        return [
            {
                "source_id": row.source_id,
                "source_name": row.source_name,
                "operator_id": row.operator_id,
                "operator_name": row.operator_name,
                "contacts_count": row.contacts_count
            }
            for row in result.all()
        ]

