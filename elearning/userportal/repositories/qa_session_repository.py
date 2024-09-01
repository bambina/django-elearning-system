from typing import Union, Tuple
from django.shortcuts import get_object_or_404
from userportal.models import *


class QASessionRepository:
    """Repository for Q&A session related operations."""

    @staticmethod
    def fetch(course: Course) -> Union[QASession, None]:
        """Retrieve a Q&A session for the specified course."""
        return QASession.objects.filter(course=course).first()

    @staticmethod
    def get_or_create(course: Course) -> Tuple[bool, Union[str, None]]:
        """
        Fetch or create a new Q&A session for the specified course.
        Update the room name if the session is already ended.
        Return a boolean indicating if the active session already exists and the previous room name.
        """
        qa_session, created = QASession.objects.get_or_create(course=course)
        if not created and qa_session.is_active():
            return True, None
        previous_room_name = qa_session.room_name
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
        qa_session.room_name = f"{qa_session.course.id}_{timestamp}"
        qa_session.status = QASession.Status.ACTIVE
        qa_session.save()
        return False, previous_room_name

    @staticmethod
    def end(course: Course) -> QASession:
        """End the Q&A session for the specified course."""
        qa_session = get_object_or_404(QASession, course=course)
        qa_session.status = QASession.Status.ENDED
        qa_session.save()
        return qa_session
