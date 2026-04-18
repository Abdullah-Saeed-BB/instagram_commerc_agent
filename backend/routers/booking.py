from fastapi import APIRouter
from db.session import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from fastapi import Depends, HTTPException
from db.models import Booking
import stripe

router = APIRouter()

@router.get("/{id}")
async def get_booking(id: str, db: Session = Depends(get_db)):
    try:
        stmt = select(Booking).options(selectinload(Booking.barber)).where(Booking.id == id)
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()
        
        if not booking:
            return HTTPException(status_code=404, detail="Booking not found")

        # Fetch payment intent from stripe to get client_secret
        intent = stripe.PaymentIntent.retrieve(booking.payment_id)
        
        return {
            "id": str(booking.id),
            "service": booking.service,
            "amount": float(booking.amount),
            "booking_datetime": booking.booking_datetime.isoformat(),
            "customer_name": booking.customer_name,
            "client_secret": intent.client_secret,
            "payment_status": booking.payment_status,
            "barber": {
                "name": booking.barber.name
            }
        }
    except Exception as e:
        print(f"Error fetching booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))
