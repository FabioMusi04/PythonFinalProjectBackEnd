from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, insert, delete
from pydantic import BaseModel
from src.services.SQLite.index import async_session
from src.api.products.model import Product
import src.services.auth.index as auth
from sqlalchemy.orm import joinedload

app = APIRouter()

class ProductCreate(BaseModel):
    name: str
    description: str = None
    price: float
    restaurant_id: int

@app.post("/products", tags=["products"])
async def create_product(product: ProductCreate, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as session:
        new_product = Product(**product.model_dump())
        session.add(new_product)
        await session.commit()
        return {"product": new_product, "message": "Product created successfully"}

@app.get("/products", tags=["products"])
async def get_products(skip: int = 0, limit: int = 100, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = select(Product).offset(skip).limit(limit)
        result = await conn.execute(stmt)
        products = result.scalars().all()
        return products
    
@app.get("/products/{restaurant_id}", tags=["products"])
async def get_product_by_restaurant(restaurant_id: int, token: dict = Depends(auth.JWTBearer())):
    async with async_session() as conn:
        stmt = select(Product).where(Product.restaurant_id == restaurant_id)
        result = await conn.execute(stmt)
        products = result.scalars().all()
        return products

@app.get("/products/{product_id}", tags=["products"])
async def get_product(product_id: int, token: dict = Depends(auth.JWTBearer())):
    async with async_session() as conn:
        stmt = select(Product).where(Product.id == product_id)
        result = await conn.execute(stmt)
        product = result.scalars().first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    
@app.put("/products/{product_id}", tags=["products"])
async def update_product(product_id: int, product: ProductCreate, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = update(Product).where(Product.id == product_id).values(**product.model_dump())
        await conn.execute(stmt)
        product = await conn.execute(select(Product).where(Product.id == product_id))
        return product.scalars().first()
    
@app.delete("/products/{product_id}", tags=["products"])
async def delete_product(product_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = delete(Product).where(Product.id == product_id)
        await conn.execute(stmt)
        await conn.commit()
        return {"message": "Product deleted successfully"}

