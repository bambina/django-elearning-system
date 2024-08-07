from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


# Custom validators
def registration_date_validator(value):
    """
    Validates that the registration date is not earlier than 2020-01-01.
    """
    if value < date(2020, 1, 1):
        raise ValidationError(
            _("Invalid registration date: %(value)s. Must be after 2020-01-01."),
            code="invalid",
            params={"value": value},
        )
