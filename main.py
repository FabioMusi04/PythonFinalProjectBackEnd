from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import src.services.SQLite.index as db
import src.api.users.index as users
import src.api.restaurants.index as restaurants
import src.api.orders.index as orders
import src.api.products.index as products
import src.api.auth.index as auth
import src.api.qrcodes.index as qrcodes

import src.services.QRCode.index as qr_code

""" fastapi dev main.py """


import os
from dotenv import load_dotenv 
load_dotenv() 

origins = [
    os.getenv("FRONTEND_URL", "https://python-final-project-front-end.vercel.app"),
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.app)
app.include_router(restaurants.app)
app.include_router(products.app)
app.include_router(orders.app)
app.include_router(auth.app)
app.include_router(qrcodes.app)

from src.services.seeder.index import seed_data


async def startup_event():
    # Reset the database
    await db.reset_database()
    # Seed the database
    await seed_data()

app.add_event_handler("startup", startup_event)


