"""
Forms for the online judge app.

The ``SubmissionForm`` uses a ``Textarea`` widget to allow
multi‑line code input.  In the template this textarea will be
converted to a CodeMirror editor via JavaScript.
"""

from __future__ import annotations

from django import forms  # type: ignore


class SubmissionForm(forms.Form):
    code = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        label='Your Python solution',
        help_text='Write your Python code here. Use standard input/output for I/O.'
    )