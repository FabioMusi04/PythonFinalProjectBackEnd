from passlib.hash import pbkdf2_sha256
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.users.model import User
from src.api.products.model import Product
from src.api.orders.model import Order
from src.api.orderItems.model import order_items
from src.api.restaurants.model import Restaurant
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


# Setup async engine and session
async_engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=True)
async_session = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


async def seed_data():
    async with async_session() as session:
        # Create Admin User
        admin_email = "admin@admin.com"
        result = await session.execute(select(User).filter_by(email=admin_email))
        admin_user = result.scalars().first()

        if not admin_user:
            admin_user = User(
                name="Admin",
                surname="Admin",
                email=admin_email,
                hashed_password=pbkdf2_sha256.hash("admin"),
                role="admin",
            )
            session.add(admin_user)
            print("Default admin user created")

        # Create Normal User
        normal_user_email = "user@example.com"
        result = await session.execute(select(User).filter_by(email=normal_user_email))
        normal_user = result.scalars().first()

        if not normal_user:
            normal_user = User(
                name="Normal",
                surname="User",
                email=normal_user_email,
                hashed_password=pbkdf2_sha256.hash("password"),
                role="user",
            )
            session.add(normal_user)
            print("Normal user created")

            # Create Owner
        owner_email = "owner@example.com"
        result = await session.execute(select(User).filter_by(email=owner_email))
        owner = result.scalars().first()

        if not owner:
            owner = User(
                name="Owner",
                surname="Example",
                email=owner_email,
                hashed_password=pbkdf2_sha256.hash("ownerpassword"),
                role="owner",
            )
            session.add(owner)
            print("Owner user created")

        # Create Restaurant
        restaurant_name = "Sample Restaurant"
        result = await session.execute(
            select(Restaurant).filter_by(name=restaurant_name)
        )
        restaurant = result.scalars().first()

        if not restaurant:
            restaurant = Restaurant(
                name=restaurant_name,
                address="123 Main St",
                city="City",
                country="Country",
                postal_code="12345",
                owner_id=owner.id,  # Assuming the owner is the normal user for simplicity
                email=owner_email,
            )
            session.add(restaurant)
            print("Restaurant created")

        # Commit the session
        await session.commit()

        products = [
            {"id": 1, "name": "Pizza", "price": 1099, "restaurant_id": restaurant.id},
            {"id": 2, "name": "Burger", "price": 599, "restaurant_id": restaurant.id},
            {"id": 3, "name": "Salad", "price": 799, "restaurant_id": restaurant.id},
        ]

        for product_data in products:
            stmt = select(Product).where(Product.name == product_data["name"])
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()

            if not product:
                product = Product(**product_data)
                session.add(product)
                print("Products created")

        await session.commit()

        order = {
            "customer_id": normal_user.id,
            "products": [product["id"] for product in products],
            "quantities": [2, 1, 4],
            "restaurant_id": 1,
        }

        stmt = select(Order).where(Order.customer_id == order["customer_id"])

        result = await session.execute(stmt)
        existing_order = result.scalar_one_or_none()

        if not existing_order:

            new_order = Order(customer_id=order["customer_id"], restaurant_id=order["restaurant_id"])
            new_order.total_price = 0

            session.add(new_order)
            await session.commit()

            for product_id, quantity in zip(order["products"], order["quantities"]):
                stmt = select(Product).where(Product.id == product_id)
                result = await session.execute(stmt)
                product = result.scalar_one_or_none()

                if product:

                    new_order.total_price += product.price * quantity

                    await session.execute(
                        order_items.insert().values(
                            order_id=new_order.id,
                            product_id=product_id,
                            quantity=quantity,
                            price=(
                                (product.price * product.discount)
                                if product.discount
                                else product.price
                            ),
                        )
                    )

            await session.commit()
