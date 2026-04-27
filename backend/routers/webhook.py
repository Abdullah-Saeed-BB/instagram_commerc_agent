import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.session import get_db
from db.models import Booking, PaymentStatus
from services.generate_bill import generate_bill

router = APIRouter()


@router.post("")
async def webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle Stripe webhook events.
    - payment_intent.succeeded  → mark booking SUCCESSFUL and generate PDF bill
    - payment_intent.payment_failed → mark booking FAILED
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    # ── Verify Stripe signature ────────────────────────────────────────────────
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        if event["type"] == "payment_intent.succeeded":
            payment_id = event["data"]["object"]["id"]

            stmt = (
                select(Booking)
                .options(selectinload(Booking.service), selectinload(Booking.barber))
                .where(Booking.payment_id == payment_id)
            )
            result = await db.execute(stmt)
            booking = result.scalar_one_or_none()

            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")

            booking.payment_status = PaymentStatus.SUCCESSFUL

            # Generate PDF bill (non-fatal if it fails)
            try:
                generate_bill(
                    filename=f"./bills/{str(booking.id)[:8]}.pdf",
                    barber_name=booking.barber.name if booking.barber else "N/A",
                    booking_datetime=booking.booking_datetime,
                    service_name=booking.service.name if booking.service else "N/A",
                    price=booking.service.price if booking.service else 0,
                    payment_status=booking.payment_status.value,
                    customer_name=booking.customer_name or "N/A",
                    booking_id=booking.id,
                )
            except Exception as bill_err:
                print(f"[Webhook] Bill generation failed: {bill_err}")

            await db.commit()

        elif event["type"] == "payment_intent.payment_failed":
            payment_id = event["data"]["object"]["id"]

            stmt = select(Booking).where(Booking.payment_id == payment_id)
            result = await db.execute(stmt)
            booking = result.scalar_one_or_none()

            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")

            booking.payment_status = PaymentStatus.FAILED
            await db.commit()

        else:
            print(f"[Webhook] Unhandled event type: {event['type']}  ID: {event['id']}")

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Webhook] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}
