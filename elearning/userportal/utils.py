import os
from uuid import uuid4
from django.utils import timezone
from datetime import datetime


def path_and_rename(instance, filename):
    """Rename the file with a unique name"""
    upload_to = "materials/"
    base, ext = os.path.splitext(filename)
    new_filename = f"{base}_{uuid4().hex}{ext}"
    return os.path.join(upload_to, new_filename)


def create_timezone_aware_datetime(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0
) -> datetime:
    """Create a timezone-aware datetime object from year, month, and day."""
    # Create a naive datetime
    naive_datetime = datetime(year, month, day, hour, minute, second)
    # Make it timezone-aware using the default timezone
    return timezone.make_aware(naive_datetime)


def generate_unique_room_name(course_id: int) -> str:
    """Generate a unique room name for a Q&A session."""
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
    unique_id = uuid4().hex[:8]
    return f"{course_id}_{timestamp}_{unique_id}"
