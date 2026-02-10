from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.database import Base
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    content = Column(Text)
    word_count = Column(Integer)

    media_type = Column(String(20))
    media_url = Column(String)

    author_name = Column(String(100))
    author_type = Column(String(20))

    status = Column(String(20))

    category_id = Column(Integer, ForeignKey("categories.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # ✅ ADD THESE
    category = relationship("Category")
    user = relationship("User")

    created_at = Column(DateTime, default=datetime.utcnow)
