import { useState, useEffect } from "react";
import { PaymentStatus } from "./types";

export function BookingDetails({
  id,
  service,
  price,
  bookingDatetime,
  customerName,
  barber,
  paymentStatus,
  onSaveSuccess,
}: {
  id: string;
  service: string | null;
  price: string | null;
  bookingDatetime: string | null;
  customerName: string | null;
  paymentStatus: PaymentStatus | null;
  barber: string | null;
  onSaveSuccess?: () => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    customer_name: customerName || "",
    booking_datetime: bookingDatetime
      ? new Date(bookingDatetime).toISOString().slice(0, 16)
      : "",
    service: service || "",
    barber: barber || "",
  });

  const [services, setServices] = useState<{ id: string; name: string }[]>([]);
  const [barbers, setBarbers] = useState<{ id: string; name: string }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isEditing) {
      fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/booking/data/services`)
        .then((res) => res.json())
        .then((data) => setServices(data))
        .catch(console.error);

      fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/booking/data/barbers`)
        .then((res) => res.json())
        .then((data) => setBarbers(data))
        .catch(console.error);
    }
  }, [isEditing]);

  const handleSave = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/booking/${id}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            customer_name: editData.customer_name || null,
            booking_datetime: editData.booking_datetime
              ? new Date(editData.booking_datetime).toISOString()
              : null,
            service: editData.service || null,
            barber: editData.barber || null,
          }),
        },
      );

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Failed to update");
      }

      setIsEditing(false);
      if (onSaveSuccess) onSaveSuccess();
    } catch (e: any) {
      console.error(e);
      alert(`Error: ${e.message || "Failed to save booking details"}`);
    } finally {
      setLoading(false);
    }
  };

  const formattedDate = bookingDatetime
    ? new Date(bookingDatetime).toLocaleString("en-CH", {
        year: "numeric",
        month: "short",
        day: "numeric",
        weekday: "short",
        hour: "numeric",
        minute: "2-digit",
      })
    : null;

  return (
    <div className="w-full bg-white p-6 sm:p-8 rounded-2xl shadow-sm border border-gray-100 h-fit transition-all hover:shadow-md relative">
      <h2 className="text-[#087BA3] font-bold text-xl mb-6 flex items-center gap-3">
        <span className="p-2 bg-[#F5F7F7] rounded-lg">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-[#087BA3]"
          >
            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </span>
        Booking Details
      </h2>

      {paymentStatus !== "SUCCESSFUL" && !isEditing && (
        <button
          onClick={() => setIsEditing(true)}
          className="absolute top-6 right-6 text-sm text-[#087BA3] font-medium hover:underline px-3 py-1 bg-[#F5F7F7] rounded-md transition-colors hover:bg-[#E8F0F3]"
        >
          Edit
        </button>
      )}

      {isEditing ? (
        <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
          <div>
            <label className="block text-[#51A1BD] text-xs font-bold uppercase tracking-wider mb-1.5">
              Customer Name
            </label>
            <input
              type="text"
              value={editData.customer_name}
              onChange={(e) =>
                setEditData({ ...editData, customer_name: e.target.value })
              }
              className="w-full bg-[#f0f4f7] border border-[#d1dce2] focus:border-[#087BA3] focus:ring-2 focus:ring-[#087BA3]/20 outline-none rounded-xl p-3.5 text-sm text-[#333] placeholder:text-gray-400 transition-all shadow-inner"
              placeholder="Enter your name"
            />
          </div>
          <div>
            <label className="block text-[#51A1BD] text-xs font-bold uppercase tracking-wider mb-1.5">
              Service
            </label>
            <select
              value={editData.service}
              onChange={(e) =>
                setEditData({ ...editData, service: e.target.value })
              }
              className="w-full bg-[#f0f4f7] border border-[#d1dce2] focus:border-[#087BA3] focus:ring-2 focus:ring-[#087BA3]/20 outline-none rounded-xl p-3.5 text-sm text-[#333] transition-all shadow-inner appearance-none cursor-pointer"
            >
              <option value="">Select a service</option>
              {services.map((s) => (
                <option key={s.id} value={s.name}>
                  {s.name.replaceAll("_", " ")}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[#51A1BD] text-xs font-bold uppercase tracking-wider mb-1.5">
              Barber
            </label>
            <select
              value={editData.barber}
              onChange={(e) =>
                setEditData({ ...editData, barber: e.target.value })
              }
              className="w-full bg-[#f0f4f7] border border-[#d1dce2] focus:border-[#087BA3] focus:ring-2 focus:ring-[#087BA3]/20 outline-none rounded-xl p-3.5 text-sm text-[#333] transition-all shadow-inner appearance-none cursor-pointer"
            >
              <option value="">Select a barber</option>
              {barbers.map((b) => (
                <option key={b.id} value={b.name}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[#51A1BD] text-xs font-bold uppercase tracking-wider mb-1.5">
              Date & Time
            </label>
            <input
              type="datetime-local"
              value={editData.booking_datetime}
              onChange={(e) =>
                setEditData({ ...editData, booking_datetime: e.target.value })
              }
              className="w-full bg-[#f0f4f7] border border-[#d1dce2] focus:border-[#087BA3] focus:ring-2 focus:ring-[#087BA3]/20 outline-none rounded-xl p-3.5 text-sm text-[#333] transition-all shadow-inner"
            />
          </div>
          <div className="flex gap-3 pt-4">
            <button
              onClick={handleSave}
              disabled={loading}
              className="flex-1 bg-[#087BA3] hover:bg-[#066a8d] text-white py-3 rounded-xl text-sm font-bold shadow-sm transition-all active:scale-[0.98] disabled:opacity-50"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg
                    className="animate-spin h-4 w-4 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Saving...
                </span>
              ) : (
                "Save Changes"
              )}
            </button>
            <button
              onClick={() => setIsEditing(false)}
              disabled={loading}
              className="flex-1 bg-white border border-[#E1E8EB] text-[#51A1BD] hover:bg-gray-50 py-3 rounded-xl text-sm font-bold transition-all disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          <div className="flex justify-between items-center py-1">
            <span className="text-[#51A1BD] text-sm font-medium">Customer</span>
            <span className="text-[#4F5759] font-semibold ">
              {customerName || (
                <span className="text-red-400 italic font-normal">Missing</span>
              )}
            </span>
          </div>

          <div className="flex justify-between items-center py-1">
            <span className="text-[#51A1BD] text-sm font-medium">Barber</span>
            <span className="text-[#4F5759] font-semibold ">
              {barber || (
                <span className="text-red-400 italic font-normal">Missing</span>
              )}
            </span>
          </div>

          <div className="flex justify-between items-start py-1">
            <span className="text-[#51A1BD] text-sm font-medium">Service</span>
            <span className="text-[#4F5759] font-semibold bg-[#F5F7F7] capitalize italic text-right max-w-[150px]">
              {service ? (
                service.replaceAll("_", " ")
              ) : (
                <span className="text-red-400 italic font-normal not-italic bg-transparent">
                  Missing
                </span>
              )}
            </span>
          </div>

          {paymentStatus && (
            <div className="flex justify-between items-start py-1">
              <span className="text-[#51A1BD] text-sm font-medium">Status</span>
              <span
                className={`${
                  paymentStatus === "SUCCESSFUL"
                    ? "bg-green-100 text-green-800"
                    : paymentStatus === "CANCELED"
                      ? "bg-red-100 text-red-800"
                      : "bg-yellow-100 text-yellow-800"
                } font-semibold px-3 py-1 rounded-full capitalize text-sm text-right max-w-[150px]`}
              >
                {paymentStatus.toLowerCase()}
              </span>
            </div>
          )}

          <div className="flex justify-between items-center py-1">
            <span className="text-[#51A1BD] text-sm font-medium">
              Date & Time
            </span>
            <span className="text-[#4F5759] font-semibold text-sm">
              {formattedDate || (
                <span className="text-red-400 italic font-normal">Missing</span>
              )}
            </span>
          </div>

          <div className="pt-6 mt-2 border-t border-dashed border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-[#087BA3] font-bold">Total Amount</span>
              <span className="text-3xl font-bold text-[#087BA3]">
                ${price || "0.00"}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
