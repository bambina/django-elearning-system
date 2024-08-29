from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .constants import *


# Custom validators

def file_size_validator(value):
    """
    Validates that the file size is not greater than 1 MB.
    """
    if value.size > 1 * 1024 * 1024:
        raise ValidationError(
            {
                "file": ValidationError(
                    f"{INVALID_VALUE_MSG} {_('File size must be less than 1 MB.')}",
                    code=VALIDATION_ERR_INVALID,
                    params={"value": value},
                )
            }
        )
