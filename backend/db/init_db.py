import asyncio
import sys
import os
from dotenv import load_dotenv

# Find the .env file in the backend directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(backend_dir, ".env"))

# Add the project root to sys.path to allow imports from backend
# Project root is one level up from backend
sys.path.insert(0, os.path.abspath(os.path.join(backend_dir, "..")))

from backend.db.base import Base
from backend.db.session import engine

async def init_db():
    print("Initializing the database...")
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialization complete.")

if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except Exception as e:
        print(f"Error initializing database: {e}")
