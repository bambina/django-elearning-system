from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .constants import *


# Custom validators


def file_size_validator(value):
    """
    Validates that the file size is not greater than 1 MB.
    """
    if value.size > MAX_MATERIAL_FILE_SIZE_BYTES:
        size_in_mb = f"{value.size / (1024 * 1024):.1f} MB"
        max_size_in_mb = f"{MAX_MATERIAL_FILE_SIZE} MB"
        raise ValidationError(
            INVALID_VALUE_MSG.format(value=size_in_mb)
            + " "
            + INVALID_FILE_SIZE_MSG.format(size=max_size_in_mb),
            code=VALIDATION_ERR_INVALID_SIZE,
        )
