"use client";
import { useState } from "react";
import {
  CardNumberElement,
  CardExpiryElement,
  CardCvcElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";

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

export function ManualCheckout({ clientSecret }: { clientSecret: string }) {
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

      {message && message.includes("success") ? (
        <></>
      ) : (
        <button
          disabled={!stripe || isLoading}
          className="w-full mt-2 py-3 bg-[#4F5759] text-white rounded-md font-semibold hover:bg-slate-600 hover:cursor-pointer transition-all disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isLoading ? "Processing..." : "Pay Now"}
        </button>
      )}

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
