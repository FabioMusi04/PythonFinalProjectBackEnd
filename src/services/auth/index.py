import jwt
from datetime import datetime, timedelta
from typing import Dict
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os
from dotenv import load_dotenv 
load_dotenv() 

def sign_jwt(user) -> Dict[str, str]:
    expires_at = datetime.now() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 4328)))

    payload = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "expires": expires_at.timestamp()
    }
    token = jwt.encode(payload, os.getenv("JWT_SECRET", "secret"), algorithm=os.getenv("JWT_ALGORITHM", "HS256"))

    userToSend = user
    userToSend.hashed_password = None

    return {"token": { "access_token": token, "expires_in": int(expires_at.timestamp()) }, "token_type": "bearer", "user": userToSend}

def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, os.getenv("JWT_SECRET", "secret"), algorithms=[(os.getenv("JWT_ALGORITHM", "HS256"))])
        return decoded_token if decoded_token["expires"] >= datetime.now().timestamp() else None
    except:
        return {}

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            payload = decode_jwt(credentials.credentials)
            return payload 
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid
    
def admin_required(token: dict = Depends(JWTBearer())):
    if token.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return token

def owner_required(token: dict = Depends(JWTBearer())):
    if token.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Owner privileges required.")
    return token

def owner_or_admin_required(token: dict = Depends(JWTBearer())):
    if token.get("role") not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Owner or Admin privileges required.")
    return token