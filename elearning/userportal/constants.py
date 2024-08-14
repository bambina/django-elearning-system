from django.utils.translation import gettext as _


VALIDATION_ERR_REQUIRED = "required"
VALIDATION_ERR_INVALID = "invalid"

INVALID_VALUE_MSG = _("Invalid value: %(value)s.")

INVALID_START_DATETIME_MSG = _("Start datetime cannot be greater than end datetime.")

COURSE_ALREADY_STARTED_MSG = _(
    "Registration is not allowed for courses that have already started."
)

ALREADY_ENROLLED_MSG = _("You are already enrolled in this course.")

CREATE_STUDENT_ACCOUNT_SUCCESS_MSG = _(
    "You have successfully created a student account."
)
PASSWORD_CHANGE_SUCCESS_MSG = _("Your password has been successfully changed.")

UPDATE_STATUS_SUCCESS_MSG = _("Your status has been successfully updated.")

ENROLL_COURSE_SUCCESS_MSG = _("You have successfully enrolled in the course.")

ENROLL_COURSE_ALREADY_MSG = _("You are already enrolled in this course.")
