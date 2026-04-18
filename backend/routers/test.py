# These are some test routes, that should be removed in production.
# It perform the AI operations as test.
from fastapi import APIRouter
from db.session import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from db.models import Booking, Barber
import stripe
from datetime import datetime
import os

router = APIRouter()

frontend_url = os.getenv("FRONTEND_URL")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/create-payment")
async def create_payment(db: Session = Depends(get_db)):
    bill_data = {
        "service": "cutting-hair",
        "price": 20, 
        "booking_datetime": datetime(2026, 4, 14, 10, 0, 0),
        "name": "Khalid",
        "barber": "Moe Johnson"
    } 


    try:
        intent = stripe.PaymentIntent.create(
            amount=bill_data["price"] * 100,
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )

        barber_id_stmt = select(Barber).where(Barber.name == bill_data["barber"])
        result = (await db.execute(barber_id_stmt)).scalar_one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Barber not found")
        barber_id = result.id

        new_booking = Booking(
            payment_id=intent.id, service=bill_data["service"],
            amount=bill_data["price"], booking_datetime=bill_data["booking_datetime"],
            customer_name=bill_data["name"], barber_id=barber_id
        )
        db.add(new_booking)
        await db.commit()

        payment_link = f"{frontend_url}/payment?id={new_booking.id}"

        return payment_link
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
