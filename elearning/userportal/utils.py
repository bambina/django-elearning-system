import os
from uuid import uuid4
from django.utils import timezone
import datetime


def path_and_rename(instance, filename):
    """Rename the file with a unique name"""
    upload_to = "materials/"
    base, ext = os.path.splitext(filename)
    new_filename = f"{base}_{uuid4().hex}{ext}"
    return os.path.join(upload_to, new_filename)


def create_timezone_aware_datetime(year, month, day, hour=0, minute=0, second=0):
    """Create a timezone-aware datetime object from year, month, and day."""
    # Create a naive datetime
    naive_datetime = datetime.datetime(year, month, day, hour, minute, second)
    # Make it timezone-aware using the default timezone
    return timezone.make_aware(naive_datetime)
