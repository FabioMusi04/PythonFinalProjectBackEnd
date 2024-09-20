from fastapi import FastAPI
import src.services.SQLite.index as db
import src.api.users.index as users

""" fastapi dev main.py """

app = FastAPI()

app.include_router(users.app)