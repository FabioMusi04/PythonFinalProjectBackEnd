from fastapi import FastAPI
import src.services.SQLite.index as db
import src.api.users.index as users
import src.api.restaurants.index as restaurants
import src.api.auth.index as auth

""" fastapi dev main.py """

app = FastAPI()

app.include_router(users.app)
app.include_router(restaurants.app)
app.include_router(auth.app)

from src.services.seeder.index import seed_data


async def startup_event():
    # Reset the database
    await db.reset_database()
    # Seed the database
    await seed_data()

app.add_event_handler("startup", startup_event)
