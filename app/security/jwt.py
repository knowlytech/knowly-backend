from datetime import datetime, timedelta
from jose import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

def create_access_token(user_id: int, days: int = 30):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=days)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
