from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50))
    email = Column(String(150), unique=True, index=True)
    password_hash = Column(String)

    phone = Column(String(15), nullable=True)   # ✅ ADD THIS
    profile_image = Column(String, nullable=True)

    is_email_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
