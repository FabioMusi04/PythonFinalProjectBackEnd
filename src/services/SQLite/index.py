from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.api.users.model import Base

sync_engine = create_engine("sqlite:///./test.db", echo=True)

async_engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=True)

async_session = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

Base.metadata.create_all(bind=sync_engine)