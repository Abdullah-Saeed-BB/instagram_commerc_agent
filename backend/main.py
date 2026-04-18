from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import stripe
import os

from dotenv import load_dotenv
load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI()

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