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
            {"id": 4, "name": "Pasta", "price": 899, "restaurant_id": restaurant.id, "description": "Delicious pasta with tomato sauce", "discount": 10},
            {"id": 5, "name": "Sushi", "price": 1299, "restaurant_id": restaurant.id, "description": "Fresh sushi rolls", "discount": 15},
            {"id": 6, "name": "Steak", "price": 1599, "restaurant_id": restaurant.id, "description": "Juicy grilled steak", "discount": 20},
            {"id": 7, "name": "Tacos", "price": 699, "restaurant_id": restaurant.id, "description": "Spicy beef tacos", "discount": 5},
            {"id": 8, "name": "Sandwich", "price": 499, "restaurant_id": restaurant.id, "description": "Ham and cheese sandwich", "discount": 10},
            {"id": 9, "name": "Soup", "price": 399, "restaurant_id": restaurant.id, "description": "Hot chicken soup", "discount": 10},
            {"id": 10, "name": "Fries", "price": 299, "restaurant_id": restaurant.id, "description": "Crispy french fries", "discount": 5},
            {"id": 11, "name": "Ice Cream", "price": 199, "restaurant_id": restaurant.id, "description": "Vanilla ice cream", "discount": 10},
            {"id": 12, "name": "Cake", "price": 499, "restaurant_id": restaurant.id, "description": "Chocolate cake", "discount": 15},
            {"id": 13, "name": "Salmon", "price": 1399, "restaurant_id": restaurant.id, "description": "Grilled salmon", "discount": 20},
            {"id": 14, "name": "Chicken Wings", "price": 799, "restaurant_id": restaurant.id, "description": "Spicy chicken wings", "discount": 10},
            {"id": 15, "name": "Pizza Margherita", "price": 1099, "restaurant_id": restaurant.id, "description": "Classic Margherita pizza", "discount": 10},
            {"id": 16, "name": "Pizza Pepperoni", "price": 1199, "restaurant_id": restaurant.id, "description": "Pepperoni pizza", "discount": 10},
            {"id": 17, "name": "Pizza Veggie", "price": 999, "restaurant_id": restaurant.id, "description": "Vegetarian pizza", "discount": 10},
            {"id": 18, "name": "Burger Cheese", "price": 699, "restaurant_id": restaurant.id, "description": "Cheeseburger", "discount": 10},
            {"id": 19, "name": "Burger Bacon", "price": 799, "restaurant_id": restaurant.id, "description": "Bacon burger", "discount": 10},
            {"id": 20, "name": "Burger Veggie", "price": 599, "restaurant_id": restaurant.id, "description": "Vegetarian burger", "discount": 10},
            {"id": 21, "name": "Salad Caesar", "price": 899, "restaurant_id": restaurant.id, "description": "Caesar salad", "discount": 10},
            {"id": 22, "name": "Salad Greek", "price": 799, "restaurant_id": restaurant.id, "description": "Greek salad", "discount": 10},
            {"id": 23, "name": "Salad Fruit", "price": 699, "restaurant_id": restaurant.id, "description": "Fruit salad", "discount": 10},
            {"id": 24, "name": "Pasta Carbonara", "price": 999, "restaurant_id": restaurant.id, "description": "Pasta Carbonara", "discount": 10},
            {"id": 25, "name": "Pasta Alfredo", "price": 1099, "restaurant_id": restaurant.id, "description": "Pasta Alfredo", "discount": 10},
            {"id": 26, "name": "Pasta Bolognese", "price": 1199, "restaurant_id": restaurant.id, "description": "Pasta Bolognese", "discount": 10},
            {"id": 27, "name": "Sushi Nigiri", "price": 1399, "restaurant_id": restaurant.id, "description": "Nigiri sushi", "discount": 10},
            {"id": 28, "name": "Sushi Sashimi", "price": 1499, "restaurant_id": restaurant.id, "description": "Sashimi sushi", "discount": 10},
            {"id": 29, "name": "Sushi Maki", "price": 1299, "restaurant_id": restaurant.id, "description": "Maki sushi", "discount": 10},
            {"id": 30, "name": "Steak Ribeye", "price": 1799, "restaurant_id": restaurant.id, "description": "Ribeye steak", "discount": 10},
            {"id": 31, "name": "Steak Sirloin", "price": 1699, "restaurant_id": restaurant.id, "description": "Sirloin steak", "discount": 10},
            {"id": 32, "name": "Steak T-bone", "price": 1899, "restaurant_id": restaurant.id, "description": "T-bone steak", "discount": 10},
            {"id": 33, "name": "Tacos Chicken", "price": 799, "restaurant_id": restaurant.id, "description": "Chicken tacos", "discount": 10},
            {"id": 34, "name": "Tacos Beef", "price": 899, "restaurant_id": restaurant.id, "description": "Beef tacos", "discount": 10},
            {"id": 35, "name": "Tacos Fish", "price": 999, "restaurant_id": restaurant.id, "description": "Fish tacos", "discount": 10},
            {"id": 36, "name": "Sandwich Club", "price": 599, "restaurant_id": restaurant.id, "description": "Club sandwich", "discount": 10},
            {"id": 37, "name": "Sandwich BLT", "price": 699, "restaurant_id": restaurant.id, "description": "BLT sandwich", "discount": 10},
            {"id": 38, "name": "Sandwich Tuna", "price": 799, "restaurant_id": restaurant.id, "description": "Tuna sandwich", "discount": 10},
            {"id": 39, "name": "Soup Tomato", "price": 499, "restaurant_id": restaurant.id, "description": "Tomato soup", "discount": 10},
            {"id": 40, "name": "Soup Mushroom", "price": 599, "restaurant_id": restaurant.id, "description": "Mushroom soup", "discount": 10},
            {"id": 41, "name": "Soup Lentil", "price": 699, "restaurant_id": restaurant.id, "description": "Lentil soup", "discount": 10},
            {"id": 42, "name": "Fries Sweet Potato", "price": 399, "restaurant_id": restaurant.id, "description": "Sweet potato fries", "discount": 10},
            {"id": 43, "name": "Fries Curly", "price": 499, "restaurant_id": restaurant.id, "description": "Curly fries", "discount": 10},
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
