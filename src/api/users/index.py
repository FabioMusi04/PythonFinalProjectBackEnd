from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, insert, delete
from pydantic import BaseModel
from src.services.SQLite.index import async_session
from src.api.users.model import User
import src.services.auth.index as auth
from sqlalchemy.orm import joinedload
from typing import Optional
from datetime import datetime

app = APIRouter()

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    role: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    profile_picture: Optional[str] = None
    email: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    surname: str
    role: str
    phone_number: Optional[int] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    profile_picture: Optional[str] = None
    email: str
    password: str

@app.get("/users", tags=["users"])
async def get_users(skip: int = 0, limit: int = 100, token: dict = Depends(auth.admin_required)):
    async with async_session() as conn:
        stmt = select(User).offset(skip).limit(limit).options(joinedload(User.restaurants))
        result = await conn.execute(stmt)
        users = result.scalars().all()
        return users

@app.get("/users/{user_id}", tags=["users"])
async def get_user(user_id: int, token: dict = Depends(auth.admin_required)):
    async with async_session() as conn:
        stmt = select(User).where(User.id == user_id).options(joinedload(User.restaurants))
        result = await conn.execute(stmt)
        user = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
@app.put("/users/me", tags=["users"])
async def update_user_me(user_update: UserUpdate, token: dict = Depends(auth.JWTBearer())):
    async with async_session() as conn:
        stmt = select(User).where(User.id == token["id"])
        result = await conn.execute(stmt)
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        stmt = update(User).where(User.id == token["id"]).values(**update_data)
        await conn.execute(stmt)

        user = await conn.execute(select(User).where(User.id == token["id"]))

        await conn.commit()

        return user.scalars().first()


@app.put("/users/{user_id}", tags=["users"])
async def update_user(user_id: int, user_update: UserUpdate, token: dict = Depends(auth.admin_required)):
    async with async_session() as conn:
        stmt = select(User).where(User.id == user_id)
        result = await conn.execute(stmt)
        user = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        stmt = update(User).where(User.id == user_id).values(**user_update.model_dump())
        await conn.execute(stmt)
        await conn.commit()
        return {"message": "User updated successfully"}

@app.post("/users", tags=["users"])
async def create_user(user_create: UserCreate, token: dict = Depends(auth.admin_required)):
    async with async_session() as conn:
        stmt = insert(User).values(**user_create.model_dump())
        result = await conn.execute(stmt)
        await conn.commit()
        return {"id": result.inserted_primary_key}

@app.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int, token: dict = Depends(auth.admin_required)):
    async with async_session() as conn:
        stmt = delete(User).where(User.id == user_id)
        result = await conn.execute(stmt)
        await conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
