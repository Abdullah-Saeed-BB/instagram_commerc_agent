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
        
        new_barbers = [
            {'name': 'Moe Johnson', 'career_start_date': date(2010, 1, 18)},
            {'name': 'John Doe', 'career_start_date': date(2012, 5, 3)},
            {'name': 'Jane Miller', 'career_start_date': date(2014, 11, 12)},
        ]

        for barber in new_barbers:
            await conn.execute(
                text("INSERT INTO barbers (name, career_start_date) VALUES (:name, :career_start_date)"),
                {"name": barber["name"], "career_start_date": barber["career_start_date"]}
            )

        services = pd.read_csv("./data/services.csv")
        services_records = services.to_dict(orient="records")

        for service in services_records:
            await conn.execute(
                text("INSERT INTO services (name, description, price) VALUES (:name, :description, :price)"),
                {"name": service["service_title"], "description": service["description"], "price": int(service["price"].replace("$", ""))}
            )
        
        await conn.commit()
    print("Database initialization complete.")

if __name__ == "__main__":
    is_db_exists = asyncio.run(create_database_if_not_exists())
    if not is_db_exists:
        asyncio.run(init_db())