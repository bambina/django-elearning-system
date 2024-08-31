from typing import Union
from django.shortcuts import get_object_or_404
from userportal.models import *


class QASessionRepository:
    """Repository for Q&A session related operations."""

    @staticmethod
    def get(course: Course) -> Union[QASession, None]:
        """Retrieve a Q&A session for the specified course."""
        return QASession.objects.filter(course=course).first()

    @staticmethod
    def update_room_name(qa_session: QASession) -> QASession:
        """Create a new Q&A session for the specified course."""
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
        qa_session.room_name = f"{qa_session.course.id}_{timestamp}"
        qa_session.status = QASession.Status.ACTIVE
        qa_session.save()
        return qa_session

    @staticmethod
    def end(course: Course) -> QASession:
        """End the Q&A session for the specified course."""
        qa_session = get_object_or_404(QASession, course=course)
        qa_session.status = QASession.Status.ENDED
        qa_session.save()
        return qa_session
