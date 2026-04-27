import stripe
import os
from dotenv import load_dotenv
from db.models import Booking, PaymentStatus
from sqlalchemy import select
from arq.connections import RedisSettings
from db.session import AsyncSessionLocal

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

async def cancel_booking_task(ctx, booking_id: str):
    async with AsyncSessionLocal() as db:
        try:
            stmt = select(Booking).where(Booking.id == booking_id)
            result = await db.execute(stmt)
            booking = result.scalar_one_or_none()
            
            if not booking:
                print(f"Booking {booking_id} not found")
                return
            
            intent = stripe.PaymentIntent.retrieve(booking.payment_id)
            
            if intent.status != "succeeded" and booking.payment_status != PaymentStatus.SUCCESSFUL:
                booking.payment_status = PaymentStatus.CANCELED
                await db.commit()
                print(f"Booking {booking_id} cancelled (Payment status: {intent.status})")
            else:
                print(f"Booking {booking_id} confirmed or already paid.")

        except Exception as e:
            print(f"Error while checking booking {booking_id}: {e}")
            await db.rollback()

async def on_shutdown(ctx):
    from db.session import engine
    await engine.dispose()
    print("Database engine disposed.")

class WorkerSettings:
    functions = [cancel_booking_task]
    redis_settings = RedisSettings()
    on_shutdown = on_shutdown

