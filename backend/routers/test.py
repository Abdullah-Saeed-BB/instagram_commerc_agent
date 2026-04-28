# These are test routes that simulate what the AI Agent sends.
# Should be removed or locked down in production.
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe
import os
from datetime import datetime

import uuid
from db.session import get_db
from db.models import Booking, Barber, Services
from dependencies import get_arq_pool

router = APIRouter()

frontend_url = os.getenv("FRONTEND_URL")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class BillData(BaseModel):
    service_id: Optional[uuid.UUID] = None
    booking_datetime: Optional[datetime] = None
    name: Optional[str] = None
    barber_id: Optional[uuid.UUID] = None


@router.post("/create-payment")
async def create_payment(
    bill_data: BillData = None,
    db: AsyncSession = Depends(get_db),
    arq_pool=Depends(get_arq_pool),
):
    data = bill_data.model_dump()

    # ── Validate booking_datetime ─────────────────────────────────────────────
    booking_dt = data.get("booking_datetime")
    if booking_dt:
        # Strip timezone info to compare against naive datetime.now()
        if booking_dt.tzinfo is not None:
            booking_dt = booking_dt.replace(tzinfo=None)
        if booking_dt < datetime.now():
            raise HTTPException(status_code=400, detail="Booking datetime must be in the future")
    data["booking_datetime"] = booking_dt

    try:
        # ── Resolve service ───────────────────────────────────────────────────
        service_result = None
        service_id = None
        if data.get("service_id"):
            stmt = select(Services).where(Services.id == data["service_id"])
            service_result = (await db.execute(stmt)).scalar_one_or_none()
            service_id = service_result.id if service_result else None

        # ── Resolve barber ────────────────────────────────────────────────────
        barber_id = None
        if data.get("barber_id"):
            stmt = select(Barber).where(Barber.id == data["barber_id"])
            barber_result = (await db.execute(stmt)).scalar_one_or_none()
            barber_id = barber_result.id if barber_result else None

        # ── Create Stripe PaymentIntent only when booking is complete ─────────
        intent_id = None
        is_complete = all([
            service_id,
            service_result,
            barber_id,
            data.get("name"),
            data.get("booking_datetime"),
        ])
        if is_complete:
            intent = stripe.PaymentIntent.create(
                amount=int(service_result.price * 100),
                currency="usd",
                automatic_payment_methods={"enabled": True},
            )
            intent_id = intent.id

        # ── Persist booking ───────────────────────────────────────────────────
        new_booking = Booking(
            payment_id=intent_id,
            service_id=service_id,
            barber_id=barber_id,
            booking_datetime=data.get("booking_datetime"),
            customer_name=data.get("name"),
        )
        db.add(new_booking)
        await db.commit()
        await db.refresh(new_booking)

        # ── Schedule auto-cancel after 30 minutes ─────────────────────────────
        await arq_pool.enqueue_job(
            "cancel_booking_task",
            booking_id=str(new_booking.id),
            _defer_by=30 * 60,
        )

        payment_link = f"{frontend_url}/payment?id={new_booking.id}"
        return {
            "payment_link": payment_link,
            "booking_id": str(new_booking.id),
            "is_complete": is_complete,
            "needs_info": not is_complete,
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
