import { PaymentStatus } from "./types";

export function BookingDetails({
  service,
  price,
  bookingDatetime,
  customerName,
  barber,
  paymentStatus,
}: {
  service: string | null;
  price: string | null;
  bookingDatetime: string | null;
  customerName: string | null;
  paymentStatus: PaymentStatus | null;
  barber: string | null;
}) {
  if (
    !service &&
    !price &&
    !bookingDatetime &&
    !customerName &&
    !barber &&
    !paymentStatus
  )
    return null;

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
    <div className="w-full bg-white p-6 sm:p-8 rounded-2xl shadow-sm border border-gray-100 h-fit transition-all hover:shadow-md">
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

      <div className="space-y-5">
        {customerName && (
          <div className="flex justify-between items-center py-1">
            <span className="text-[#51A1BD] text-sm font-medium">Customer</span>
            <span className="text-[#4F5759] font-semibold ">
              {customerName}
            </span>
          </div>
        )}

        {barber && (
          <div className="flex justify-between items-center py-1">
            <span className="text-[#51A1BD] text-sm font-medium">Barber</span>
            <span className="text-[#4F5759] font-semibold ">{barber}</span>
          </div>
        )}

        {service && (
          <div className="flex justify-between items-start py-1">
            <span className="text-[#51A1BD] text-sm font-medium">Service</span>
            <span className="text-[#4F5759] font-semibold bg-[#F5F7F7] capitalize italic text-right max-w-[150px]">
              {service.replaceAll("_", " ")}
            </span>
          </div>
        )}

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

        {formattedDate && (
          <div className="flex justify-between items-center py-1">
            <span className="text-[#51A1BD] text-sm font-medium">
              Date & Time
            </span>
            <span className="text-[#4F5759] font-semibold text-sm">
              {formattedDate}
            </span>
          </div>
        )}

        <div className="pt-6 mt-2 border-t border-dashed border-gray-200">
          <div className="flex justify-between items-center">
            <span className="text-[#087BA3] font-bold">Total Amount</span>
            <span className="text-3xl font-bold text-[#087BA3]">
              ${price || "0.00"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
