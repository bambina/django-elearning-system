from drf_spectacular.utils import OpenApiExample

teacher_example = OpenApiExample(
    name="Teacher Example",
    description="Example showing editable fields for a teacher profile",
    value={
        "first_name": "John",
        "last_name": "Smith",
        "title": "Dr.",
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
        "title": "Mr.",
        "profile": {
            "status": "Good!",
        },
    },
    request_only=True,
)
