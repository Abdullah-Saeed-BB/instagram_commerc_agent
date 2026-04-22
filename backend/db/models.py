from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, ForeignKey, Numeric, func, Enum as SqlEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum
import uuid

class Base(DeclarativeBase):
    """Shared declarative base — import this in every model file."""
    pass

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class Services(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(355), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

class Barber(Base):
    __tablename__ = "barbers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    career_start_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationship
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="barber")

    def __repr__(self) -> str:
        return f"<Barber(name={self.name})>"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    payment_id: Mapped[str] = mapped_column(String(35), nullable=False) 
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    booking_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    barber_id: Mapped[int] = mapped_column(ForeignKey("barbers.id"), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SqlEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value,  # ✅ important
        nullable=False
    )

    # Relationship
    barber: Mapped["Barber"] = relationship("Barber", back_populates="bookings")
    service: Mapped["Services"] = relationship("Services", back_populates="bookings")

    def __repr__(self) -> str:
        return f"<Booking(customer={self.customer_name}, status={self.status})>"
