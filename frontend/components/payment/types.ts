export interface BookingData {
  id: string;
  service: string | null;
  amount: number | null;
  booking_datetime: string | null;
  customer_name: string | null;
  client_secret: string | null;
  payment_status: "PENDING" | "SUCCESSFUL" | "FAILED" | "CANCELED";
  barber: { name: string } | null;
}

export interface ServiceData {
  id: string;
  name: string;
  price: number;
}

export interface BarberData {
  id: string;
  name: string;
}
