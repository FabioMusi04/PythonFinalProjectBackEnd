from fastapi import APIRouter, Depends
from sqlalchemy import select
from src.services.SQLite.index import async_session
from src.api.users.model import User
import src.services.auth.index as auth

app = APIRouter()

@app.get("/users", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def get_users(skip: int = 0, limit: int = 100):
    async with async_session() as conn:
        stmt = select(User).offset(skip).limit(limit)
        result = conn.execute(stmt)
        users = result.fetchall()
        return users

@app.get("/users/{user_id}", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def get_user(user_id: int):
    async with async_session() as conn:
        stmt = select(User).where(User.id == user_id)
        result = conn.execute(stmt)
        user = result.fetchone()
        return user

@app.put("/users/{user_id}", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def update_user(user_id: int, user):
    async with async_session() as conn:
        stmt = select(User).where(User.id == user_id)
        result = conn.execute(stmt)
        user = result.fetchone()
        user.update(user)
        return user
    
@app.post("/users", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def create_user(user):
    async with async_session() as conn:
        stmt = User.insert().values(user)
        result = conn.execute(stmt)
        return result.inserted_primary_key

@app.delete("/users/{user_id}", dependencies=[Depends(auth.JWTBearer(True))], tags=["users"])
async def delete_user(user_id: int):
    async with async_session() as conn:
        stmt = User.delete().where(User.id == user_id)
        result = conn.execute(stmt)
        return result.rowcount
    
