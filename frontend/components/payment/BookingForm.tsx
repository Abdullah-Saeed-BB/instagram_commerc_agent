import React, { useState, useEffect } from "react";
import { BookingData, ServiceData, BarberData } from "./types";

interface BookingFormProps {
  booking: BookingData;
  onSuccess: () => void;
}

interface AvailableSlot {
  time: string;
  available_barbers: { id: string; name: string }[];
}

export const BookingForm: React.FC<BookingFormProps> = ({
  booking,
  onSuccess,
}) => {
  const [customerName, setCustomerName] = useState(booking.customer_name || "");
  const [service, setService] = useState(booking.service || "");
  const [barber, setBarber] = useState(booking.barber?.name || "");
  const [bookingDate, setBookingDate] = useState("");
  const [bookingTime, setBookingTime] = useState("");

  const [services, setServices] = useState<ServiceData[]>([]);
  const [barbers, setBarbers] = useState<BarberData[]>([]);
  const [availableSlots, setAvailableSlots] = useState<AvailableSlot[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Parse existing datetime if available
  useEffect(() => {
    if (booking.booking_datetime) {
      const dt = new Date(booking.booking_datetime);
      const tzOffset = dt.getTimezoneOffset() * 60000; // offset in milliseconds
      const localISOTime = new Date(dt.getTime() - tzOffset)
        .toISOString()
        .slice(0, 10);
      setBookingDate(localISOTime);

      const hours = dt.getHours().toString().padStart(2, "0");
      const minutes = dt.getMinutes().toString().padStart(2, "0");
      setBookingTime(`${hours}:${minutes}`);
    }
  }, [booking.booking_datetime]);

  // Fetch initial data
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/booking/data/services`)
      .then((res) => res.json())
      .then((data) => setServices(data))
      .catch(console.error);

    fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/booking/data/barbers`)
      .then((res) => res.json())
      .then((data) => setBarbers(data))
      .catch(console.error);
  }, []);

  // Fetch slots when date or barber changes
  useEffect(() => {
    if (bookingDate) {
      let url = `${process.env.NEXT_PUBLIC_BACKEND_URL}/booking/availability?date=${bookingDate}`;

      if (barber) {
        const barberObj = barbers.find((b) => b.name === barber);
        if (barberObj) {
          url += `&barber_id=${barberObj.id}`;
        }
      }

      fetch(url)
        .then((res) => res.json())
        .then((data) => {
          if (data.available_slots) {
            setAvailableSlots(data.available_slots);
            // If the selected time is no longer available, clear it
            if (bookingTime && !data.available_slots.includes(bookingTime)) {
              // We don't clear it immediately in case it's their existing booked slot
            }
          }
        })
        .catch(console.error);
    } else {
      setAvailableSlots([]);
    }
  }, [bookingDate, barber, barbers, bookingTime]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!customerName || !service || !barber || !bookingDate || !bookingTime) {
      setError("Please fill out all fields.");
      setLoading(false);
      return;
    }

    // Combine date and time
    const combinedDateTime = `${bookingDate}T${bookingTime}:00`;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/booking/${booking.id}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            customer_name: customerName,
            service: service,
            barber: barber,
            booking_datetime: combinedDateTime,
          }),
        },
      );

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || "Failed to update booking");
      }

      onSuccess();
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
    >
      <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">
        Complete Booking Details
      </h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-600 rounded text-sm">
          {error}
        </div>
      )}

      <div className="space-y-4 text-gray-600">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Customer Name
          </label>
          <input
            type="text"
            className="w-full border border-gray-300 rounded-md p-2"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Service
          </label>
          <select
            className="w-full border border-gray-300 rounded-md p-2 bg-white"
            value={service}
            onChange={(e) => setService(e.target.value)}
            required
          >
            <option value="">Select a service</option>
            {services.map((s) => (
              <option key={s.id} value={s.name}>
                {s.name} (${s.price})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Barber
          </label>
          <select
            className="w-full border border-gray-300 rounded-md p-2 bg-white"
            value={barber}
            onChange={(e) => setBarber(e.target.value)}
            required
          >
            <option value="">Select a barber</option>
            {barbers.map((b) => (
              <option key={b.id} value={b.name}>
                {b.name}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date
            </label>
            <input
              type="date"
              className="w-full border border-gray-300 rounded-md p-2"
              value={bookingDate}
              onChange={(e) => setBookingDate(e.target.value)}
              min={new Date().toISOString().split("T")[0]}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time
            </label>
            <select
              className="w-full border border-gray-300 rounded-md p-2 bg-white"
              value={bookingTime}
              onChange={(e) => setBookingTime(e.target.value)}
              required
              disabled={!bookingDate}
            >
              <option value="">Select a time</option>
              {bookingTime &&
                !availableSlots.some((slot) => slot.time === bookingTime) && (
                  <option value={bookingTime}>{bookingTime}</option>
                )}
              {availableSlots.map((slot) => (
                <option key={slot.time} value={slot.time}>
                  {slot.time} |{" "}
                  {slot.available_barbers.map((b) => b.name).join(", ")}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white font-medium py-2 px-4 rounded-md hover:bg-blue-700 transition disabled:opacity-50"
        >
          {loading ? "Saving..." : "Confirm Details & Pay"}
        </button>
      </div>
    </form>
  );
};
