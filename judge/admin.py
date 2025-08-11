"""
Django admin configuration for the judge app.

This file registers the ``Problem``, ``TestCase``, and ``Submission``
models with the admin site so they can be managed through the
Django administration interface.
"""

from __future__ import annotations

from django.contrib import admin  # type: ignore

from .models import Problem, TestCase, Submission


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'short_input', 'short_expected_output')
    list_filter = ('problem',)

    def short_input(self, obj: TestCase) -> str:
        return obj.input_data[:50] + ('...' if len(obj.input_data) > 50 else '')

    short_input.short_description = 'Input'

    def short_expected_output(self, obj: TestCase) -> str:
        return obj.expected_output[:50] + ('...' if len(obj.expected_output) > 50 else '')

    short_expected_output.short_description = 'Expected Output'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'created_at', 'passed')
    list_filter = ('problem', 'passed')
    readonly_fields = ('created_at', 'output', 'error')