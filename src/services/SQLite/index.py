from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.api.users.model import Base

import os
from dotenv import load_dotenv 
load_dotenv() 

sync_engine = create_engine((os.getenv("ENGINE_PATH_DB")), echo=True)

async_engine = create_async_engine((os.getenv("ASYNC_ENGINE_PATH_DB")), echo=True)

async_session = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

Base.metadata.create_all(bind=sync_engine)