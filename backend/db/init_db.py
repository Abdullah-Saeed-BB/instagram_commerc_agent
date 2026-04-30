import asyncio
import sys
import os
from datetime import date
from dotenv import load_dotenv

# Find the .env file in the backend directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(backend_dir, ".env"))

# Add the project root to sys.path to allow imports from backend
# Project root is one level up from backend
sys.path.insert(0, os.path.abspath(os.path.join(backend_dir, "..")))

from models import Base
from session import engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from session import make_database_url
import pandas as pd

DB_NAME = os.getenv("DB_NAME")
async def create_database_if_not_exists():
    engine = create_async_engine(make_database_url("postgres"), isolation_level="AUTOCOMMIT")
    is_exists = False

    async with engine.connect() as conn:
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        )
        exists = result.scalar()

        if not exists:
            print(f"Database '{DB_NAME}' does not exist. Creating...")
            await conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))

        else:
            print(f"Database '{DB_NAME}' already exists.")
            is_exists = True

    await engine.dispose()
    return is_exists

async def init_db():
    print("Initializing the database...")
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        barbers = pd.read_csv("./data/barbers.csv")
        barbers["career_start_date"] = pd.to_datetime(barbers["career_start_date"])
        barbers_records = barbers.to_dict(orient="records")

        for barber in barbers_records:
            await conn.execute(
                text("INSERT INTO barbers (id, name, career_start_date) VALUES (:id, :name, :career_start_date)"),
                {"id": barber["id"], "name": barber["name"], "career_start_date": barber["career_start_date"]}
            )

        services = pd.read_csv("./data/services.csv")
        services["title"] = services["title"]\
            .str.replace(" ", "_").str.replace("&", "and")\
            .str.replace('"', "").str.lower()
        services["price"] = pd.to_numeric(
            services["price"].str.replace("$", ""))
        services_records = services.to_dict(orient="records")

        for service in services_records:
            await conn.execute(
                text("INSERT INTO services (id, name, description, price) VALUES (:id, :name, :description, :price)"),
                {"id": service["id"], "name": service["title"], "description": service["description"], "price": service["price"]}
            )
        
        await conn.commit()
    print("Database initialization complete.")

if __name__ == "__main__":
    is_db_exists = asyncio.run(create_database_if_not_exists())
    if not is_db_exists:
        asyncio.run(init_db())