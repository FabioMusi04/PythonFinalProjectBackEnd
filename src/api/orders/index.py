from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, delete, and_
from pydantic import BaseModel
from src.services.SQLite.index import async_session
from src.api.orders.model import Order
from src.api.products.model import Product
from src.api.restaurants.model import Restaurant
import src.services.auth.index as auth
from sqlalchemy.orm import joinedload

app = APIRouter()

class OrderCreate(BaseModel):
    customer_id: int
    products: list[int]
    quantity: list[int]
    restaurant_id: int

@app.post("/orders", tags=["orders"])
async def create_order(order: OrderCreate, token: dict = Depends(auth.JWTBearer())):
    async with async_session() as session:
        new_order = Order(customer_id=order.customer_id , restaurant_id=order.restaurant_id)

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
async def get_orders(skip: int = 0, limit: int = 100, token: dict = Depends(auth.admin_required)):
    async with async_session() as conn:
        stmt = select(Order).offset(skip).limit(limit).options(joinedload(Order.products))
        result = await conn.execute(stmt)
        orders = result.unique().scalars().all()
        return orders

@app.get("/orders/{restaurant_id}", tags=["orders"])
async def get_orders_of_restaurant(restaurant_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt_restaurant = select(Restaurant).where(_and(Restaurant.owner_id == token["id"], Restaurant.id == restaurant_id))
        result_restaurant = await conn.execute(stmt_restaurant)
        restaurant = result_restaurant.scalar_one_or_none()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        stmt = select(Order).where(Product.restaurant_id == restaurant_id).options(joinedload(Order.products))
        result = await conn.execute(stmt)
        orders = result.unique().scalars().all()
        return orders
    
@app.get("/orders/{order_id}", tags=["orders"])
async def get_order(order_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        if token["role"] == "owner":
            stmt_restaurant = select(Restaurant).where(Restaurant.owner_id == token["id"])
            result_restaurant = await conn.execute(stmt_restaurant)
            restaurants = result_restaurant.scalars().all()
            if not restaurants:
                raise HTTPException(status_code=404, detail="No restaurants found for this owner")

            stmt_order = select(Order).where(Order.id == order_id).options(joinedload(Order.products))
            result_order = await conn.execute(stmt_order)
            order = result_order.scalar_one_or_none()
            if order is None:
                raise HTTPException(status_code=404, detail="Order not found")

            if order.restaurant_id not in [restaurant.id for restaurant in restaurants]:
                raise HTTPException(status_code=403, detail="You are not authorized to view this order")

        elif token["role"] == "user":
            stmt = select(Order).where(Order.id == order_id)
            result = await conn.execute(stmt)
            order = result.scalars().first()
            if order is None:
                raise HTTPException(status_code=404, detail="Order not found")
            if order.customer_id != token["id"]:
                raise HTTPException(status_code=403, detail="You are not authorized to view this order")
        
        stmt = select(Order).where(Order.id == order_id).options(joinedload(Order.products))
        result = await conn.execute(stmt)
        order = result.scalars().first()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    
@app.put("/orders/{order_id}", tags=["orders"])
async def update_order(order_id: int, status: str, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt_restaurant = select(Restaurant).where(Restaurant.owner_id == token["id"])
        result_restaurant = await conn.execute(stmt_restaurant)
        restaurants = result_restaurant.scalars().all()
        if not restaurants:
            raise HTTPException(status_code=404, detail="No restaurants found for this owner")

        stmt_order = select(Order).where(Order.id == order_id).options(joinedload(Order.products))
        result_order = await conn.execute(stmt_order)
        order = result_order.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.restaurant_id not in [restaurant.id for restaurant in restaurants]:
            raise HTTPException(status_code=403, detail="You are not authorized to update this order")
        
        stmt = update(Order).where(Order.id == order_id).values(status=status)
        await conn.execute(stmt)
        await conn.commit()
        return {"message": "Order updated successfully"}

@app.delete("/orders/{order_id}", tags=["orders"])
async def delete_order(order_id: int, token: dict = Depends(auth.owner_or_admin_required)):
    async with async_session() as conn:
        stmt_restaurant = select(Restaurant).where(Restaurant.owner_id == token["id"])
        result_restaurant = await conn.execute(stmt_restaurant)
        restaurants = result_restaurant.scalars().all()
        if not restaurants:
            raise HTTPException(status_code=404, detail="No restaurants found for this owner")

        stmt_order = select(Order).where(Order.id == order_id).options(joinedload(Order.products))
        result_order = await conn.execute(stmt_order)
        order = result_order.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.restaurant_id not in [restaurant.id for restaurant in restaurants]:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this order")
        
        stmt = delete(Order).where(Order.id == order_id)
        await conn.execute(stmt)
        await conn.commit()
        return {"message": "Order deleted successfully"}
    
@app.get("/orders/me/{restaurant_id}", tags=["orders"])
async def get_my_orders(restaurant_id: int, token: dict = Depends(auth.JWTBearer())):
    async with async_session() as conn:
        print(token["id"])
        stmt = select(Order).where(
            and_(Order.restaurant_id == restaurant_id, Order.customer_id == token["id"])
        ).options(joinedload(Order.products))        
        result = await conn.execute(stmt)
        orders = result.unique().scalars().all()
        return orders
