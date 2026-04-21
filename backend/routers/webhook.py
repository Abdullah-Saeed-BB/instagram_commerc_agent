from fastapi import APIRouter
from db.session import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Request, Depends, HTTPException
from db.models import Booking
import stripe
import os

router = APIRouter()

@router.post("")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        if event["type"] == "payment_intent.succeeded":
            payment_id = event["data"]["object"]["id"]
            stmt = select(Booking).where(Booking.payment_id == payment_id)
            result = await db.execute(stmt)
            booking = result.scalar_one_or_none()
            
            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")
            
            booking.payment_status = "SUCCESSFUL"
            await db.commit()


        elif event["type"] == "payment_intent.payment_failed":
            payment_id = event["data"]["object"]["id"]
            stmt = select(Booking).where(Booking.payment_id == payment_id)
            result = await db.execute(stmt)
            booking = result.scalar_one_or_none()
            
            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")
            
            booking.payment_status = "FAILED"
            await db.commit()
        else:
            print("Unknown Payment type:", event["type"], " ID:", event["id"])
    except Exception as e:
        print("Webhook - Error message:", e)
        raise HTTPException(status_code=500, detail=str(e))