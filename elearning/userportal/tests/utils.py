from django.utils import timezone
from userportal.models import AcademicTerm


def get_current_term():
    """Generate an AcademicTerm instance representing the current academic term based on the current date."""
    today = timezone.now().date()
    current_year = today.year
    next_year = current_year + 1
    previous_year = current_year - 1

    # Fall term is from October 1 to March 31
    fall_start = timezone.datetime(previous_year, 10, 1).date()
    fall_end = timezone.datetime(current_year, 3, 31).date()
    # Spring term is from April 1 to September 30
    spring_start = timezone.datetime(current_year, 4, 1).date()
    spring_end = timezone.datetime(current_year, 9, 30).date()
    # Fall term is from October 1 to March 31
    fall_start2 = timezone.datetime(current_year, 10, 1).date()
    fall_end2 = timezone.datetime(next_year, 3, 31).date()

    if fall_start <= today <= fall_end:
        return AcademicTerm(
            semester=AcademicTerm.SemesterType.FALL,
            year=fall_start.year,
            start_datetime=fall_start,
            end_datetime=fall_end,
        )
    elif spring_start <= today <= spring_end:
        return AcademicTerm(
            semester=AcademicTerm.SemesterType.SPRING,
            year=spring_start.year,
            start_datetime=spring_start,
            end_datetime=spring_end,
        )
    else:
        return AcademicTerm(
            semester=AcademicTerm.SemesterType.FALL,
            year=fall_start2.year,
            start_datetime=fall_start2,
            end_datetime=fall_end2,
        )
