from app.database import engine
from sqlalchemy import text

# Add the missing image_url column to the posts table
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE posts ADD COLUMN IF NOT EXISTS image_url VARCHAR;"))
    conn.commit()

print("Migration completed: Added image_url column to posts table.")