"""
Configuration for the judge Django app.
"""

from __future__ import annotations

from django.apps import AppConfig  # type: ignore


class JudgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'judge'
    verbose_name = 'Online Judge'