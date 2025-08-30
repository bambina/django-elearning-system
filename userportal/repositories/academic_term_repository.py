from typing import Union

from django.utils.timezone import now

from userportal.models import AcademicTerm


class AcademicTermRepository:
    """Repository for AcademicTerm model"""

    @staticmethod
    def current() -> Union[AcademicTerm, None]:
        """Get the current academic term."""
        return AcademicTerm.objects.filter(
            start_datetime__lte=now(), end_datetime__gte=now()
        ).first()

    @staticmethod
    def next() -> Union[AcademicTerm, None]:
        """Get the next academic term."""
        return (
            AcademicTerm.objects.filter(start_datetime__gt=now())
            .order_by("start_datetime")
            .first()
        )

    @staticmethod
    def previous() -> Union[AcademicTerm, None]:
        """Get the previous academic term."""
        return (
            AcademicTerm.objects.filter(end_datetime__lt=now())
            .order_by("-end_datetime")
            .first()
        )
