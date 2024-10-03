from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from src.services.SQLite.index import Base
from datetime import datetime

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="categories")
    products = relationship("Product", back_populates="category")