from drf_spectacular.utils import OpenApiExample

admin_example = OpenApiExample(
    name="Admin Example",
    description="Example showing editable fields for an admin profile",
    value={
        "first_name": "",
        "last_name": "",
        "title": None,
    },
    request_only=True,
)

teacher_example = OpenApiExample(
    name="Teacher Example",
    description="Example showing editable fields for a teacher profile",
    value={
        "first_name": "John",
        "last_name": "Smith",
        "title": "PROF",
        "profile": {
            "biography": "Prof. John Smith is a Professor of Computer Science ..."
        },
    },
    request_only=True,
)

student_example = OpenApiExample(
    name="Student Example",
    description="Example showing editable fields for a student profile",
    value={
        "first_name": "Michael",
        "last_name": "Brown",
        "title": "MR",
        "profile": {
            "status": "Good!",
        },
    },
    request_only=True,
)

auth_example = OpenApiExample(
    name="Authentication Example",
    description="Example showing a valid API token authentication request",
    value={"username": "admin", "password": "abc"},
    request_only=True,
)
