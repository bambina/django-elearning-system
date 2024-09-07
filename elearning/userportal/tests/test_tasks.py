import shutil
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.core.exceptions import ObjectDoesNotExist

from userportal.tasks import *
from userportal.tests.model_factories import *


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class SharedTaskTest(TestCase):
    """Tests for Celery's shared tasks."""

    @classmethod
    def setUpTestData(cls):
        TEST_MEDIA_ROOT.mkdir(exist_ok=True, parents=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

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

    @patch("userportal.tasks.notify_students_of_live_qa_start.apply_async")
    def test_notify_students_of_live_qa_start(self, mock_apply_async):
        # Prepare test data
        current_term = AcademicTermFactory.create()
        offering = CourseOfferingFactory.create(term=current_term)
        enrollments = EnrollmentFactory.create_batch(2, offering=offering)
        course_id = enrollments[0].offering.course.id

        # Mock the apply_async method to call the actual function
        mock_apply_async.side_effect = (
            lambda args, **kwargs: notify_students_of_live_qa_start(*args)
        )
        # Call the function
        notify_students_of_live_qa_start.apply_async(args=[course_id])

        # Check if the notifications were created
        for e in enrollments:
            notification = Notification.objects.filter(user=e.student.user).first()
            self.assertIsNotNone(notification)
            self.assertIn("live Q&A session", notification.message)

    @override_settings(
        STORAGES={
            "default": {
                "BACKEND": "django.core.files.storage.InMemoryStorage",
            },
        }
    )
    @patch("userportal.tasks.notify_students_of_material_creation.apply_async")
    def test_notify_students_of_material_creation(self, mock_apply_async):
        # Prepare test data
        offering = CourseOfferingFactory.create()
        material = MaterialFactory.create(course=offering.course)
        enrollments = EnrollmentFactory.create_batch(2, offering=offering)

        # Mock the apply_async method to call the actual function
        mock_apply_async.side_effect = (
            lambda args, **kwargs: notify_students_of_material_creation(*args)
        )
        # Call the function
        notify_students_of_material_creation.apply_async(
            args=[offering.course.id, material.id]
        )

        # Check if the notifications were created
        for e in enrollments:
            notification = Notification.objects.filter(user=e.student.user).first()
            self.assertIsNotNone(notification)
            self.assertIn("new material", notification.message)

    @patch("userportal.tasks.notify_teacher_of_new_enrollment.apply_async")
    def test_notify_teacher_of_new_enrollment(self, mock_apply_async):
        # Prepare test data
        teacher = TeacherProfileFactory.create()
        offering = CourseOfferingFactory.create(course__teacher=teacher)
        enrollment = EnrollmentFactory.create(offering=offering)

        # Mock the apply_async method to call the actual function
        mock_apply_async.side_effect = (
            lambda args, **kwargs: notify_teacher_of_new_enrollment(*args)
        )
        # Call the function
        notify_teacher_of_new_enrollment.apply_async(
            args=[offering.course.id, offering.id, enrollment.student.user.username]
        )

        # Check if the notification was created
        notification = Notification.objects.filter(user=teacher.user).first()
        self.assertIsNotNone(notification)
        self.assertIn("enrolled", notification.message)

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
