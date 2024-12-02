from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.future import select
from src.services.SQLite.index import async_session
from src.api.users.model import User
from pydantic import BaseModel
import src.services.auth.index as auth
from passlib.hash import pbkdf2_sha256 

app = APIRouter()
auth_scheme = HTTPBearer()


class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login", tags=["auth"])
async def login(login_request: LoginRequest):
    async with async_session() as conn:
        query = select(User).where(User.email == login_request.email)
        result = await conn.execute(query)
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if not pbkdf2_sha256.verify(login_request.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")

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
    confirm_password: str

@app.post("/register", tags=["auth"])
async def register(RegisterRequest: RegisterRequest):
    if RegisterRequest.password != RegisterRequest.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    """ check email format """
    """ check password format """

    async with async_session() as conn:
        existing_user = await conn.execute(select(User).where(User.email == RegisterRequest.email))
        existing_user = existing_user.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        hashed_password = pbkdf2_sha256.hash(RegisterRequest.password)

        print(RegisterRequest)
        
        user = User(
            email=RegisterRequest.email,
            name=RegisterRequest.name,
            surname=RegisterRequest.surname,
            hashed_password=hashed_password,
        )
        print(user)

        conn.add(user)

        await conn.commit()

        return auth.sign_jwt(user)
    