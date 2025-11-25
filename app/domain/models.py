from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Operator(Base):
    """Модель оператора."""
    
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    max_load = Column(Integer, default=10, nullable=False)  # Лимит активных обращений
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    source_weights = relationship("OperatorSourceWeight", back_populates="operator", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="operator")


class Source(Base):
    """Модель источника (бота)."""
    
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    operator_weights = relationship("OperatorSourceWeight", back_populates="source", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="source")


class OperatorSourceWeight(Base):
    """Модель веса оператора для источника (компетенция)."""
    
    __tablename__ = "operator_source_weights"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    weight = Column(Integer, nullable=False, default=1)  # Вес для распределения
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    operator = relationship("Operator", back_populates="source_weights")
    source = relationship("Source", back_populates="operator_weights")
    
    # Уникальность пары оператор-источник
    __table_args__ = (
        UniqueConstraint('operator_id', 'source_id', name='uq_operator_source'),
    )


class Lead(Base):
    """Модель лида (клиента)."""
    
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, nullable=True, index=True)  # Внешний идентификатор (телефон, email и т.п.)
    phone = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    contacts = relationship("Contact", back_populates="lead", cascade="all, delete-orphan")


class Contact(Base):
    """Модель обращения (контакта) лида."""
    
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, default="active", nullable=False)  # active, closed, etc.
    message = Column(String, nullable=True)  # Дополнительные данные обращения
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")

