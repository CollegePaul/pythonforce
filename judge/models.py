"""
Database models for the online judge app.

These models represent programming problems (``Problem``), input/output
test cases for each problem (``TestCase``), and code submissions
(``Submission``).  Submissions store the submitted code, whether it
passed all test cases, and any output produced during evaluation.
"""

from __future__ import annotations

from django.db import models  # type: ignore


class Problem(models.Model):
    """A programming challenge for students to solve.

    Each problem has a title and a longer description.  A problem can
    have multiple associated test cases which define the expected
    behaviour of a correct solution.
    """

    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class TestCase(models.Model):
    """An individual test case for a problem.

    ``input_data`` should contain the raw text that will be provided on
    standard input to the user's program.  ``expected_output`` should
    contain the exact text (with newlines) that should be printed on
    standard output by a correct solution.
    """

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self) -> str:
        return f'Test case for {self.problem.title}'


class Submission(models.Model):
    """A user's attempt at solving a problem.

    Stores the raw ``code`` submitted by the user, a timestamp, a flag
    indicating whether all test cases were passed, and the combined
    output or error messages generated during execution.  ``passed``
    defaults to ``None`` so that new submissions can be distinguished
    from evaluated ones.
    """

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    passed = models.BooleanField(null=True)
    output = models.TextField(blank=True)
    error = models.TextField(blank=True)

    def __str__(self) -> str:
        status = 'passed' if self.passed else 'failed' if self.passed is not None else 'pending'
        return f'Submission #{self.pk} for {self.problem.title} ({status})'