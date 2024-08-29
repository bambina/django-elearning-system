from django.utils.timezone import now
from userportal.models import AcademicTerm


class AcademicTermRepository:
    @staticmethod
    def current():
        return AcademicTerm.objects.filter(
            start_datetime__lte=now(), end_datetime__gte=now()
        ).first()

    @staticmethod
    def next():
        return (
            AcademicTerm.objects.filter(start_datetime__gt=now())
            .order_by("start_datetime")
            .first()
        )

    @staticmethod
    def previous():
        return (
            AcademicTerm.objects.filter(end_datetime__lt=now())
            .order_by("-end_datetime")
            .first()
        )
