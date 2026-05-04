from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from collections import Counter
from datetime import datetime, date
import uuid
import stripe
import os

from db.session import get_db
from db.models import Booking, Barber, Services, PaymentStatus
from services.get_slots import generate_slots

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class BookingUpdate(BaseModel):
    customer_name: Optional[str] = None
    booking_datetime: Optional[datetime] = None
    service: Optional[str] = None
    barber: Optional[str] = None


# ── GET /booking/data/services ─────────────────────────────────────────────────
@router.get("/data/services")
async def get_services(db: AsyncSession = Depends(get_db)):
    """Return all available services."""
    result = await db.execute(select(Services))
    services = result.scalars().all()
    return [{"id": str(s.id), "name": s.name, "price": float(s.price)} for s in services]


# ── GET /booking/data/barbers ──────────────────────────────────────────────────
@router.get("/data/barbers")
async def get_barbers(db: AsyncSession = Depends(get_db)):
    """Return all barbers."""
    result = await db.execute(select(Barber))
    barbers = result.scalars().all()
    return [{"id": str(b.id), "name": b.name} for b in barbers]


# ── GET /booking/availability ──────────────────────────────────────────────────
from collections import defaultdict

@router.get("/availability")
async def get_availability(
    date: date,
    barber_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return available 30-minute slots for a given date.
    Returns a list of objects containing the time and names of available barbers.
    """
    all_slots = generate_slots()

    # 1. Fetch all active barbers
    barber_stmt = select(Barber)
    if barber_id:
        barber_stmt = barber_stmt.where(Barber.id == barber_id)
    
    barbers_result = await db.execute(barber_stmt)
    active_barbers = barbers_result.scalars().all()
    
    # Create a lookup for barber names by ID
    barber_lookup = {b.id: b.name for b in active_barbers}

    # 2. Fetch existing bookings
    stmt = (
        select(Booking)
        .where(func.date(Booking.booking_datetime) == date)
        .where(Booking.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.SUCCESSFUL]))
        .where(Booking.payment_id != None)
    )
    result = await db.execute(stmt)
    bookings = result.scalars().all()

    # 3. Create a map of {time: [list_of_booked_barber_ids]}
    booked_map = defaultdict(set)
    for b in bookings:
        time_key = b.booking_datetime.time()
        booked_map[time_key].add(b.barber_id)

    # 4. Build the structured response
    available_data = []
    
    for slot_time in all_slots:
        # Filter out barbers who are already booked at this specific time
        free_barbers = [
            {"id": b_id, "name": b_name}
            for b_id, b_name in barber_lookup.items()
            if b_id not in booked_map[slot_time]
        ]

        # Only add the slot if there is at least one barber free
        if free_barbers:
            available_data.append({
                "time": slot_time.strftime("%H:%M"),
                "available_barbers": free_barbers
            })

    return {
        "date": date,
        "available_slots": available_data,
    }


# ── GET /booking/{id} ─────────────────────────────────────────────────────────
@router.get("/{id}")
async def get_booking(id: str, db: AsyncSession = Depends(get_db)):
    """Fetch a booking by ID, sync payment status from Stripe if needed."""
    try:
        stmt = (
            select(Booking)
            .options(selectinload(Booking.barber), selectinload(Booking.service))
            .where(Booking.id == id)
        )
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        client_secret = None
        if booking.payment_id:
            intent = stripe.PaymentIntent.retrieve(booking.payment_id)
            if intent.status == "succeeded" and booking.payment_status != PaymentStatus.SUCCESSFUL:
                booking.payment_status = PaymentStatus.SUCCESSFUL
                await db.commit()
            elif intent.status == "canceled" and booking.payment_status not in (
                PaymentStatus.FAILED, PaymentStatus.CANCELED
            ):
                booking.payment_status = PaymentStatus.FAILED
                await db.commit()
            client_secret = intent.client_secret

        return {
            "id": str(booking.id),
            "service": booking.service.name if booking.service else None,
            "amount": float(booking.service.price) if booking.service else None,
            "booking_datetime": booking.booking_datetime.isoformat() if booking.booking_datetime else None,
            "customer_name": booking.customer_name,
            "client_secret": client_secret,
            "payment_status": booking.payment_status,
            "barber": {"name": booking.barber.name} if booking.barber else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── PUT /booking/{id} ─────────────────────────────────────────────────────────
@router.put("/{id}")
async def update_booking(
    id: str,
    booking_update: BookingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a pending booking's fields.
    If all required fields become present after the update, create or update
    the Stripe PaymentIntent automatically.
    """
    try:
        stmt = (
            select(Booking)
            .options(selectinload(Booking.barber), selectinload(Booking.service))
            .where(Booking.id == id)
        )
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if booking.payment_status == PaymentStatus.SUCCESSFUL:
            raise HTTPException(status_code=400, detail="Cannot edit a confirmed booking")

        # ── Apply field updates ───────────────────────────────────────────────
        if booking_update.customer_name is not None:
            booking.customer_name = booking_update.customer_name

        if booking_update.booking_datetime is not None:
            dt = booking_update.booking_datetime
            # Strip timezone to store as naive datetime (DB column is naive)
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            booking.booking_datetime = dt

        if booking_update.service is not None:
            service_stmt = select(Services).where(Services.name == booking_update.service)
            service = (await db.execute(service_stmt)).scalar_one_or_none()
            if not service:
                raise HTTPException(status_code=404, detail="Service not found")
            booking.service_id = service.id
            booking.service = service

        if booking_update.barber is not None:
            barber_stmt = select(Barber).where(Barber.name == booking_update.barber)
            barber = (await db.execute(barber_stmt)).scalar_one_or_none()

            if not barber:
                raise HTTPException(status_code=404, detail="Barber not found")
            
            is_barber_free = (await db.execute(select(Booking).where(Booking.barber_id == barber.id, Booking.booking_datetime == booking.booking_datetime)))
            if is_barber_free:
                raise HTTPException(status_code=400, detail="Barber is not free at the selected time")

            booking.barber_id = barber.id
            booking.barber = barber

        # ── Create or update Stripe intent when all fields are present ────────
        if all([booking.customer_name, booking.booking_datetime, booking.service_id, booking.barber_id]):
            if not booking.payment_id:
                intent = stripe.PaymentIntent.create(
                    amount=int(booking.service.price * 100),
                    currency="usd",
                    automatic_payment_methods={"enabled": True},
                )
                booking.payment_id = intent.id
            else:
                # Update amount in case the service changed
                stripe.PaymentIntent.modify(
                    booking.payment_id,
                    amount=int(booking.service.price * 100),
                )

        await db.commit()
        return {"status": "success"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
