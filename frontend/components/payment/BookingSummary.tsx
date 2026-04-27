import React from "react";
import { BookingData } from "./types";

interface BookingSummaryProps {
  booking: BookingData;
}

export const BookingSummary: React.FC<BookingSummaryProps> = ({ booking }) => {
  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Pending...";
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">
        Booking Summary
      </h2>

      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-500 font-medium">Customer</p>
          <p className="text-gray-900 font-medium">{booking.customer_name || "Pending..."}</p>
        </div>

        <div>
          <p className="text-sm text-gray-500 font-medium">Service</p>
          <p className="text-gray-900 font-medium">
            {booking.service ? (
              <>
                {booking.service}
                {booking.amount && <span className="text-gray-500 ml-2">(${booking.amount})</span>}
              </>
            ) : (
              "Pending..."
            )}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500 font-medium">Barber</p>
          <p className="text-gray-900 font-medium">{booking.barber?.name || "Pending..."}</p>
        </div>

        <div>
          <p className="text-sm text-gray-500 font-medium">Date & Time</p>
          <p className="text-gray-900 font-medium">{formatDate(booking.booking_datetime)}</p>
        </div>
      </div>
    </div>
  );
};
