from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from src.services.SQLite.index import Base
from datetime import datetime
from src.api.orderItems.model import order_items

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Link to the User (customer)
    status = Column(Enum("pending", "completed", "canceled"), nullable=False, default='pending')
    total_price = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)

    # Relationships
    customer = relationship("User", back_populates="orders", uselist=False)
    products = relationship("Product", secondary=order_items, back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")