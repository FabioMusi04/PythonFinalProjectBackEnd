import jwt
import time
from typing import Dict
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 4320

def sign_jwt(user) -> Dict[str, str]:
    payload = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "expires": time.time() + ACCESS_TOKEN_EXPIRE_MINUTES
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {"access_token": token}

def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
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
