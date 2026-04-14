from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, ForeignKey, Numeric, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from .base import Base

class BookingStatus(str, Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"

class Barber(Base):
    __tablename__ = "barbers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    career_start_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationship
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="barber")

    def __repr__(self) -> str:
        return f"<Barber(name={self.name})>"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    booking_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    barber_id: Mapped[int] = mapped_column(ForeignKey("barbers.id"), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        SqlEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False
    )

    # Relationship
    barber: Mapped["Barber"] = relationship("Barber", back_populates="bookings")

    def __repr__(self) -> str:
        return f"<Booking(customer={self.customer_name}, status={self.status})>"
