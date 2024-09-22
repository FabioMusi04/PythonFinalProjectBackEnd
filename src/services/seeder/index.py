from passlib.hash import pbkdf2_sha256
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.users.model import User
from src.api.restaurants.model import Restaurant 
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy.ext.asyncio import create_async_engine

# Setup async engine and session
async_engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=True)
async_session = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

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
        result = await session.execute(select(Restaurant).filter_by(name=restaurant_name))
        restaurant = result.scalars().first()

        if not restaurant:
            restaurant = Restaurant(
                name=restaurant_name,
                address="123 Main St",
                city="City",
                country="Country",
                postal_code="12345",
                owner_id=owner.id  # Assuming the owner is the normal user for simplicity
            )
            session.add(restaurant)
            print("Restaurant created")

        # Commit the session
        await session.commit()
