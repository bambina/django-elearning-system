import os, sys
import django
import itertools
from django.utils import timezone
from datetime import datetime

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory
project_root = os.path.abspath(os.path.join(script_dir, ".."))
# Add the project root directory to the system path
sys.path.append(project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elearning.settings")
django.setup()

from userportal.models import *

total_records = 0

# Clean up the database
Program.objects.all().delete()
PortalUser.objects.all().delete()
AcademicTerm.objects.all().delete()
Course.objects.all().delete()

COMMON_PASSWORD = "abc123"

# Create a superuser
PortalUser.objects.create_superuser(
    username="admin", password=COMMON_PASSWORD, email="admin@example.com"
)
total_records += 1

# Create programs
programs = [
    Program(
        title="Bachelor of Science in Computer Science",
        description="This 360-credit degree programme from the University of London blends strong foundational computing skills with emerging technology specialisms and case study material to help you apply your new skills to real-world contexts.",
    ),
]
Program.objects.bulk_create(programs)
total_records += len(programs)

# Create users
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
    PortalUser(
        username="student4",
        first_name="James",
        last_name="Smith",
        email="s4@example.com",
        title=PortalUser.Title.MR,
        user_type=PortalUser.UserType.STUDENT,
    ),
]
created_users = PortalUser.objects.bulk_create(users)

for user in created_users:
    user.set_password(COMMON_PASSWORD)
    user.save()

total_records += len(users)

program = Program.objects.get(title="Bachelor of Science in Computer Science")
student_profiles = [
    StudentProfile(
        user=PortalUser.objects.get(username="student1"),
        program=program,
        registration_date="2021-01-01",
        registration_expiry_date="2027-01-01",
    ),
    StudentProfile(
        user=PortalUser.objects.get(username="student2"),
        program=program,
        registration_date="2024-01-01",
        registration_expiry_date="2030-01-01",
    ),
]

StudentProfile.objects.bulk_create(student_profiles)
total_records += len(student_profiles)

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
TeacherProfile.objects.bulk_create(teacher_profiles)
total_records += len(teacher_profiles)

academic_terms = [
    AcademicTerm(
        semester=AcademicTerm.SemesterType.FALL,
        year=2023,
        start_datetime=timezone.make_aware(datetime(2023, 10, 1, 0, 0)),
        end_datetime=timezone.make_aware(datetime(2024, 3, 31, 23, 59))
    ),
    AcademicTerm(
        semester=AcademicTerm.SemesterType.SPRING,
        year=2024,
        start_datetime=timezone.make_aware(datetime(2024, 4, 1, 0, 0)),
        end_datetime=timezone.make_aware(datetime(2024, 9, 30, 23, 59))
    ),
    AcademicTerm(
        semester=AcademicTerm.SemesterType.FALL,
        year=2024,
        start_datetime=timezone.make_aware(datetime(2024, 10, 1, 0, 0)),
        end_datetime=timezone.make_aware(datetime(2025, 3, 31, 23, 59))
    ),
    AcademicTerm(
        semester=AcademicTerm.SemesterType.SPRING,
        year=2025,
        start_datetime=timezone.make_aware(datetime(2025, 4, 1, 0, 0)),
        end_datetime=timezone.make_aware(datetime(2025, 9, 30, 23, 59))
    ),
]

AcademicTerm.objects.bulk_create(academic_terms)
total_records += len(academic_terms)

courses = [
    Course(
        title="Introduction to Computer Science",
        description="An introductory course covering the essentials of computer science, from basic programming to algorithm understanding.",
        program=program,
        teacher=TeacherProfile.objects.get(user__username="teacher1"),
    ),
    Course(
        title="Data Structures and Algorithms",
        description="Study key data structures and algorithms to enhance problem-solving and software development skills.",
        program=program,
        teacher=TeacherProfile.objects.get(user__username="teacher1"),
    ),
    Course(
        title="Database Management Systems",
        description="Learn the fundamentals of database design, SQL, and managing relational database systems.",
        program=program,
        teacher=TeacherProfile.objects.get(user__username="teacher1"),
    ),
    Course(
        title="Software Engineering",
        description="Gain insights into software development processes, from design to testing and maintenance.",
        program=program,
        teacher=TeacherProfile.objects.get(user__username="teacher1"),
    ),
]

Course.objects.bulk_create(courses)
total_records += len(courses)

first_three_courses = Course.objects.all()[:3]
all_terms = AcademicTerm.objects.all()
course_offerings = []

for course, term in itertools.product(first_three_courses, all_terms):
    course_offerings.append(CourseOffering(course=course, term=term))

CourseOffering.objects.bulk_create(course_offerings)
total_records += len(course_offerings)

student_1 = StudentProfile.objects.get(user__username="student1")
course_1 = Course.objects.get(title="Introduction to Computer Science")
course_2 = Course.objects.get(title="Data Structures and Algorithms")

next_term = AcademicTerm.next()
current_term = AcademicTerm.current()
previous_term = AcademicTerm.previous()

next_offering_1 = CourseOffering.objects.filter(
    course=course_1, term=next_term
).first()
next_offering_2 = CourseOffering.objects.filter(
    course=course_2, term=next_term
).first()

current_offering_1 = CourseOffering.objects.filter(
    course=course_1, term=current_term
).first()
current_offering_2 = CourseOffering.objects.filter(
    course=course_2, term=current_term
).first()

previous_offering_1 = CourseOffering.objects.filter(
    course=course_1, term=previous_term
).first()
previous_offering_2 = CourseOffering.objects.filter(
    course=course_2, term=previous_term
).first()

enrollments = [
    StudentCourseOffering(student=student_1, offering=next_offering_1),
    StudentCourseOffering(student=student_1, offering=next_offering_2),
    StudentCourseOffering(student=student_1, offering=current_offering_1),
    StudentCourseOffering(student=student_1, offering=current_offering_2),
    StudentCourseOffering(student=student_1, offering=previous_offering_1),
    StudentCourseOffering(student=student_1, offering=previous_offering_2),
]

StudentCourseOffering.objects.bulk_create(enrollments)
total_records += len(enrollments)

print(f"Total records created: {total_records}")
