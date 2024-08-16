from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
import itertools
import random
from userportal.models import *


class Command(BaseCommand):
    help = "Populate database with initial data"
    COMMON_PASSWORD = "abc"
    FEEDBACK_COMMENTS = [
        "I directly applied the concepts and skills I learned from my courses to an exciting new project at work.",
        "To be able to take courses at my own pace and rhythm has been an amazing experience. I can learn whenever it fits my schedule and mood.",
        "Taking this course was an important step in my career. I could readily see the practical application of some of what we studied and strengthen my theoretical understanding of algorithms and frameworks used at work. Interacting with professors and course mates was inspiring and generated new intuitions and ideas."
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._total_records = 0
        self.program = None
        self.created_teachers = []
        self.student_1 = None
        self.student_2 = None
        self.student_3 = None
        self.created_courses = []

    def handle(self, *args, **kwargs):
        self.cleanup_database()
        self.create_superuser()
        self.create_program()
        self.create_users()
        self.create_teacher_profiles()
        self.create_student_profiles()
        self.create_academic_terms()
        self.create_courses()
        self.create_course_offerings()
        self.create_enrollments()
        self.create_feedback()
        print(f"Total records created: {self._total_records}")

    def update_record_count(self, count):
        """Update the total records count"""
        self._total_records += count

    def cleanup_database(self):
        """Cleanup the database"""
        Program.objects.all().delete()
        PortalUser.objects.all().delete()
        AcademicTerm.objects.all().delete()
        Course.objects.all().delete()

    def create_superuser(self):
        """Create a superuser 'admin'"""
        PortalUser.objects.create_superuser(
            username="admin", password=self.COMMON_PASSWORD, email="admin@example.com"
        )
        self.update_record_count(1)

    def create_program(self):
        """Create a program"""
        programs = [
            Program(
                title="Bachelor of Science in Computer Science",
                description="This 360-credit degree programme from the University of London blends strong foundational computing skills with emerging technology specialisms and case study material to help you apply your new skills to real-world contexts.",
            ),
        ]
        programs = Program.objects.bulk_create(programs)
        self.program = programs[0]
        self.update_record_count(len(programs))

    def create_users(self):
        """Create users"""
        users = [
            PortalUser(
                username="teacher1",
                first_name="John",
                last_name="Smith",
                email="t1@example.com",
                title=PortalUser.Title.PROF,
                user_type=PortalUser.UserType.TEACHER,
            ),
            PortalUser(
                username="teacher2",
                first_name="Emily",
                last_name="Johnson",
                email="t2@example.com",
                title=PortalUser.Title.DR,
                user_type=PortalUser.UserType.TEACHER,
            ),
            PortalUser(
                username="student1",
                first_name="Michael",
                last_name="Brown",
                email="s1@example.com",
                title=PortalUser.Title.PREFER_NOT_TO_SAY,
                user_type=PortalUser.UserType.STUDENT,
            ),
            PortalUser(
                username="student2",
                first_name="Sarah",
                last_name="Davis",
                email="s2@example.com",
                title=PortalUser.Title.MS,
                user_type=PortalUser.UserType.STUDENT,
            ),
            PortalUser(
                username="student3",
                first_name="Anna",
                last_name="Johnson",
                email="s3@example.com",
                title=PortalUser.Title.MRS,
                user_type=PortalUser.UserType.STUDENT,
            ),
        ]
        created_users = PortalUser.objects.bulk_create(users)

        for user in created_users:
            user.set_password(self.COMMON_PASSWORD)
            user.save()

        self.update_record_count(len(users))

    def create_teacher_profiles(self):
        """Create teacher profiles"""
        teacher_profiles = [
            TeacherProfile(
                user=PortalUser.objects.get(username="teacher1"),
                biography="Prof. John Smith is a Professor of Computer Science at the University of California. He obtained his Ph.D. in Computer Science and Engineering from the Visual Computing Lab at the University of California, Berkeley in 1995. With over two decades of experience, he has dedicated his career to advancing the fields of artificial intelligence and machine learning.",
            ),
            TeacherProfile(
                user=PortalUser.objects.get(username="teacher2"),
                biography="Dr. Emily Johnson is an Associate Professor of Mechanical Engineering at the Massachusetts Institute of Technology. She earned her Ph.D. in Mechanical Engineering with a focus on biomechanics from Stanford University in 2010. Dr. Johnson specializes in the development of robotic systems for healthcare applications, blending her expertise in engineering with medical technology.",
            ),
        ]
        self.created_teachers = TeacherProfile.objects.bulk_create(teacher_profiles)
        self.update_record_count(len(teacher_profiles))

    def create_student_profiles(self):
        """Create student profiles"""
        student_profiles = [
            StudentProfile(
                user=PortalUser.objects.get(username="student1"),
                program=self.program,
                registration_date="2021-01-01",
                registration_expiry_date="2027-01-01",
            ),
            StudentProfile(
                user=PortalUser.objects.get(username="student2"),
                program=self.program,
                registration_date="2024-01-01",
                registration_expiry_date="2030-01-01",
            ),
            StudentProfile(
                user=PortalUser.objects.get(username="student3"),
                program=self.program,
                registration_date="2022-01-01",
                registration_expiry_date="2028-01-01",
            ),
        ]

        self.student_1, self.student_2, self.student_3 = (
            StudentProfile.objects.bulk_create(student_profiles)
        )
        self.update_record_count(len(student_profiles))

    def create_academic_terms(self):
        academic_terms = [
            AcademicTerm(
                semester=AcademicTerm.SemesterType.FALL,
                year=2023,
                start_datetime=timezone.make_aware(datetime(2023, 10, 1, 0, 0)),
                end_datetime=timezone.make_aware(datetime(2024, 3, 31, 23, 59)),
            ),
            AcademicTerm(
                semester=AcademicTerm.SemesterType.SPRING,
                year=2024,
                start_datetime=timezone.make_aware(datetime(2024, 4, 1, 0, 0)),
                end_datetime=timezone.make_aware(datetime(2024, 9, 30, 23, 59)),
            ),
            AcademicTerm(
                semester=AcademicTerm.SemesterType.FALL,
                year=2024,
                start_datetime=timezone.make_aware(datetime(2024, 10, 1, 0, 0)),
                end_datetime=timezone.make_aware(datetime(2025, 3, 31, 23, 59)),
            ),
            AcademicTerm(
                semester=AcademicTerm.SemesterType.SPRING,
                year=2025,
                start_datetime=timezone.make_aware(datetime(2025, 4, 1, 0, 0)),
                end_datetime=timezone.make_aware(datetime(2025, 9, 30, 23, 59)),
            ),
        ]
        AcademicTerm.objects.bulk_create(academic_terms)
        self.update_record_count(len(academic_terms))

    def create_courses(self):
        courses = [
            Course(
                title="Introduction to Computer Science",
                description="An introductory course covering the essentials of computer science, from basic programming to algorithm understanding.",
                program=self.program,
                teacher=self.created_teachers[0],
            ),
            Course(
                title="Data Structures and Algorithms",
                description="Study key data structures and algorithms to enhance problem-solving and software development skills.",
                program=self.program,
                teacher=self.created_teachers[0],
            ),
            Course(
                title="Database Management Systems",
                description="Learn the fundamentals of database design, SQL, and managing relational database systems.",
                program=self.program,
                teacher=self.created_teachers[0],
            ),
            Course(
                title="Software Engineering",
                description="Gain insights into software development processes, from design to testing and maintenance.",
                program=self.program,
                teacher=self.created_teachers[0],
            ),
        ]

        self.created_courses = Course.objects.bulk_create(courses)
        self.update_record_count(len(courses))

    def create_course_offerings(self):
        offerings = []
        for course, term in itertools.product(
            self.created_courses[:3], AcademicTerm.objects.all()
        ):
            offerings.append(CourseOffering(course=course, term=term))

        self.created_offerings = CourseOffering.objects.bulk_create(offerings)
        self.update_record_count(len(offerings))

    def create_enrollments(self):
        next_term = AcademicTerm.next()
        current_term = AcademicTerm.current()
        previous_term = AcademicTerm.previous()
        course_1 = self.created_courses[0]
        course_2 = self.created_courses[1]
        enrollments = [
            Enrollment(
                student=self.student_1,
                offering=CourseOffering.objects.get(course=course_1, term=next_term),
            ),
            Enrollment(
                student=self.student_1,
                offering=CourseOffering.objects.get(course=course_2, term=next_term),
            ),
            Enrollment(
                student=self.student_1,
                offering=CourseOffering.objects.get(course=course_1, term=current_term),
            ),
            Enrollment(
                student=self.student_1,
                offering=CourseOffering.objects.get(course=course_2, term=current_term),
            ),
            Enrollment(
                student=self.student_1,
                offering=CourseOffering.objects.get(
                    course=course_1, term=previous_term
                ),
                grade=random.choice([Enrollment.Grade.PASS, Enrollment.Grade.FAIL]),
            ),
            Enrollment(
                student=self.student_2,
                offering=CourseOffering.objects.get(
                    course=course_1, term=previous_term
                ),
                grade=random.choice([Enrollment.Grade.PASS, Enrollment.Grade.FAIL]),
            ),
            Enrollment(
                student=self.student_3,
                offering=CourseOffering.objects.get(
                    course=course_1, term=previous_term
                ),
                grade=random.choice([Enrollment.Grade.PASS, Enrollment.Grade.FAIL]),
            ),
        ]

        Enrollment.objects.bulk_create(enrollments)
        self.update_record_count(len(enrollments))

    def create_feedback(self):
        feedbacks = []
        ended_enrollments = Enrollment.objects.filter(
            offering__term__end_datetime__lt=timezone.now()
        ).select_related('student', 'offering__course')

        for i, enrollment in enumerate(ended_enrollments):
            comment_no = i % len(self.FEEDBACK_COMMENTS)
            feedbacks.append(
                Feedback(
                    student=enrollment.student,
                    course=enrollment.offering.course,
                    comments=self.FEEDBACK_COMMENTS[comment_no],
                )
            )

        Feedback.objects.bulk_create(feedbacks)
        self.update_record_count(len(feedbacks))
