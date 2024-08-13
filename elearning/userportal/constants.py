from django.utils.translation import gettext as _


VALIDATION_ERR_REQUIRED = "required"
VALIDATION_ERR_INVALID = "invalid"

INVALID_VALUE_MSG = _("Invalid value: %(value)s.")

INVALID_START_DATETIME_MSG = _("Start datetime cannot be greater than end datetime.")

CREATE_STUDENT_ACCOUNT_SUCCESS_MSG = _(
    "You have successfully created a student account."
)
PASSWORD_CHANGE_SUCCESS_MSG = _("Your password has been successfully changed.")

UPDATE_STATUS_SUCCESS_MSG = _("Your status has been successfully updated.")
