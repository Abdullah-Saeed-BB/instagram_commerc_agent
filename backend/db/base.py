from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Shared declarative base — import this in every model file."""
    pass

# Import all models here so they are registered with Base.metadata
from .models import Barber, Booking
