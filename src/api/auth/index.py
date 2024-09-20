from fastapi import APIRouter, Depends
from sqlalchemy import select
from src.services.SQLite.index import engine
from src.api.users.model import User
import src.services.auth.index as auth

app = APIRouter()


@app.post("/login", tags=["auth"])
async def login(email: str, password: str):
    async with engine.begin() as conn:
        query = select([User]).where(User.email == email)
        result = await conn.execute(query)
        user = await result.fetchone()

        if user is None:
            return {"error": "Invalid credentials"}

        if user.verify_password(password) is False:
            return {"error": "Invalid credentials"}

        return auth.sign_jwt(user)
    

@app.get("/logout", dependencies=[Depends(auth.JWTBearer())],  tags=["auth"])
async def logout():
    return {"message": "Logged out"}

@app.post("/register", tags=["auth"])
async def register():
    pass
