from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, insert, delete
from pydantic import BaseModel
from src.services.SQLite.index import async_session
from src.api.orders.model import Order
from src.api.products.model import Product
import src.services.auth.index as auth
from sqlalchemy.orm import joinedload

app = APIRouter()

class OrderCreate(BaseModel):
    customer_id: int
    products: list[int]
    quantity: list[int]

@app.post("/orders", tags=["orders"])
async def create_order(order: OrderCreate, token: dict = Depends(auth.JWTBearer())):
    async with async_session() as session:
        new_order = Order(customer_id=order.customer_id)

        for product_id, quantity in zip(order.products, order.quantities):
            stmt = select(Product).where(Product.id == product_id)
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
            
            new_order.products.append(product)
            new_order.total_price += product.price * quantity

        session.add(new_order)
        await session.commit()
        return {"id": new_order.id, "message": "Order created successfully"}
    
@app.get("/orders", tags=["orders"])
async def get_orders(skip: int = 0, limit: int = 100, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = select(Order).offset(skip).limit(limit).options(joinedload(Order.products))
        result = await conn.execute(stmt)
        orders = result.unique().scalars().all()
        return orders

@app.get("/orders/{restaurant_id}", tags=["orders"])
async def get_orders_by_restaurant(restaurant_id: int, token: dict = Depends(auth.JWTBearer())):
    async with async_session() as conn:
        stmt = select(Order).where(Product.restaurant_id == restaurant_id).options(joinedload(Order.products))
        result = await conn.execute(stmt)
        orders = result.unique().scalars().all()
        return orders
    
@app.get("/orders/{order_id}", tags=["orders"])
async def get_order(order_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = select(Order).where(Order.id == order_id).options(joinedload(Order.products))
        result = await conn.execute(stmt)
        order = result.scalars().first()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    
@app.put("/orders/{order_id}", tags=["orders"])
async def update_order(order_id: int, status: str, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = update(Order).where(Order.id == order_id).values(status=status)
        await conn.execute(stmt)
        await conn.commit()
        return {"message": "Order updated successfully"}

@app.delete("/orders/{order_id}", tags=["orders"])
async def delete_order(order_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt = delete(Order).where(Order.id == order_id)
        await conn.execute(stmt)
        await conn.commit()
        return {"message": "Order deleted successfully"}
    
@app.get("/orders/me/{restaurant_id}", tags=["orders"])
async def get_my_orders(restaurant_id: int, token: dict = Depends(auth.JWTBearer())):
    async with async_session() as conn:
        stmt = select(Order).where(Product.restaurant_id == restaurant_id).options(joinedload(Order.products))
        result = await conn.execute(stmt)
        orders = result.unique().scalars().all()
        return orders
