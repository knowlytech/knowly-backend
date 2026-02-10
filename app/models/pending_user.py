from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class PendingUser(Base):
    __tablename__ = "pending_users"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)

    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    otp_code = Column(String(6), nullable=False)
    otp_expires_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
