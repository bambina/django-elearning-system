from dateutil.relativedelta import relativedelta
from userportal.models import AcademicTerm
from userportal.tests.model_factories import AcademicTermFactory
from userportal.tests.utils import get_term_datetimes
from datetime import datetime


class TermTestMixin:
    """Mixin for creating academic terms."""

    @classmethod
    def create_academic_term(
        self, semester_val: int, year: int, start_date: datetime, end_date: datetime
    ) -> AcademicTerm:
        """Create a new academic term."""
        return AcademicTermFactory.create(
            semester=AcademicTerm.SemesterType(semester_val),
            year=year,
            start_datetime=start_date,
            end_datetime=end_date,
        )

    @classmethod
    def create_next_term(self, current_term: AcademicTerm) -> AcademicTerm:
        """Create the next academic term based on the end datetime of the given term."""
        next_term_properties = get_term_datetimes(
            current_term.end_datetime + relativedelta(days=1)
        )
        return self.create_academic_term(*next_term_properties)

    @classmethod
    def create_previous_term(self, current_term: AcademicTerm) -> AcademicTerm:
        """Create the previous academic term based on the start datetime of the given term."""
        prev_term_properties = get_term_datetimes(
            current_term.start_datetime - relativedelta(days=1)
        )
        return self.create_academic_term(*prev_term_properties)
