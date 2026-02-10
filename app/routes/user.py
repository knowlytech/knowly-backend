# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from app.schemas.post import PostCreate
# from app.models.post import Post
# from app.utils.validation import validate_50_words, validate_media

# router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.post("/user/post")
# def create_post(post: PostCreate, db: Session = Depends(get_db)):

#     # 1️⃣ Validate 50 words
#     if not validate_50_words(post.content):
#         raise HTTPException(status_code=400, detail="Content must be around 50 words")

#     # 2️⃣ Validate image/video
#     if not validate_media(post.media_type, post.media_url):
#         raise HTTPException(status_code=400, detail="Image or video is required")

#     # 3️⃣ Calculate word count (CRITICAL FIX)
#     word_count = len(post.content.split())

#     # 4️⃣ Create post
#     new_post = Post(
#         title=post.title,
#         content=post.content,
#         word_count=word_count,          # ✅ FIX HERE
#         category=post.category,
#         media_type=post.media_type,
#         media_url=post.media_url,
#         author_name=post.author_name,
#          author_type="user",
#         status="pending"
#     )

#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)

#     return {"message": "Post submitted for approval"}

import time
from datetime import datetime, timezone
from uuid import UUID
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.post import PostCreate
from app.schemas.user import UpdateProfileSchema
from app.models.post import Post
from app.utils.validation import validate_50_words, validate_media
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.subscription import Subscription
from app.models.savepost import SavedPost

router = APIRouter()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# CREATE POST (USER)
# -----------------------------
@router.post("/user/post")
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ word count calculate
    word_count = len(post.content.split())

    new_post = Post(
        title=post.title,
        content=post.content,
        word_count=word_count,            # ✅ FIXED
        media_type=post.media_type,
        media_url=post.media_url,
        category_id=post.category_id,

        user_id=current_user.id,
        author_name=f"{current_user.first_name} {current_user.last_name}",
        author_type="user",
        status="pending",
        created_at=datetime.now(timezone.utc)                # ✅ pending for admin
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"message": "Post submitted for admin approval"}


    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"message": "Post created"}


