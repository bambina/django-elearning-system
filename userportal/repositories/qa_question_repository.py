from django.utils import timezone
from userportal.models import *


class QAQuestionRepository:
    """Repository for QAQuestion model."""

    @staticmethod
    def create_and_save_close_comment(qa_session: QASession) -> QAQuestion:
        """Create and save a close comment for the given QA session."""
        close_comment = QAQuestion(
            room_name=qa_session.room_name,
            text=LIVE_QA_END_SESSION_MSG,
            sender="System",
            timestamp=timezone.now(),
        )
        close_comment.save()
        return close_comment
