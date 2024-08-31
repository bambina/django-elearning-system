from typing import Union
from userportal.models import *


class QASessionRepository:
    """Repository for Q&A session related operations."""

    @staticmethod
    def get_active_session(course: Course) -> Union[QASession, None]:
        """Retrieve the most recent active Q&A session for the specified course."""
        return QASession.objects.filter(
            course=course, status=QASession.Status.ACTIVE
        ).first()

    @staticmethod
    def get_ended_session(course: Course) -> Union[QASession, None]:
        """Retrieve the most recent ended Q&A session for the specified course."""
        return QASession.objects.filter(
            course=course, status=QASession.Status.ENDED
        ).first()

    @staticmethod
    def get_last_session(course: Course) -> Union[QASession, None]:
        """Retrieve the most recent Q&A session for the specified course."""
        return QASession.objects.filter(course=course).first()

    @staticmethod
    def create(course: Course) -> QASession:
        """Create a new Q&A session for the specified course."""
        qa_session = QASession.objects.get_or_create(course=course)
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
        qa_session.room_name = f"{course.id}_{timestamp}"
        qa_session.save()
        return qa_session
