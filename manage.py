#!/usr/bin/env python
"""
Utility script for managing the Django project.  This script mirrors the
default ``manage.py`` file created by ``django-admin startproject`` and
exposes the ``django.core.management`` command‑line utility.  Having a
``manage.py`` file in the repository makes it easy to run common tasks
like running the development server or applying migrations without
needing to know the underlying Python module names.

Usage examples:

    python manage.py runserver
    python manage.py makemigrations
    python manage.py migrate

Note: Django is not installed in this environment, so executing this
script will raise an ImportError.  It is provided here as part of the
complete example for the user's reference.
"""

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_oj.settings')
    try:
        from django.core.management import execute_from_command_line  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()