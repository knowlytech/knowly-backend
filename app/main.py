from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.routes import user, feed, admin
from app.routes import category
from app.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)



app = FastAPI(title="Knowledge Startup Backend")


origins = [
    "http://localhost:5173",  # Aapka frontend URL (Vite default)
    "http://127.0.0.1:5173",
    "*"                       # Testing ke liye '*' (sab allow) kar sakte hain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # Kaun frontend allow hai
    allow_credentials=True,
    allow_methods=["*"],      # GET, POST, PUT sab allow karo
    allow_headers=["*"],      # Headers allow karo
)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(user.router)
app.include_router(feed.router)
app.include_router(admin.router)
app.include_router(category.router)
app.include_router(auth_router)