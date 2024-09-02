from django.test import TestCase
from userportal.tests.mixins import TermTestMixin
from userportal.tests.model_factories import *
from userportal.repositories import *


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
