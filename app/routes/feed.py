from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models.post import Post

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

# =====================================================
# 1️⃣ HOME FEED — ALL CATEGORIES (20 MIXED POSTS)
# =====================================================
@router.get("/feed/home")
def home_feed(
    limit: int = Query(20, le=50),
    cursor: str | None = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(Post)
        .options(
            joinedload(Post.user),
            joinedload(Post.category)
        )
        .filter(
            Post.status == "approved",
            Post.user_id.isnot(None)   # 🔐 SAFETY
        )
    )

    if cursor:
        query = query.filter(Post.created_at < cursor)

    posts = (
        query
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "media_url": post.media_url,

                # ✅ SAFE AUTHOR
                "author": {
                    "id": post.user.id if post.user else None,
                    "name": f"{post.user.first_name} {post.user.last_name}" if post.user else "Unknown",
                    "profile_image": post.user.profile_image if post.user else None
                },

                "created_at": post.created_at,

                # ✅ SAFE CATEGORY
                "category": post.category.name if post.category else None
            }
            for post in posts
        ],
        "next_cursor": posts[-1].created_at if posts else None
    }


# =====================================================
# 2️⃣ CATEGORY FEED — BY CATEGORY ID
# =====================================================
@router.get("/feed/category/{category_id}")
def category_feed(
    category_id: int,
    limit: int = Query(20, le=50),
    cursor: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Post).filter(
        Post.status == "approved",
        Post.category_id == category_id
    )

    if cursor:
        query = query.filter(Post.created_at < cursor)

    posts = (
        query
        .order_by(Post.created_at.desc())   # ✅ SAME ORDER
        .limit(limit)
        .all()
    )

    return {
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "media_url": post.media_url,
                "author_name": post.author_name,
                "created_at": post.created_at,
                "category_id": post.category_id,
                "category": post.category.name
            }
            for post in posts
        ],
        "next_cursor": posts[-1].created_at if posts else None
    }
