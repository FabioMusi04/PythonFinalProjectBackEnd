from sqlalchemy import Column, Integer, String, DateTime, Enum
from src.services.SQLite.index import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):  # Inherit from Base
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum("user", "admin", "owner"), nullable=False, default='user')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Additional fields
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    profile_picture = Column(String, nullable=True)

    # Relationships
    restaurants = relationship("Restaurant", back_populates="owner")
    orders = relationship("Order", back_populates="customer")