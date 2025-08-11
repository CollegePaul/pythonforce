"""
ASGI config for the online judge project.

This module exposes the ASGI callable as a module‑level variable named
``application``.  It is used by Django’s ASGI servers for asynchronous
communication.

See https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/ for
more information.
"""

import os

from django.core.asgi import get_asgi_application  # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_oj.settings')

application = get_asgi_application()