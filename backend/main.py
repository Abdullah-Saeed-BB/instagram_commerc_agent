from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import stripe
import os
from arq import create_pool
from arq.connections import RedisSettings
from contextlib import asynccontextmanager
import logging

from dotenv import load_dotenv
load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await create_pool(RedisSettings())
    app.state.arq_pool = pool

    try:
        await pool.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    if not redis_ok:
        raise RuntimeError("Redis is not working")

    worker_keys = await pool.keys("arq:queue:*")
    if not worker_keys:
        raise RuntimeError("No ARQ workers detected")
    
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




from routers import booking, webhook, test

app.include_router(test.router, prefix="/test", tags=["test"])
app.include_router(booking.router, prefix="/booking", tags=["booking"])
app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)