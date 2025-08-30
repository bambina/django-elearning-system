from typing import Tuple, Optional
from django.shortcuts import get_object_or_404
from userportal.models import *
from userportal.utils import *


class QASessionRepository:
    """Repository for Q&A session related operations."""

    @staticmethod
    def fetch(course: Course) -> Optional[QASession]:
        """Retrieve a Q&A session for the specified course."""
        return QASession.objects.filter(course=course).first()

    @staticmethod
    def get_create_or_reactivate(course: Course) -> Tuple[bool, bool, Optional[str]]:
        """
        Fetch or create a new Q&A session for the specified course.
        Update the room name if the session is already ended.

        Returns:
            - created: True if a new session is created, False otherwise.
            - already_available: True if there is an active session, False otherwise.
            - room_name_to_be_deleted: The old room name whose associated questions should be deleted, or None.
            This is used when reactivating an inactive session with a new room name.
        """
        qa_session, created = QASession.objects.get_or_create(course=course)
        already_available = not created and qa_session.is_active()
        room_name_to_be_deleted = None
        if created or already_available:
            return created, already_available, room_name_to_be_deleted
        # Reactivate an inactive session with a new room name
        room_name_to_be_deleted = qa_session.room_name
        qa_session.room_name = generate_unique_room_name(qa_session.course.id)
        qa_session.status = QASession.Status.ACTIVE
        qa_session.save()
        return created, already_available, room_name_to_be_deleted

    @staticmethod
    def end(course: Course) -> QASession:
        """End the Q&A session for the specified course."""
        qa_session = get_object_or_404(QASession, course=course)
        qa_session.status = QASession.Status.ENDED
        qa_session.save()
        return qa_session
