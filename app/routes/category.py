# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from app.schemas.category import Category

# router = APIRouter()

# # Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # --- GET API (Sirf Fetch karega) ---
# @router.get("/categories")
# def get_categories(db: Session = Depends(get_db)):
#     """
#     Ye API database se saved Categories (Name + Image URL) return karegi.
#     """
#     return db.query(Category).all()





from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.category import Category
from app.models.post import Post   # 🔹 Post model import

router = APIRouter()

# -------------------------
# DB Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# GET ALL CATEGORIES
# -------------------------
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Ye API database se saari categories return karegi
    (AI, Data Science, Backend, etc.)
    """
    return db.query(Category).all()

# -------------------------
# GET POSTS BY CATEGORY ID
# -------------------------
@router.get("/categories/{category_id}/posts")
def get_posts_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Ye API sirf us category ka content return karegi
    jo frontend se click hoke aayi hai
    """
    return (
        db.query(Post)
        .filter(Post.category_id == category_id)
        .all()
    )

