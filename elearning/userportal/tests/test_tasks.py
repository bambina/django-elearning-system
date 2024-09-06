from unittest.mock import patch

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from userportal.tasks import *
from userportal.tests.model_factories import *


class SharedTaskTest(TestCase):
    """Tests for Celery's shared tasks."""

    @patch("userportal.tasks.delete_qa_questions.apply_async")
    def test_delete_qa_questions(self, mock_apply_async):
        # Prepare test data
        room_name_1, room_name_2 = "room1", "room2"
        qa_question1 = QAQuestionFactory.create(room_name=room_name_1)
        qa_question2 = QAQuestionFactory.create(room_name=room_name_2)

        # Mock the apply_async method to call the actual function
        mock_apply_async.side_effect = lambda args, **kwargs: delete_qa_questions(*args)
        # Call the function
        delete_qa_questions.apply_async(args=[room_name_1])

        # Check if the question was deleted
        with self.assertRaises(ObjectDoesNotExist):
            qa_question1.refresh_from_db()
        self.assertFalse(QAQuestion.objects.filter(room_name=room_name_1).exists())
        # Check if the other question was not deleted
        qa_question2.refresh_from_db()
        self.assertTrue(QAQuestion.objects.filter(room_name=room_name_2).exists())

    @patch("userportal.tasks.mark_notifications_as_read.apply_async")
    def test_mark_notifications_as_read(self, mock_apply_async):
        # Prepare test data
        notifications = NotificationFactory.create_batch(2, is_read=False)
        notification_ids = [n.id for n in notifications]

        # Mock the apply_async method to call the actual function
        mock_apply_async.side_effect = (
            lambda args, **kwargs: mark_notifications_as_read(*args)
        )
        # Call the function
        mark_notifications_as_read.apply_async(args=[notification_ids])

        # Check if the notification was marked as read
        for n in notifications:
            n.refresh_from_db()
            self.assertTrue(n.is_read)
