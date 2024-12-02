from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from src.services.SQLite.index import Base
from datetime import datetime

class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False, unique=True, index=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)
    status = Column(Enum("open", "closed", "under_review"), nullable=False, default='under_review')
    
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Link to the User (Owner)
    
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True, index=True)
    website = Column(String, nullable=True)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    owner = relationship("User", back_populates="restaurants")
    products = relationship("Product", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")
