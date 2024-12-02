import segno
from typing import Dict
import os
from dotenv import load_dotenv 
load_dotenv()

front_end_url = os.getenv("FRONTEND2_URL", "https://python-final-project-front-end.vercel.app")

def generate_qr_code(data: Dict) -> str:
    url = f"{front_end_url}/restaurant/{data['restaurant_id']}/table/{data['table_number']}"
    print(url)
    qr = segno.make(url, error='H')
    return qr.png_data_uri(scale=5)