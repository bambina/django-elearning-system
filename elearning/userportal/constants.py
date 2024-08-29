from django.utils.translation import gettext as _

# Validation error codes
VALIDATION_ERR_REQUIRED = "required"
VALIDATION_ERR_INVALID = "invalid"
VALIDATION_ERR_MISSING_FIELD = _("{entity} must be specified")

# Invalid value error messages
INVALID_VALUE_MSG = _("Invalid value: %(value)s.")
INVALID_START_DATETIME_MSG = _("Start datetime cannot be greater than end datetime.")
INVALID_COURSE_ALREADY_STARTED_MSG = _(
    "Registration is not allowed for courses that have already started."
)

# Error messages
ERR_UNEXPECTED = _("Unexpected error in receive: {message}")
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

# Warning messages
ALREADY_ENROLLED_MSG = _("You are already enrolled in this course.")
ACTIVE_QA_SESSION_EXISTS = _("An active QA session already exists for this course.")

# Info messages
USER_ALREADY_DEACTIVATED_MSG = _("User {username} is already deactivated.")
USER_ALREADY_ACTIVATED_MSG = _("User {username} is already activated.")
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
MATERIAL_CREATED_SUCCESS_MSG = _("The material has been created successfully.")
DEACTIVATE_USER_SUCCESS_MSG = _("User {username} has been successfully deactivated.")
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
