from datetime import datetime, timedelta, time


def generate_slots(start_hr=9, end_hr=18, interval_min=30):
    """Generate all valid booking time slots between start_hr and end_hr."""
    slots = []
    current = datetime.combine(datetime.today(), time(start_hr, 0))
    end = datetime.combine(datetime.today(), time(end_hr, 0))

    while current < end:
        slots.append(current.time())
        current += timedelta(minutes=interval_min)

    return slots
