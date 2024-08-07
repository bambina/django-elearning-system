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
programs = [
    Program(
        title="Bachelor of Science in Computer Science",
        description="This 360-credit degree programme from the University of London blends strong foundational computing skills with emerging technology specialisms and case study material to help you apply your new skills to real-world contexts.",
    ),
]
Program.objects.bulk_create(programs)
total_records += len(programs)
print(f"Total records created: {total_records}")
