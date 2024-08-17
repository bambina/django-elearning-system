import os
from uuid import uuid4


def path_and_rename(instance, filename):
    """Rename the file with a unique name"""
    upload_to = "materials/"
    base, ext = os.path.splitext(filename)
    new_filename = f"{base}_{uuid4().hex}{ext}"
    return os.path.join(upload_to, new_filename)
