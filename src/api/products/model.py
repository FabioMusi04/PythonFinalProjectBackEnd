from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.services.SQLite.index import Base
from datetime import datetime

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    status = Column(Enum("available", "out_of_stock", "coming_soon"), nullable=False, default='available')
    discount = Column(Integer, nullable=True)
    image = Column(String, nullable=True)
    visible = Column(Boolean, nullable=False, default=True)
    #category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)  # Link to the Category
    
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)  # Link to the Restaurant
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)  # Link to the Category
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="products", uselist=False)
    orders = relationship("Order", secondary="order_items", back_populates="products")
    category = relationship("Category", back_populates="products", uselist=False)