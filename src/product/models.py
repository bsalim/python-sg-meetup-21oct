from src.models import Base
from sqlalchemy import (
    Column,
    Boolean,
    DateTime,
    DECIMAL,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    UniqueConstraint,
    UUID,
    select
)
from sqlalchemy.orm import joinedload
from typing import Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Category(Base):
    __tablename__ = 'categories'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(100), nullable=False)
    description = mapped_column(String)
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = 'products'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id = mapped_column(UUID)
    name = mapped_column(String(255))
    demo_url = mapped_column(String(255))
    category_id = mapped_column(Integer, ForeignKey('categories.id'), nullable=True)
    
    created_at = mapped_column(DateTime, default=datetime.now)
    updated_at = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = mapped_column(Boolean, default=True)

    #vendor = relationship("Vendor", back_populates="products")
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    # order_items = relationship("OrderItem", back_populates="product")
    
    @classmethod
    async def find(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()
    
    @classmethod
    async def find_all(cls, database_session: AsyncSession):
        _stmt = select(cls).options(joinedload(Product.category))
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

