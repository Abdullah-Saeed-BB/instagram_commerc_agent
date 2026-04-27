# Project Plan: Barber AI Booking Backend

This document outlines the development strategy for the Barber Business Booking API. The goal is to facilitate a seamless transition from an AI-driven conversation to a secure payment fulfillment process using FastAPI, Stripe, and PostgreSQL.

---

## 1. Project Description

The backend serves as the orchestration layer between a (simulated) AI Agent and the Stripe payment gateway. It manages "soft" booking records that may contain incomplete data.

**The core logic handles two paths:**

- **Incomplete Data:** Creates a booking record and returns a redirect/flag to the frontend to gather missing information.
- **Complete Data:** Creates a booking record, initializes a Stripe Payment Intent immediately, and returns the client secret for payment.

---

## 2. Project Structure

We will follow a modular FastAPI structure to ensure scalability and separation of concerns.

```text
barber_backend/
├── app/
│   ├── db/
│   │   ├── init_db.py         # Init the database, run it once to create the database tables
│   │   ├── models.py          # SQLAlchemy models (as provided)
│   │   └── session.py         # SQLAlchemy engine and session logic
│   ├── services/
│   │   ├── stripe_service.py  # Logic for Stripe Payment Intent creation
│   │   └── booking_service.py # Logic for handling DB operations
│   ├── api/
│   │   └── routes/
│   │       └── test_agent.py  # The 'create-payment' endpoint
│   └── main.py                # FastAPI app initialization
├── .env                       # Secrets (STRIPE_SECRET_KEY, etc.)
├── requirements.txt
└── docker-compose.yml         # For Postgres and Redis
```

---

## 3. Plan Working Steps

### Phase 1: Environment Setup

- Initialize FastAPI with a virtual environment.
- Configure **PostgreSQL** connection via SQLAlchemy.
- Set up **Redis** for caching or session management (if required for complex state).
- Install Stripe Python SDK and configure API keys.

### Phase 2: Core Logic Implementation

- **Model Integration:** Implement the provided SQLAlchemy models into the `models/` directory.
- **Stripe Service:** Create a utility to generate `PaymentIntents` based on the `service.price`.
- **Service Layer:** Write logic to check if a booking is "Complete" (Customer Name, Service, Barber, and Datetime are all present).

### Phase 3: Route Development (`create-payment`)

- **Input:** Receive JSON containing booking details.
- **Persistence:** Save the initial booking record with `PaymentStatus.PENDING`.
- **Conditional Logic:**
  - If **Complete**: Call Stripe API $\rightarrow$ update `payment_id` $\rightarrow$ return `client_secret`.
  - If **Incomplete**: Return the `booking_id` and a `needs_info` flag to the frontend.

### Phase 4: Webhook & Cleanup (Optional but Recommended)

- Implement a Stripe Webhook to update `PaymentStatus` to `SUCCESSFUL` once the event `payment_intent.succeeded` is received.

---

## 4. Questions & Vagueness

To ensure the backend logic aligns with your vision, please clarify the following:

1.  **Price Fetching:** Since `Booking` only receives a `service_id`, should I assume the `price` must be queried from the `Services` table before hitting Stripe, or will the AI Agent provide the amount? Answer: The price is dependent on the service price, so AI agent should not provide the amount.

2.  **Redirect URL:** When a Stripe intent is generated, do you want me to provide a `success_url` and `cancel_url` for Stripe Checkout, or are you using Stripe Elements (where I only return the `client_secret`)? Answer:

3.  **Redis Usage:** You mentioned **Redis** in the tools—is this intended for rate limiting, session storage for the incomplete booking, or as a message broker for tasks? Answer: The only use of it, is to cancel the booking after 30 minutes if the customer didn't pay yet.

4.  **Working datetime:** What is the accepted working datetime of the barber shop, how the schedule of barber working? Answer: The working datetime starts from 9:00 AM to 6:00 PM, and booking datetime the minutes must be multiples of 30 (e.g. 9:30, 10:00, 14:30, etc).

5.  **Can a barber have more than one booking at the same time?** Answer: No, a barber can't have more than one booking at the same time.
