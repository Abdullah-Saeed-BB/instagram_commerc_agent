"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Image from "next/image";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";
import { ManualCheckout } from "@/components/payment/ManualCheckout";
import { BookingDetails } from "@/components/BookingDetails";

const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const stripePromise = publishableKey ? loadStripe(publishableKey) : null;

function PaymentContent() {
  const searchParams = useSearchParams();
  const clientSecret = searchParams.get("client_secret");
  const service = searchParams.get("service");
  const price = searchParams.get("price");
  const bookingDatetime = searchParams.get("booking_datetime");
  const customer_name = searchParams.get("name");
  const barber = searchParams.get("barber");

  if (!publishableKey) {
    return (
      <div className="p-10 text-center text-[#087BA3]">Missing Stripe Key</div>
    );
  }

  if (!clientSecret) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#F5F7F7] p-4">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 max-w-sm w-full text-center">
          <h2 className="text-[#087BA3] font-bold text-xl mb-2">Error</h2>
          <p className="text-[#51A1BD]">Missing client_secret parameter.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F5F7F7] flex flex-col items-center py-12 px-4 md:pt-20 md:pb-6">
      {/* Brand Section */}
      <div className="mb-12 text-center">
        <div className="relative w-16 h-16 mx-auto mb-4 group">
          <div className="absolute inset-0 bg-[#087BA3] opacity-20 blur-xl group-hover:opacity-30 transition-opacity rounded-full"></div>
          <Image
            src="/logo.png"
            alt="Logo"
            fill
            className="object-contain relative z-10"
            priority
          />
        </div>
        <h1 className="text-3xl font-bold text-[#087BA3] tracking-tight">
          Silver blade
        </h1>
        <p className="text-[#51A1BD] text-sm mt-1">Secure Payment Portal</p>
      </div>

      {/* Responsive Layout Container */}
      <div className="w-full max-w-5xl flex flex-col lg:flex-row items-center lg:items-start justify-center gap-8 lg:gap-12">
        {/* Payment Form Container */}
        <div className="w-full max-w-md bg-white p-8 sm:p-10 rounded-2xl shadow-sm border border-gray-100 order-1 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-[#087BA3]"></div>
          <Elements stripe={stripePromise}>
            <ManualCheckout clientSecret={clientSecret} />
          </Elements>
        </div>

        {/* Booking Details Container */}
        <div className="w-full max-w-md lg:max-w-sm order-2">
          <BookingDetails
            service={service}
            price={price}
            bookingDatetime={bookingDatetime}
            customer_name={customer_name}
            barber={barber}
          />
        </div>
      </div>

      {/* Helper Footer */}
      <div className="mt-12 text-center max-w-md">
        <p className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-4">
          Test Mode Instructions
        </p>
        <span className="text-sm italic text-[#51A1BD] leading-relaxed block bg-white/50 py-3 px-6 rounded-lg border border-slate-100">
          For <b>Card Number</b> enter{" "}
          <code className="text-[#087BA3] font-bold">4242 4242 4242 4242</code>
          <br />
          For <b>Expiration</b> enter any future date, and <b>CVC</b> enter any
          random values
        </span>
      </div>
    </div>
  );
}

export default function FinalPaymentPage() {
  return (
    <Suspense
      fallback={
        <div className="h-screen bg-[#F5F7F7] flex items-center justify-center">
          <div className="w-12 h-12 border-4 border-[#51A1BD] border-t-[#087BA3] rounded-full animate-spin"></div>
        </div>
      }
    >
      <PaymentContent />
    </Suspense>
  );
}
