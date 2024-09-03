from django.utils.translation import gettext as _

# Permission groups
PERMISSION_GROUP_TEACHER = "teacher"
PERMISSION_GROUP_STUDENT = "student"

# Validation error codes
VALIDATION_ERR_REQUIRED = "required"
VALIDATION_ERR_INVALID = "invalid"
VALIDATION_ERR_INVALID_SIZE = "invalid_size"
VALIDATION_ERR_MISSING_FIELD = _("{entity} must be specified")

# Invalid value error messages
INVALID_VALUE_MSG = _("Invalid value: {value}.")
INVALID_EMAIL_MSG = _("This email address is already in use.")
INVALID_START_DATETIME_MSG = _("Start datetime cannot be greater than end datetime.")
INVALID_COURSE_ALREADY_STARTED_MSG = _(
    "Registration is not allowed for courses that have already started."
)
INVALID_FILE_SIZE_MSG = _("File size must be less than {size}.")
INVALID_TEACHER_PROFILE_USER_TYPE_MSG = _(
    "User must be of type teacher to create a TeacherProfile."
)
INVALID_STUDENT_PROFILE_USER_TYPE_MSG = _(
    "User must be of type student to create a StudentProfile."
)


# Error messages
ERR_UNEXPECTED_LOG = _("Unexpected error occurred: {error}.")
ERR_UNEXPECTED_MSG = _("Unexpected error occurred. Please try again later.")
ERR_ONLY_STUDENTS_CAN_ENROLL = _("Only students can enroll in courses.")
ERR_ONLY_STUDENTS_CAN_CREATE_FEEDBACK = _("Only students can create feedback.")
ERR_ONLY_TEACHERS_CAN_CREATE_COURSES = _("Only teachers can create courses.")
ERR_ONLY_TEACHERS_CAN_CREATE_COURSE_OFFERINGS = _(
    "Only teachers can create course offerings."
)
ERR_ONLY_TEACHERS_CAN_CREATE_MATERIALS = _("Only teachers can create materials.")
ERR_DOES_NOT_EXIST = _("The requested {entity} does not exist.")
ERR_NO_CURRENT_OFFERING = _("There is no current offering for this course.")
ERR_MISSING_NOTIFICATION_LINK = _(
    "Both link_path and link_text must be provided together."
)
ERR_ONLY_AUTHORIZED_CAN_MANAGE_QA_SESSIONS = _(
    "Only authorized personnel can manage QA sessions."
)
ERR_INVALID_JSON = _("Invalid JSON received")
ERR_FAILED_TO_SEND_NOTIFICATION = _(
    "Failed to send notifications to users. Error: {exception}."
)
ERR_FAILED_TO_END_SESSION = _("Failed to end the QA session. Error: {exception}.")
ERR_UPDATE_USER_ACTIVE_STATUS_FAIL = _(
    "Failed to update the active status of user {username}."
)

# Warning messages
ALREADY_ENROLLED_MSG = _("You are already enrolled in this course.")
ACTIVE_QA_SESSION_EXISTS = _(
    "Active QA session already exists for this course. "
    "Only one Live QA Session can be created per course. Please end the current session to start a new one."
)

# Info messages
USER_ALREADY_CHANGED_MSG = _("User {username} is already {action}.")
QA_SESSION_EMPTY_MSG = _("Empty message received and ignored")
QA_SESSION_ENDED_MSG = _("Message received after session end and ignored")

# Success messages
CREATE_STUDENT_ACCOUNT_SUCCESS_MSG = _(
    "You have successfully created a student account."
)
PASSWORD_CHANGE_SUCCESS_MSG = _("Your password has been successfully changed.")
UPDATE_STATUS_SUCCESS_MSG = _("Your status has been successfully updated.")
ENROLL_COURSE_SUCCESS_MSG = _("You have successfully enrolled in the course.")
SAVE_FEEDBACK_SUCCESS_MSG = _("Your feedback has been saved successfully.")
CREATED_SUCCESS_MSG = _("The {entity} has been created successfully.")
UPDATE_USER_ACTIVE_STATUS_SUCCESS_MSG = _(
    "User {username} has been successfully {action}."
)
ACTIVATE_USER_SUCCESS_MSG = _("User {username} has been successfully activated.")
QA_SESSION_END_SUCCESS_MSG = _("QA session ended successfully.")

# Notification messages
MATERIAL_CREATED_NOTIFICATION_MSG = _(
    "A new material {material_title} has been added to the course {course_title}."
)
MATERIAL_CREATED_NOTIFICATION_LINK_TEXT = _("View material")
STUDENT_ENROLLED_NOTIFICATION_MSG = _(
    "Student {username} has enrolled in your upcoming course {course_title}."
)
STUDENT_ENROLLED_NOTIFICATION_LINK_TEXT = _("View enrolled students")
LIVE_QA_START_NOTIFICATION_MSG = _(
    "A live Q&A session has started for the course {course_title}."
)
LIVE_QA_START_NOTIFICATION_LINK_TEXT = _("Join the session")

# Constants for live Q&A session
LIVE_QA_PREFIX = "liveqa_"
MESSAGE_TYPE_CLOSE = "close.connection"
MESSAGE_TYPE_QUESTION = "question.message"
MESSAGE_TYPE_QUESTION_LIST = "question.list"
LIVE_QA_END_SESSION_MSG = _(
    "This Q&A session has concluded. Thank you for participating! Messages can no longer be sent."
)
UNAUTHORIZED_ACCESS_MSG = _("Unauthorized access to the live Q&A session.")

SESSION_TERMINATE_CODE = 4000
UNAUTHORIZED_ACCESS_CODE = 4001

# Constants for models
ALLOWED_MATERIAL_EXTENSIONS = ["pdf", "jpg", "png", "jpeg"]
MAX_MATERIAL_FILE_SIZE = 1
MAX_MATERIAL_FILE_SIZE_BYTES = MAX_MATERIAL_FILE_SIZE * 1024 * 1024

# Constants for forms
FORM_HELP_TEXT_REQUIERED = _("Required.")
