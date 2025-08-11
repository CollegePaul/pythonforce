"""
WSGI config for the online judge project.

This module exposes the WSGI callable as a module‑level variable named
``application``.  It is used by Django’s development server and any
WSGI-compatible web servers to serve your project.

See https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/ for
more information.
"""

import os

from django.core.wsgi import get_wsgi_application  # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_oj.settings')

application = get_wsgi_application()