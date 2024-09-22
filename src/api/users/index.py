from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.services.SQLite.index import async_session
from src.api.users.model import User
import src.services.auth.index as auth

app = APIRouter()

class UserUpdate(BaseModel):
    name: str
    email: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

@app.get("/users", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def get_users(skip: int = 0, limit: int = 100):
    async with async_session() as conn:
        stmt = select(User).offset(skip).limit(limit)
        result = await conn.execute(stmt)
        users = result.scalars().all()
        return users

@app.get("/users/{user_id}", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def get_user(user_id: int):
    async with async_session() as conn:
        stmt = select(User).where(User.id == user_id)
        result = await conn.execute(stmt)
        user = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

@app.put("/users/{user_id}", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def update_user(user_id: int, user_update: UserUpdate):
    async with async_session() as conn:
        stmt = select(User).where(User.id == user_id)
        result = await conn.execute(stmt)
        user = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        stmt = update(User).where(User.id == user_id).values(**user_update.dict())
        await conn.execute(stmt)
        await conn.commit()
        return {"message": "User updated successfully"}

@app.put("/users/me", dependencies=[Depends(auth.JWTBearer())], tags=["users"])
async def update_user_me(user_update: UserUpdate, token: dict = Depends(auth.JWTBearer())):
    async with async_session() as conn:
        stmt = select(User).where(User.id == token["id"])
        result = await conn.execute(stmt)
        user = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        stmt = update(User).where(User.id == token["id"]).values(**user_update.dict())
        await conn.execute(stmt)
        await conn.commit()
        return {"message": "User updated successfully"}

@app.post("/users", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def create_user(user_create: UserCreate):
    async with async_session() as conn:
        stmt = insert(User).values(**user_create.dict())
        result = await conn.execute(stmt)
        await conn.commit()
        return {"id": result.inserted_primary_key}

@app.delete("/users/{user_id}", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def delete_user(user_id: int):
    async with async_session() as conn:
        stmt = delete(User).where(User.id == user_id)
        result = await conn.execute(stmt)
        await conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
