# def main():
#     print("Hello from insta-commerc-agent!")


# if __name__ == "__main__":
#     main()

from db.session import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import stripe
import os
from datetime import datetime

from db.models import Booking, Barber

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
frontend_url = os.getenv("FRONTEND_URL")

@app.post("/create-payment")
async def create_payment(db: Session = Depends(get_db)):
    bill_data = {
        "service": "cutting-hair",
        "price": 20, 
        "booking_datetime": datetime(2026, 4, 14, 10, 0, 0),
        "name": "Khalid",
        "barber": "Moe Jonson"
    } 

    intent = stripe.PaymentIntent.create(
        amount=bill_data["price"] * 100,
        currency="usd",
        automatic_payment_methods={"enabled": True},
    )

    try:
        barber_id_stmt = select(Barber).where(Barber.name == bill_data["barber"])
        barber_id = (await db.execute(barber_id_stmt)).scalar_one().id

        print(barber_id)

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
        return {"status": "error", "message": str(e)}

@app.get("/booking/{id}")
async def get_booking(id: str, db: Session = Depends(get_db)):
    try:
        stmt = select(Booking).options(selectinload(Booking.barber)).where(Booking.id == id)
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Fetch payment intent from stripe to get client_secret
        intent = stripe.PaymentIntent.retrieve(booking.payment_id)
        
        return {
            "id": str(booking.id),
            "service": booking.service,
            "amount": float(booking.amount),
            "booking_datetime": booking.booking_datetime.isoformat(),
            "customer_name": booking.customer_name,
            "client_secret": intent.client_secret,
            "payment_status": intent.status,
            "barber": {
                "name": booking.barber.name
            }
        }
    except Exception as e:
        print(f"Error fetching booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return {"status": "error", "message": str(e)} 

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        print("Payment Type is confirmed. Payment ID:", event["id"], "  Intent ID:", intent["id"])

        # ✅ Update database (VERY IMPORTANT)
    else:
        print("Payment Type is:", event["type"], "\n  Payment ID:", event["id"])

    return {"status": "success", "message": "Payment confirmed"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)