export type PaymentStatus = "PENDING" | "SUCCESSFUL" | "FAILED" | "CANCELED";

export interface BookingData {
  id: string;
  service: string;
  amount: number;
  booking_datetime: string;
  customer_name: string;
  client_secret: string;
  payment_status: PaymentStatus;
  barber: {
    name: string;
  };
}
