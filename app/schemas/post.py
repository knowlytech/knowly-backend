from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    category_id: int     # ✅ ID only
    media_type: str
    media_url: str
    author_name: str


class AdminPostCreate(BaseModel):
    title: str
    content: str
    category: str
    media_type: str
    media_url: str