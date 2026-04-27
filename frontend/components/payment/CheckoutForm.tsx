import React, { useState } from "react";
import {
  CardNumberElement,
  CardExpiryElement,
  CardCvcElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";

interface CheckoutFormProps {
  clientSecret: string;
}

const inputStyle = {
  style: {
    base: {
      fontSize: "16px",
      color: "#374151",
      fontFamily: "ui-sans-serif, system-ui, sans-serif",
      "::placeholder": { color: "#9CA3AF" },
    },
    invalid: { color: "#ef4444" },
  },
};

export const CheckoutForm: React.FC<CheckoutFormProps> = ({ clientSecret }) => {
  const stripe = useStripe();
  const elements = useElements();

  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsLoading(true);
    setMessage(null);

    const { error, paymentIntent } = await stripe.confirmCardPayment(
      clientSecret,
      {
        payment_method: {
          card: elements.getElement(CardNumberElement)!,
        },
      }
    );

    console.log("Error message:", error);

    if (error) {
      setMessage(error.message || "An error occurred.");
    } else if (paymentIntent?.status === "succeeded") {
      setMessage("Payment successful!");
      window.location.reload();
    } else {
      setMessage("An unexpected status occurred.");
    }

    setIsLoading(false);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
    >
      <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">
        Payment Details
      </h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Card Number
          </label>
          <div className="p-3 border border-gray-300 rounded-md bg-white shadow-sm">
            <CardNumberElement options={inputStyle} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expiration
            </label>
            <div className="p-3 border border-gray-300 rounded-md bg-white shadow-sm">
              <CardExpiryElement options={inputStyle} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              CVC
            </label>
            <div className="p-3 border border-gray-300 rounded-md bg-white shadow-sm">
              <CardCvcElement options={inputStyle} />
            </div>
          </div>
        </div>
      </div>

      {message && message.includes("success") ? null : (
        <button
          disabled={isLoading || !stripe || !elements}
          id="submit"
          className="mt-6 w-full bg-blue-600 text-white font-medium py-2 px-4 rounded-md hover:bg-blue-700 transition disabled:opacity-50"
        >
          <span id="button-text">{isLoading ? "Processing..." : "Pay now"}</span>
        </button>
      )}

      {message && (
        <div className={`mt-4 p-3 rounded text-sm text-center ${message.includes("success") ? "bg-green-50 text-green-600" : "bg-red-50 text-red-600"}`}>
          {message}
        </div>
      )}
    </form>
  );
};
