from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


import os
from dotenv import load_dotenv 
load_dotenv() 

sync_engine = create_engine((os.getenv("ENGINE_PATH_DB")), echo=True)

async_engine = create_async_engine((os.getenv("ASYNC_ENGINE_PATH_DB")), echo=True)

async_session = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

async def reset_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


