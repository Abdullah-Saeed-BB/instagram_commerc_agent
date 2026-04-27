"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";
import { BookingData } from "@/components/payment/types";
import { BookingSummary } from "@/components/payment/BookingSummary";
import { BookingForm } from "@/components/payment/BookingForm";
import { CheckoutForm } from "@/components/payment/CheckoutForm";

const stripePromise = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
  ? loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)
  : null;

function PaymentContent() {
  const searchParams = useSearchParams();
  const id = searchParams.get("id");
  const payment_intent_client_secret = searchParams.get(
    "payment_intent_client_secret",
  );

  const [booking, setBooking] = useState<BookingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBooking = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/booking/${id}`,
      );
      if (!res.ok) {
        throw new Error("Failed to load booking");
      }
      const data = await res.json();
      setBooking(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooking();
  }, [id]);

  if (!id) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center max-w-sm w-full">
          <p className="text-gray-600">No booking ID provided.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="animate-pulse text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error || !booking) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center max-w-sm w-full">
          <p className="text-red-600">{error || "Booking not found."}</p>
        </div>
      </div>
    );
  }

  // Handle successful payment redirect
  if (payment_intent_client_secret && booking.payment_status === "SUCCESSFUL") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-green-200 text-center max-w-sm w-full">
          <h2 className="text-2xl font-bold text-green-600 mb-2">
            Payment Successful!
          </h2>
          <p className="text-gray-600">Your booking is confirmed.</p>
        </div>
      </div>
    );
  }

  const isComplete =
    booking.client_secret && booking.payment_status === "PENDING";
  console.log(booking.client_secret, booking.payment_status);

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900">Silver Blade</h1>
          <p className="mt-2 text-gray-600">Complete your booking securely</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <BookingSummary booking={booking} />
          </div>

          <div>
            {!isComplete ? (
              <BookingForm booking={booking} onSuccess={fetchBooking} />
            ) : (
              stripePromise && (
                <Elements
                  stripe={stripePromise}
                  options={{ clientSecret: booking.client_secret! }}
                >
                  <CheckoutForm clientSecret={booking.client_secret!} />
                </Elements>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PaymentPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="animate-pulse text-gray-500">Loading...</div>
        </div>
      }
    >
      <PaymentContent />
    </Suspense>
  );
}
