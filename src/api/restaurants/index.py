from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, insert, delete
from pydantic import BaseModel
from src.services.SQLite.index import async_session
from src.api.restaurants.model import Restaurant
import src.services.auth.index as auth
from sqlalchemy.orm import joinedload
from typing import Optional

app = APIRouter()

class RestaurantCreate(BaseModel):
    name: str
    address: str
    city: str
    country: str
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    image: Optional[str] = None

class RestaurantUpdate(BaseModel):
    name: str
    address: str
    city: str
    country: str
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "under_review"
    image: Optional[str] = None

@app.get("/restaurants", tags=["restaurants"])
async def get_restaurants(skip: int = 0, limit: int = 100):
    async with async_session() as conn:
        stmt = select(Restaurant).offset(skip).limit(limit).options(joinedload(Restaurant.owner))
        result = await conn.execute(stmt)
        restaurants = result.scalars().all()
        return restaurants
    
@app.get("/restaurants/me", tags=["restaurants"])
async def get_my_restaurants(token: dict = Depends(auth.owner_required)):
    async with async_session() as conn:
        stmt = select(Restaurant).where(Restaurant.owner_id == token["id"]).options(joinedload(Restaurant.owner))
        result = await conn.execute(stmt)
        restaurants = result.scalars().all()
        return restaurants

@app.get("/restaurants/{restaurant_id}", tags=["restaurants"])
async def get_restaurant(restaurant_id: int):
    async with async_session() as conn:
        stmt = select(Restaurant).where(Restaurant.id == restaurant_id).options(joinedload(Restaurant.owner))
        result = await conn.execute(stmt)
        restaurant = result.scalars().first()
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant

@app.post("/restaurants", tags=["restaurants"])
async def create_restaurant(restaurant_create: RestaurantCreate, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        if restaurant_create.status and restaurant_create.status not in ["open", "closed", "under_review"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        stmt = select(Restaurant).where(
            (Restaurant.email == restaurant_create.email) | 
            (Restaurant.name == restaurant_create.name)
        )
        result = await conn.execute(stmt)
        existing_restaurant = result.scalars().first()
        
        if existing_restaurant:
            raise HTTPException(status_code=400, detail="Restaurant with this email or name already exists")

        stmt = insert(Restaurant).values(**restaurant_create.model_dump(), owner_id=token["id"])
        result = await conn.execute(stmt)
        await conn.commit()
        
        stmt = select(Restaurant).where(Restaurant.id == result.lastrowid).options(joinedload(Restaurant.owner))
        result = await conn.execute(stmt)
        restaurant = result.scalars().first()
        
        return restaurant

@app.put("/restaurants/{restaurant_id}", tags=["restaurants"])
async def update_restaurant(restaurant_id: int, restaurant_update: RestaurantUpdate, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = select(Restaurant).where(Restaurant.id == restaurant_id, Restaurant.owner_id == token["id"])
        result = await conn.execute(stmt)
        restaurant = result.scalars().first()
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found or unauthorized")
        
        print(restaurant_update)

        stmt = update(Restaurant).where(Restaurant.id == restaurant_id).values(**restaurant_update.model_dump(exclude_unset=True))
        await conn.execute(stmt)
        stmt = select(Restaurant).where(Restaurant.id == restaurant_id)
        result = await conn.execute(stmt)
        restaurant = result.scalars().first()
        await conn.commit()
        return restaurant

@app.delete("/restaurants/{restaurant_id}", tags=["restaurants"])
async def delete_restaurant(restaurant_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = select(Restaurant).where(Restaurant.id == restaurant_id)
        result = await conn.execute(stmt)
        restaurant = result.scalars().first()

        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        if token["role"] != "admin" and restaurant.owner_id != token["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this restaurant")

        stmt = delete(Restaurant).where(Restaurant.id == restaurant_id)
        result = await conn.execute(stmt)
        await conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        return {"message": "Restaurant deleted successfully"}
