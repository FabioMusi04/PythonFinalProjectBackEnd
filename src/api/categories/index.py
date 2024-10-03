from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from pydantic import BaseModel
from src.services.SQLite.index import async_session
from src.api.categories.model import Category
from sqlalchemy.orm import joinedload
import src.services.auth.index as auth
import src.api.users.model as User

app = APIRouter()

class CategoryCreate(BaseModel):
    name: str
    description: str
    restaurant_id: int

@app.post("/categories", tags=["categories"])   
async def create_category(category: CategoryCreate, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.name == category.name))
        existing_category = result.scalars().first()
        
        if existing_category:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        
        new_category = Category(**category.model_dump())
        session.add(new_category)
        await session.commit()
        return {"category": new_category, "message": "Category created successfully"}

@app.get("/categories", tags=["categories"])
async def get_categories(skip: int = 0, limit: int = 100, token: dict = Depends(auth.admin_required)):
    async with async_session() as conn:
        stmt = select(Category).offset(skip).limit(limit)
        result = await conn.execute(stmt)
        categories = result.scalars().all()
        return categories

@app.get("/categories/{restaurant_id}", tags=["categories"])
async def get_categories_by_restaurant(restaurant_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = select(Category).where(Category.restaurant_id == restaurant_id)
        result = await conn.execute(stmt)
        categories = result.scalars().all()
        return categories
    
@app.get("/categories/{category_id}", tags=["categories"])
async def get_category(category_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = select(Category).where(Category.id == category_id)
        result = await conn.execute(stmt)
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

@app.put("/categories/{category_id}", tags=["categories"])
async def update_category(category_id: int, category: CategoryCreate, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as session:
        stmt = select(Category).where(Category.id == category_id)
        result = await session.execute(stmt)
        existing_category = result.scalar_one_or_none()
        if not existing_category:
            raise HTTPException(status_code=404, detail="Category not found")
        

        stmt = select(User).where(User.id == token["id"]).options(joinedload(User.restaurants))
        user_result = await session.execute(stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if existing_category.restaurant_id not in [restaurant.id for restaurant in user.restaurants]:
            raise HTTPException(status_code=403, detail="You are not authorized to update this category")
        
        existing_category.name = category.name
        existing_category.description = category.description
        await session.commit()
        return {"category": existing_category, "message": "Category updated successfully"}


@app.delete("/categories/{category_id}", tags=["categories"])
async def delete_category(category_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as session:
        stmt = select(Category).where(Category.id == category_id)
        result = await session.execute(stmt)
        existing_category = result.scalar_one_or_none()
        if not existing_category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        stmt = select(User).where(User.id == token["id"]).options(joinedload(User.restaurants))
        user_result = await session.execute(stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if existing_category.restaurant_id not in [restaurant.id for restaurant in user.restaurants]:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this category")
        
        session.delete(existing_category)
        await session.commit()
        return {"message": "Category deleted successfully"}