# -----------------------------
# GET POSTS (ALL / CATEGORY-WISE)
# -----------------------------
@router.get("/posts")
def get_posts(
    category_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    - All posts: /posts
    - Category-wise: /posts?category_id=2
    """
    query = db.query(Post)

    if category_id:
        query = query.filter(Post.category_id == category_id)

    return query.order_by(Post.created_at.desc()).all()




@router.post("/posts")
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_post = Post(
        title=post.title,
        content=post.content,
        media_url=post.media_url,
        category_id=post.category_id,
        status="approved",

        # 🔥 THIS IS THE KEY FIX
        user_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"message": "Post created"}



@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "middle_name": current_user.middle_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "profile_image": current_user.profile_image
    }




# @router.post("/profile-image")
# def upload_profile_image(
#     image: UploadFile = File(...),
#     current_user: User = Depends(get_current_user)
# ):
#     if image.content_type not in ["image/jpeg", "image/png"]:
#         raise HTTPException(400, "Only JPG or PNG allowed")

#     os.makedirs("uploads", exist_ok=True)
#     file_path = f"uploads/profile_{current_user.id}.jpg"

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(image.file, buffer)

#     image_url = f"/{file_path}"

#     db = SessionLocal()
#     user = db.query(User).filter(User.id == current_user.id).first()
#     user.profile_image = image_url
#     db.commit()
#     db.close()

#     return {
#         "message": "Profile image updated",
#         "profile_image": image_url
#     }



@router.post("/profile-image")
def upload_profile_image(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # 1. Validation
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(400, "Only JPG or PNG allowed")

    # 2. Database Session Start (Pehle hi start kar lo taaki purani image delete kar sakein)
    db = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()

    # 3. 🔥 DELETE OLD IMAGE (Optional but Recommended)
    # Agar purani image hai, to use delete kar do taaki storage na bhare
    if user.profile_image:
        # URL se file path nikalo (e.g., "/uploads/..." -> "uploads/...")
        old_file_path = user.profile_image.lstrip("/") 
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except Exception as e:
                print(f"Error deleting old file: {e}")

    # 4. 🔥 GENERATE UNIQUE FILENAME
    # Current time ko filename mein jod diya
    timestamp = int(time.time()) 
    os.makedirs("uploads", exist_ok=True)
    
    # Naya format: profile_{id}_{timestamp}.jpg
    file_path = f"uploads/profile_{current_user.id}_{timestamp}.jpg"

    # 5. Save New File
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # 6. Update Database
    image_url = f"/{file_path}"
    user.profile_image = image_url
    
    db.commit()
    db.close()

    return {
        "message": "Profile image updated",
        "profile_image": image_url
    }



@router.delete("/profile-image")
def remove_profile_image(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()

    if user.profile_image:
        try:
            os.remove(user.profile_image.lstrip("/"))
        except:
            pass

    user.profile_image = None
    db.commit()
    db.close()

    return { "message": "Profile image removed" }




@router.put("/profile")
def update_profile(
    data: UpdateProfileSchema,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()

    if data.first_name is not None:
        user.first_name = data.first_name
    if data.middle_name is not None:
        user.middle_name = data.middle_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.phone is not None:
        user.phone = data.phone

    db.commit()
    db.close()

    return { "message": "Profile updated successfully" }




@router.get("/my-posts")
def get_my_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    posts = (
        db.query(Post)
        .filter(
            Post.user_id == current_user.id,
            Post.status == "approved"   # ✅ only approved posts
        )
        .order_by(Post.created_at.desc())
        .all()
    )

    return posts



@router.get("/users/{user_id}")
def view_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    posts = db.query(Post).filter(Post.user_id == user_id).all()

    is_subscribed = db.query(Subscription).filter(
        Subscription.subscriber_id == current_user.id,
        Subscription.creator_id == user_id
    ).first() is not None

    return {
        "user": {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "profile_image": user.profile_image
        },
        "is_subscribed": is_subscribed,
        "posts": posts
    }





@router.post("/subscribe/{creator_id}") 
def subscribe_user(
    creator_id: int,
    db: Session = Depends(get_db),  
    current_user: User = Depends(get_current_user)
):
    if creator_id == current_user.id:
        raise HTTPException(400, "You cannot subscribe to yourself")

    creator = db.query(User).filter(User.id == creator_id).first()
    if not creator:
        raise HTTPException(404, "User not found")

    exists = db.query(Subscription).filter(
        Subscription.subscriber_id == current_user.id,
        Subscription.creator_id == creator_id
    ).first()

    if exists:
        raise HTTPException(400, "Already subscribed")

    sub = Subscription(
        subscriber_id=current_user.id,
        creator_id=creator_id
    )

    db.add(sub)
    db.commit()

    return {"message": "Subscribed successfully"}

@router.get("/my-subscriptions")
def my_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = (
        db.query(User)
        .join(Subscription, Subscription.creator_id == User.id)
        .filter(Subscription.subscriber_id == current_user.id)
        .all()
    )

    return [
        {
            "id": u.id,
            "name": f"{u.first_name} {u.last_name}",
            "profile_image": u.profile_image
        }
        for u in users
    ]





@router.delete("/unsubscribe/{creator_id}")
def unsubscribe_user(
    creator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(Subscription).filter(
        Subscription.subscriber_id == current_user.id,
        Subscription.creator_id == creator_id
    ).first()

    if not sub:
        raise HTTPException(400, "Not subscribed")

    db.delete(sub)
    db.commit()

    return { "message": "Unsubscribed successfully" }







    @router.post("/posts/{post_id}/save")
    def save_post(
        post_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        exists = db.query(SavedPost).filter(
            SavedPost.user_id == current_user.id,
            SavedPost.post_id == post_id
        ).first()

        if exists:
            raise HTTPException(400, "Post already saved")

        saved = SavedPost(
            user_id=current_user.id,
            post_id=post_id
        )

        db.add(saved)
        db.commit()

        return {"message": "Post saved successfully"}





    @router.delete("/posts/{post_id}/unsave")
    def unsave_post(
        post_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        saved = db.query(SavedPost).filter(
            SavedPost.user_id == current_user.id,
            SavedPost.post_id == post_id
        ).first()

        if not saved:
            raise HTTPException(404, "Post not saved")

        db.delete(saved)
        db.commit()

        return {"message": "Post removed from saved"}




    @router.get("/my-saved-posts")
    def my_saved_posts(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        posts = (
            db.query(Post)
            .join(SavedPost, SavedPost.post_id == Post.id)
            .filter(SavedPost.user_id == current_user.id)
            .order_by(SavedPost.created_at.desc())
            .all()
        )

        return posts
