"use client";

import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Image from "next/image";
import { loadStripe } from "@stripe/stripe-js";
import {
  Elements,
  CardNumberElement,
  CardExpiryElement,
  CardCvcElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";

const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const stripePromise = publishableKey ? loadStripe(publishableKey) : null;

// Shared styles for the individual inputs
const inputStyle = {
  style: {
    base: {
      fontSize: "16px",
      color: "#087BA3",
      fontFamily: "ui-sans-serif, system-ui, sans-serif",
      "::placeholder": { color: "#51A1BD" },
    },
    invalid: { color: "#ef4444" },
  },
};

function ManualCheckout({ clientSecret }: { clientSecret: string }) {
  const stripe = useStripe();
  const elements = useElements();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setIsLoading(true);
    setMessage(null);

    const { error, paymentIntent } = await stripe.confirmCardPayment(
      clientSecret,
      {
        payment_method: {
          card: elements.getElement(CardNumberElement)!,
        },
      },
    );

    if (error) {
      setMessage(error.message ?? "Payment failed");
    } else if (paymentIntent?.status === "succeeded") {
      setMessage("Payment successful!");
    }

    setIsLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4">
      {/* 1. Card Number Input */}
      <div>
        <label className="block text-sm font-medium text-[#51A1BD] mb-1">
          Card Number
        </label>
        <div className="p-3 border border-gray-200 rounded-lg bg-white shadow-sm">
          <CardNumberElement options={inputStyle} />
        </div>
      </div>

      {/* 2. Expiry and CVC Row */}
      <div className="flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-[#51A1BD] mb-1">
            Expiration
          </label>
          <div className="p-3 border border-gray-200 rounded-lg bg-white shadow-sm">
            <CardExpiryElement options={inputStyle} />
          </div>
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium text-[#51A1BD] mb-1">
            CVC
          </label>
          <div className="p-3 border border-gray-200 rounded-lg bg-white shadow-sm">
            <CardCvcElement options={inputStyle} />
          </div>
        </div>
      </div>

      <button
        disabled={!stripe || isLoading}
        className="w-full mt-2 py-3 bg-[#4F5759] text-white rounded-md font-semibold hover:bg-opacity-90 transition-all disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {isLoading ? "Processing..." : "Pay Now"}
      </button>

      {message && (
        <p
          className={`mt-4 text-sm text-center ${message.includes("successful") ? "text-green-600" : "text-red-500"}`}
        >
          {message}
        </p>
      )}
    </form>
  );
}

function PaymentContent() {
  const searchParams = useSearchParams();
  const clientSecret = searchParams.get("client_secret");

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
    <div className="min-h-screen bg-[#F5F7F7] flex flex-col items-center justify-center p-4">
      {/* Brand Section */}
      <div className="mb-8 text-center">
        <div className="relative w-16 h-16 mx-auto mb-3">
          <Image
            src="/logo.png"
            alt="Logo"
            fill
            className="object-contain"
            priority
          />
        </div>
        <h1 className="text-2xl font-bold text-[#087BA3]">Silver blade</h1>
      </div>

      {/* Payment Container */}
      <div className="w-full max-w-md bg-white p-6 sm:p-10 rounded-2xl shadow-sm border border-gray-100">
        <Elements stripe={stripePromise}>
          <ManualCheckout clientSecret={clientSecret} />
        </Elements>
      </div>
      <span className="mt-4 text-sm w-full italic text-center text-slate-400">
        For <b>Card Number</b> just enter 4242 4242 4242 4242
        <br />
        for <b>Expiration</b> enter any feature date, and <b>CVC</b> enter any
        random values
      </span>
    </div>
  );
}

export default function FinalPaymentPage() {
  return (
    <Suspense fallback={<div className="h-screen bg-[#F5F7F7]" />}>
      <PaymentContent />
    </Suspense>
  );
}
