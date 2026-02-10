from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.post import Post
from app.config import ADMIN_SECRET_KEY
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
approved_at = datetime.now(timezone.utc)
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def admin_auth(secret: str = Header(...)):
    if secret != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# ✅ Pending posts
@router.get("/admin/pending")
def pending_posts(
    db: Session = Depends(get_db),
    _: None = Depends(admin_auth)
):
    return db.query(Post).filter(Post.status == "pending").all()

# ✅ Approve post
@router.post("/admin/approve/{post_id}")
def approve_post(
    post_id: UUID,                      # ✅ UUID type
    db: Session = Depends(get_db),
    _: None = Depends(admin_auth)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(404, "Post not found")

    post.status = "approved"
    post.approved_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": "Post approved successfully"}

# ✅ Reject post
@router.post("/admin/reject/{post_id}")
def reject_post(
    post_id: UUID,                      # ✅ UUID type
    db: Session = Depends(get_db),
    _: None = Depends(admin_auth)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(404, "Post not found")

    post.status = "rejected"
    db.commit()

    return {"message": "Post rejected successfully"}
