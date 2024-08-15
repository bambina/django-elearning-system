from django.utils.translation import gettext as _

# Validation error codes
VALIDATION_ERR_REQUIRED = "required"
VALIDATION_ERR_INVALID = "invalid"

# Invalid value error messages
INVALID_VALUE_MSG = _("Invalid value: %(value)s.")
INVALID_START_DATETIME_MSG = _("Start datetime cannot be greater than end datetime.")
INVALID_COURSE_ALREADY_STARTED_MSG = _(
    "Registration is not allowed for courses that have already started."
)

# Error messages
ERR_ONLY_STUDENTS_CAN_ENROLL = _("Only students can enroll in courses.")
ERR_ONLY_TEACHERS_CAN_CREATE_COURSES = _("Only teachers can create courses.")
ERR_ONLY_TEACHERS_CAN_CREATE_COURSE_OFFERINGS = _(
    "Only teachers can create course offerings."
)
ERR_DOES_NOT_EXIST = _("The requested {value} does not exist.")

# Warning messages
ALREADY_ENROLLED_MSG = _("You are already enrolled in this course.")

# Success messages
CREATE_STUDENT_ACCOUNT_SUCCESS_MSG = _(
    "You have successfully created a student account."
)
PASSWORD_CHANGE_SUCCESS_MSG = _("Your password has been successfully changed.")
UPDATE_STATUS_SUCCESS_MSG = _("Your status has been successfully updated.")
ENROLL_COURSE_SUCCESS_MSG = _("You have successfully enrolled in the course.")
