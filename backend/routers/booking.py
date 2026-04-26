from fastapi import APIRouter
from db.session import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from fastapi import Depends, HTTPException
from db.models import Booking, Barber, Services
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class BookingUpdate(BaseModel):
    customer_name: Optional[str] = None
    booking_datetime: Optional[datetime] = None
    service: Optional[str] = None
    barber: Optional[str] = None

router = APIRouter()

@router.get("/data/services")
async def get_services(db: Session = Depends(get_db)):
    stmt = select(Services)
    result = await db.execute(stmt)
    services = result.scalars().all()
    return [{"id": str(s.id), "name": s.name, "price": s.price} for s in services]

@router.get("/data/barbers")
async def get_barbers(db: Session = Depends(get_db)):
    stmt = select(Barber)
    result = await db.execute(stmt)
    barbers = result.scalars().all()
    return [{"id": str(b.id), "name": b.name} for b in barbers]

@router.get("/{id}")
async def get_booking(id: str, db: Session = Depends(get_db)):
    try:
        stmt = select(Booking).options(
            selectinload(Booking.barber),
            selectinload(Booking.service)
        ).where(Booking.id == id)
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        client_secret = None
        if booking.payment_id:
            # Fetch payment intent from stripe to get client_secret
            intent = stripe.PaymentIntent.retrieve(booking.payment_id)
            if intent.status == "succeeded" and booking.payment_status != "SUCCESSFUL":
                booking.payment_status = "SUCCESSFUL"
                await db.commit()
            elif intent.status == "canceled" and (booking.payment_status != "FAILED" or booking.payment_status != "CANCELED"):
                booking.payment_status = "FAILED"
                await db.commit()
            client_secret = intent.client_secret
        
        return {
            "id": str(booking.id),
            "service": booking.service.name if booking.service else None,
            "amount": booking.service.price if booking.service else None,
            "booking_datetime": booking.booking_datetime.isoformat() if booking.booking_datetime else None,
            "customer_name": booking.customer_name,
            "client_secret": client_secret,
            "payment_status": booking.payment_status,
            "barber": {
                "name": booking.barber.name if booking.barber else None
            } if booking.barber else None
        }
    except Exception as e:
        print(f"Error fetching booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}")
async def update_booking(id: str, booking_update: BookingUpdate, db: Session = Depends(get_db)):
    try:
        stmt = select(Booking).options(
            selectinload(Booking.barber),
            selectinload(Booking.service)
        ).where(Booking.id == id)
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
            
        if booking.payment_status == "SUCCESSFUL":
            raise HTTPException(status_code=400, detail="Cannot edit a confirmed booking")

        if booking_update.customer_name is not None:
            booking.customer_name = booking_update.customer_name
            
        if booking_update.booking_datetime is not None:
            # Strip timezone info to match database naive timestamp column
            dt = booking_update.booking_datetime
            if dt.tzinfo is not None:
                booking.booking_datetime = dt.replace(tzinfo=None)
            else:
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
            booking.barber_id = barber.id
            booking.barber = barber
            
        # If all fields are present, generate or update stripe intent
        if booking.customer_name and booking.booking_datetime and booking.service_id and booking.barber_id:
            if not booking.payment_id:
                # Generate new intent
                intent = stripe.PaymentIntent.create(
                    amount=int(booking.service.price * 100),
                    currency="usd",
                    automatic_payment_methods={"enabled": True},
                )
                booking.payment_id = intent.id
            else:
                # Update existing intent amount just in case service changed
                stripe.PaymentIntent.modify(
                    booking.payment_id,
                    amount=int(booking.service.price * 100)
                )

        await db.commit()
        return {"status": "success"}
    except Exception as e:
        print(f"Error updating booking: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
