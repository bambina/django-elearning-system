from django.test import TestCase, override_settings
from userportal.tests.mixins import TermTestMixin
from userportal.tests.model_factories import *
from userportal.repositories import *
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil

TEST_MEDIA_ROOT = settings.BASE_DIR / "test_media"


class AcademicTermRepositoryTest(TestCase, TermTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.current_term = AcademicTermFactory.create()
        cls.next_term = cls.create_next_term(cls.current_term)
        cls.previous_term = cls.create_previous_term(cls.current_term)

    def test_return_correct_terms(self):
        self.assertEqual(AcademicTermRepository.current(), self.current_term)
        self.assertEqual(AcademicTermRepository.next(), self.next_term)
        self.assertEqual(AcademicTermRepository.previous(), self.previous_term)


class CourseOfferingRepositoryTest(TestCase, TermTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.current_term = AcademicTermFactory.create()
        cls.next_term = cls.create_next_term(cls.current_term)
        cls.previous_term = cls.create_previous_term(cls.current_term)
        cls.course = CourseFactory.create()
        cls.current_offering = CourseOfferingFactory.create(
            course=cls.course, term=cls.current_term
        )
        cls.next_offering = CourseOfferingFactory.create(
            course=cls.course, term=cls.next_term
        )
        cls.previous_offering = CourseOfferingFactory.create(
            course=cls.course, term=cls.previous_term
        )

    def test_fetch_correct_offerings(self):
        self.assertEqual(
            CourseOfferingRepository.fetch_current(self.course), self.current_offering
        )
        self.assertEqual(
            CourseOfferingRepository.fetch_next(self.course), self.next_offering
        )

    def test_fetch_with_academic_terms(self):
        offerings = CourseOfferingRepository.fetch_with_academic_terms(self.course.id)
        self.assertEqual(offerings.count(), 3)
        self.assertEqual(offerings[0], self.next_offering)
        self.assertEqual(offerings[1], self.current_offering)
        self.assertEqual(offerings[2], self.previous_offering)

    def test_create(self):
        subsequent_term = self.create_next_term(self.next_term)
        form_data = {
            "term": subsequent_term,
        }
        offering = CourseOfferingRepository.create(form_data, self.course)
        self.assertEqual(offering.course, self.course)
        self.assertEqual(offering.term, subsequent_term)


class CourseRepositoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course1 = CourseFactory.create(
            title="Introduction to Algorithms",
            description="Learn the fundamentals of algorithms...",
        )
        cls.course2 = CourseFactory.create(
            title="Data Structures Essentials",
            description="Deep dive into data structures...",
        )
        cls.course3 = CourseFactory.create(
            title="Advanced Programming Techniques",
            description="Explore advanced topics in programming...",
        )

    def test_fetch_filtered_by(self):
        keywords = "introduction"
        self.assertEqual(CourseRepository.fetch_filtered_by(keywords).count(), 1)
        self.assertEqual(CourseRepository.fetch_filtered_by().count(), 3)

    def test_create(self):
        form_data = {
            "title": "Test Course",
            "description": "Test Description",
            "program": ProgramFactory.create(),
        }
        teacher = TeacherProfileFactory.create()
        course = CourseRepository.create(form_data, teacher)
        self.assertEqual(course.title, form_data["title"])
        self.assertEqual(course.description, form_data["description"])
        self.assertEqual(course.program, form_data["program"])
        self.assertEqual(course.teacher, teacher)


class EnrollmentRepositoryTest(TestCase, TermTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.current_term = AcademicTermFactory.create()
        cls.next_term = cls.create_next_term(cls.current_term)
        cls.previous_term = cls.create_previous_term(cls.current_term)
        cls.course = CourseFactory.create(title="Course 1")
        cls.next_offering = CourseOfferingFactory.create(
            course=cls.course, term=cls.next_term
        )
        cls.current_offering = CourseOfferingFactory.create(
            course=cls.course, term=cls.current_term
        )
        cls.previous_offering = CourseOfferingFactory.create(
            course=cls.course, term=cls.previous_term
        )
        cls.student = StudentProfileFactory.create()
        cls.next_enrollment = EnrollmentFactory.create(
            student=cls.student, offering=cls.next_offering
        )
        cls.previous_enrollment = EnrollmentFactory.create(
            student=cls.student,
            offering=cls.previous_offering,
            grade=Enrollment.Grade.PASS,
        )

    def test_fetch(self):
        upcoming, current, past = EnrollmentRepository.fetch(self.student)
        self.assertEqual(upcoming, [self.next_enrollment])
        self.assertEqual(current, [])
        self.assertEqual(past, [self.previous_enrollment])

    def test_is_enrolled(self):
        self.assertTrue(
            EnrollmentRepository.is_enrolled(self.student, self.next_offering)
        )
        self.assertFalse(
            EnrollmentRepository.is_enrolled(self.student, self.current_offering)
        )

    def test_fetch_with_student(self):
        student2 = StudentProfileFactory.create()
        enrollment2 = EnrollmentFactory.create(
            student=student2, offering=self.next_offering
        )
        enrollments = EnrollmentRepository.fetch_with_student(self.next_offering.id)
        self.assertEqual(enrollments.count(), 2)
        self.assertEqual(enrollments[0], enrollment2)

    def test_fetch_latest_grades_subquery(self):
        # Create student's feedback
        FeedbackFactory.create(student=self.student, course=self.course)

        # Test case 1: Student with a previous grade
        results = FeedbackRepository.fetch_with_student_grade(self.course.id)
        self.assertEqual(results[0].grade, Enrollment.Grade.PASS)

        # Test case 2: Student with multiple previous grades
        antecedent_term = self.create_previous_term(self.previous_term)
        antecedent_offering = CourseOfferingFactory.create(
            course=self.course, term=antecedent_term
        )
        EnrollmentFactory.create(
            student=self.student,
            offering=antecedent_offering,
            grade=Enrollment.Grade.FAIL,
        )
        results = FeedbackRepository.fetch_with_student_grade(self.course.id)
        self.assertEqual(results[0].grade, Enrollment.Grade.PASS)


class FeedbackRepositoryTest(TestCase, TermTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.course = CourseFactory.create()
        cls.student = StudentProfileFactory.create()
        cls.feedback = FeedbackFactory.create(student=cls.student, course=cls.course)
        cls.current_term = AcademicTermFactory.create()
        cls.previous_term = cls.create_previous_term(cls.current_term)
        cls.antecedent_term = cls.create_previous_term(cls.previous_term)
        cls.previous_offering = CourseOfferingFactory.create(
            course=cls.course, term=cls.previous_term
        )
        cls.antecedent_offering = CourseOfferingFactory.create(
            course=cls.course, term=cls.antecedent_term
        )
        cls.previous_enrollment = EnrollmentFactory.create(
            student=cls.student,
            offering=cls.previous_offering,
            grade=Enrollment.Grade.PASS,
        )
        cls.antecedent_enrollment = EnrollmentFactory.create(
            student=cls.student,
            offering=cls.antecedent_offering,
            grade=Enrollment.Grade.FAIL,
        )

    def test_fetch(self):
        feedback = FeedbackRepository.fetch(self.student, self.course)
        self.assertEqual(feedback, self.feedback)

    def test_create_or_update(self):
        # Test case 1: Create a new feedback
        student = StudentProfileFactory.create()
        form_data = {
            "comments": "[Create] Great course!",
        }
        feedback = FeedbackRepository.create_or_update(form_data, self.course, student)
        self.assertEqual(feedback.comments, form_data["comments"])

        # Test case 2: Update the existing feedback
        form_data = {
            "comments": "[Update] Great course!",
        }
        feedback = FeedbackRepository.create_or_update(
            form_data, self.course, student, feedback
        )
        self.assertEqual(feedback.comments, form_data["comments"])

    def test_fetch_with_student_grade(self):
        results = FeedbackRepository.fetch_with_student_grade(self.course.id)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results[0].grade, Enrollment.Grade.PASS)
        self.assertEqual(results[0].grade_display, "Pass")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class MaterialRepositoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.file_name = "rubric_file.png"
        cls.content = b"0"
        cls.files = {"file": SimpleUploadedFile(cls.file_name, cls.content)}
        cls.course = CourseFactory.create()
        cls.form_data = {
            "title": "Rubric",
            "description": "Rubric for the final project",
        }
        TEST_MEDIA_ROOT.mkdir(exist_ok=True, parents=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @override_settings(
        STORAGES={
            "default": {
                "BACKEND": "django.core.files.storage.InMemoryStorage",
            },
        }
    )
    def test_create(self):
        material = MaterialRepository.create(self.form_data, self.course, self.files)
        self.assertEqual(material.title, self.form_data["title"])
        self.assertEqual(material.description, self.form_data["description"])
        self.assertEqual(material.course, self.course)
        self.assertEqual(material.file.read(), self.content)

    @override_settings(
        STORAGES={
            "default": {
                "BACKEND": "django.core.files.storage.InMemoryStorage",
            },
        }
    )
    def test_fetch(self):
        material = MaterialRepository.create(self.form_data, self.course, self.files)
        materials = MaterialRepository.fetch(self.course)
        self.assertEqual(materials.count(), 1)
        self.assertEqual(materials[0], material)
        self.assertEqual(materials[0].file.read(), self.content)
        self.assertEqual(materials[0].original_filename, self.file_name)


class NotificationRepositoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.notification = NotificationFactory.create(user=cls.user)

    def test_fetch(self):
        notifications = NotificationRepository.fetch(self.user)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications[0], self.notification)


class QAQuestionRepositoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.qa_session = QASessionFactory.create()

    def test_create_and_save_close_comment(self):
        close_comment = QAQuestionRepository.create_and_save_close_comment(
            self.qa_session
        )
        self.assertEqual(close_comment.room_name, self.qa_session.room_name)
        self.assertEqual(close_comment.text, LIVE_QA_END_SESSION_MSG)
        self.assertEqual(close_comment.sender, "System")
        self.assertIsNotNone(close_comment.timestamp)


class QASessionRepositoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = CourseFactory.create()
        cls.room_name = "test_room"
        cls.qa_session = QASessionFactory.create(
            course=cls.course, room_name=cls.room_name
        )

    def test_fetch(self):
        qa_session = QASessionRepository.fetch(self.course)
        self.assertEqual(qa_session, self.qa_session)
        self.assertEqual(qa_session.course, self.course)
        self.assertEqual(qa_session.room_name, self.room_name)

    def test_get_or_create(self):
        course = CourseFactory.create()
        # Test case 1: Create a new Q&A session
        created, already_available, room_name_to_be_deleted = (
            QASessionRepository.get_create_or_reactivate(course)
        )
        self.assertTrue(created)
        self.assertFalse(already_available)
        self.assertIsNone(room_name_to_be_deleted)

        # Test case 2: Get the existing and active Q&A session
        created, already_available, room_name_to_be_deleted = (
            QASessionRepository.get_create_or_reactivate(course)
        )
        self.assertFalse(created)
        self.assertTrue(already_available)
        self.assertIsNone(room_name_to_be_deleted)

        # Test case 3: Update the room name if the existing session is ended
        qa_session = QASession.objects.get(course=course)
        qa_session.status = QASession.Status.ENDED
        qa_session.save()
        created, already_available, room_name_to_be_deleted = (
            QASessionRepository.get_create_or_reactivate(course)
        )
        self.assertFalse(created)
        self.assertFalse(already_available)
        self.assertIsNotNone(room_name_to_be_deleted)
