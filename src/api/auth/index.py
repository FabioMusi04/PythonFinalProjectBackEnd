from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from src.services.SQLite.index import async_session
from src.api.users.model import User
from pydantic import BaseModel
import src.services.auth.index as auth
from datetime import datetime

app = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login", tags=["auth"])
async def login(login_request: LoginRequest):
    async with async_session() as conn:
        query = select(User).where(User.email == login_request.email)
        result = await conn.execute(query)
        user = result.scalars().first()

        if user is None or not user.verify_password(login_request.password):
            return {"error": "Invalid credentials"}

        return auth.sign_jwt(user)
    

@app.get("/logout", dependencies=[Depends(auth.JWTBearer())],  tags=["auth"])
async def logout():
    return {"message": "Logged out"}


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    surname: str
    email: str
    phone_number: str
    address: str
    date_of_birth: datetime
    confirm_password: str

@app.post("/register", tags=["auth"])
async def register(RegisterRequest: RegisterRequest):
    if RegisterRequest.password != RegisterRequest.confirm_password:
        return {"error": "Passwords do not match"}
    
    async with async_session() as conn:
        user = User(
            email=RegisterRequest.email,
            name=RegisterRequest.name,
            surname=RegisterRequest.surname,
            phone_number=RegisterRequest.phone_number,
            address=RegisterRequest.address,
            date_of_birth=RegisterRequest.date_of_birth,
        )
        user.set_password(RegisterRequest.password)
        conn.add(user)
        await conn.commit()
        return auth.sign_jwt(user)
