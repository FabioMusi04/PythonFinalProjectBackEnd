from fastapi import FastAPI
import src.services.SQLite.index as db
import src.api.users.index as users
import src.api.auth.index as auth

""" fastapi dev main.py """

app = FastAPI()

app.include_router(auth.app)
app.include_router(users.app)