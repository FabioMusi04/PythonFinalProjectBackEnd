from fastapi import APIRouter, Depends, HTTPException
import src.services.auth.index as auth
from src.services.QRCode.index import generate_qr_code
from pydantic import BaseModel


app = APIRouter()

class QRCodeBase(BaseModel):
    restaurant_id: int
    table_number: int


@app.post("/qrcodes", tags=["qrcodes"])
async def create_qrcode(QRCode: QRCodeBase, 
    token: dict = Depends(auth.JWTBearer())):
    user_id = token.get("id")
    qr_code = generate_qr_code({
        "restaurant_id": QRCode.restaurant_id,
        "table_number": QRCode.table_number,
        "user_id": user_id
    })

    return qr_code