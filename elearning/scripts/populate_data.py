import os, sys
import django

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
        biography="I am a professor of Computer Science.",
    ),
    TeacherProfile(
        user=PortalUser.objects.get(username="teacher2"),
        biography="I am a professor of Computer Science.",
    ),
]
TeacherProfile.objects.bulk_create(teacher_profiles)
total_records += len(teacher_profiles)

print(f"Total records created: {total_records}")
