# def main():
#     print("Hello from insta-commerc-agent!")


# if __name__ == "__main__":
#     main()

from fastapi import FastAPI, Request
from dotenv import load_dotenv
import uvicorn
import stripe
import os

load_dotenv()

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
frontend_url = os.getenv("FRONTEND_URL")

@app.post("/create-payment")
def create_payment():
    bill_data = {
        "service": "cut-hair",
        "price": 20, 
        "booking_datetime": "2026-04-14T10:00:00",
        "name": "Khalid",
        "barber": "Moe"
    } 

    intent = stripe.PaymentIntent.create(
        amount=bill_data["price"] * 100,
        currency="usd",
        automatic_payment_methods={"enabled": True},
    )

    payment_link = f"{frontend_url}/payment?client_secret={intent.client_secret}&"

    for key, value in bill_data.items():
        payment_link += f"{key}={value}&"
    payment_link = payment_link[:-1]

    return {"payment_link": payment_link}


@app.post("/webhook")
async def webhook(request: Request):
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
        print("Payment Type is confirmed:", intent["id"])

        # ✅ Update database (VERY IMPORTANT)
    else:
        print("Payment Type is:", event["type"], "\n  Payment ID:", event["id"])

    return {"status": "success", "message": "Payment confirmed"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)