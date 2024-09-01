from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .constants import *


# Custom validators


def file_size_validator(value):
    """
    Validates that the file size is not greater than 1 MB.
    """
    if value.size > MAX_MATERIAL_FILE_SIZE:
        raise ValidationError(
            _(f"File size must be less than 1 MB."),
            code='invalid_size',
            params={'value': value.size},
        )
