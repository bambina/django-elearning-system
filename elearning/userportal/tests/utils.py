from django.utils import timezone
from userportal.utils import create_aware_datetime


def get_current_term_datetimes():
    """Generate an AcademicTerm instance representing the current academic term based on the current date."""
    fall, spring = 1, 2
    today = timezone.now()
    current_year = today.year
    next_year = current_year + 1
    previous_year = current_year - 1

    # Fall term is from October 1 to March 31
    fall_start = create_aware_datetime(previous_year, 10, 1)
    fall_end = create_aware_datetime(current_year, 3, 31)
    # Spring term is from April 1 to September 30
    spring_start = create_aware_datetime(current_year, 4, 1)
    spring_end = create_aware_datetime(current_year, 9, 30)
    # Fall term is from October 1 to March 31
    fall_start2 = create_aware_datetime(current_year, 10, 1)
    fall_end2 = create_aware_datetime(next_year, 3, 31)

    if fall_start <= today <= fall_end:
        return fall, fall_start.year, fall_start, fall_end
    elif spring_start <= today <= spring_end:
        return spring, spring_start.year, spring_start, spring_end
    else:
        return fall, fall_start2.year, fall_start2, fall_end2


def get_registration_date():
    """Generate a registration date based on the current term."""
    end_date_index = 3
    return get_current_term_datetimes()[end_date_index] + timezone.timedelta(days=1)
