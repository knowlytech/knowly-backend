import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine, SessionLocal
from app.models.category import Category
from app.routes import user, feed, admin
from app.routes import category
from app.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)
os.makedirs("uploads", exist_ok=True)



app = FastAPI(title="Knowledge Startup Backend")


@app.on_event("startup")
def seed_default_categories():
    db = SessionLocal()
    try:
        category_items = [
            {"id": 1, "name": "For You"},
            {"id": 2, "name": "AI & ML"},
            {"id": 3, "name": "Data Science"},
            {"id": 4, "name": "CS & Engineering"},
            {"id": 5, "name": "Data Structures"},
            {"id": 6, "name": "DBMS"},
            {"id": 7, "name": "System Design"},
            {"id": 8, "name": "Frontend"},
            {"id": 9, "name": "Backend"},
            {"id": 10, "name": "Full Stack"},
            {"id": 11, "name": "Mobile Dev"},
            {"id": 12, "name": "Cloud Computing"},
            {"id": 13, "name": "DevOps"},
            {"id": 14, "name": "Cyber Security"},
            {"id": 15, "name": "Python"},
            {"id": 16, "name": "Java"},
            {"id": 17, "name": "C++"},
            {"id": 18, "name": ".NET Core"},
            {"id": 19, "name": "Blockchain"},
            {"id": 20, "name": "Startups"},
            {"id": 21, "name": "Gadgets"},
            {"id": 22, "name": "Tech News"},
        ]

        for item in category_items:
            existing = db.query(Category).filter(Category.id == item["id"]).first()
            if not existing:
                db.add(Category(id=item["id"], name=item["name"]))

        db.commit()
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(user.router)
app.include_router(feed.router)
app.include_router(admin.router)
app.include_router(category.router)
app.include_router(auth_router)