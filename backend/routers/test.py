# These are some test routes, that should be removed in production.
# It perform the AI operations as test.
from fastapi import APIRouter, Request
from db.session import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from db.models import Booking, Barber, Services
import stripe
from datetime import datetime
import os
from dependencies import get_arq_pool

router = APIRouter()

frontend_url = os.getenv("FRONTEND_URL")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/create-payment")
async def create_payment(db: Session = Depends(get_db), arq_pool = Depends(get_arq_pool)):
    bill_data = {
        # "service": "the_signature_fade",
        # "booking_datetime": datetime(2026, 4, 29, 10, 0, 0),
        # "name": "Khalid",
        # "barber": "Moe Johnson"
    }

    if "booking_datetime" in bill_data and bill_data["booking_datetime"] < datetime.now():
        raise HTTPException(status_code=400, detail="Booking datetime must be in the future")

    try:
        service_id = None
        if "service" in bill_data:        
            service_id_stmt = select(Services).where(Services.name == bill_data["service"])
            service_result = (await db.execute(service_id_stmt)).scalar_one_or_none()
            service_id = service_result.id if service_result else None

        barber_id = None
        if "barber" in bill_data:
            barber_id_stmt = select(Barber).where(Barber.name == bill_data["barber"])
            barber_result = (await db.execute(barber_id_stmt)).scalar_one_or_none()
            barber_id = barber_result.id if barber_result else None

        intent_id = None
        if service_id and service_result and barber_id and bill_data.get("name") and bill_data.get("booking_datetime"):
            intent = stripe.PaymentIntent.create(
                amount=int(service_result.price * 100),
                currency="usd",
                automatic_payment_methods={"enabled": True},
            )
            intent_id = intent.id

        new_booking = Booking(
            payment_id=intent_id, service_id=service_id, barber_id=barber_id,
            booking_datetime=bill_data.get("booking_datetime"),
            customer_name=bill_data.get("name")
        )
        db.add(new_booking)
        await db.commit()

        await arq_pool.enqueue_job(
            'cancel_booking_task',
            booking_id=new_booking.id,
            _defer_by=30 * 60
        )

        payment_link = f"{frontend_url}/payment?id={new_booking.id}"

        return payment_link
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
