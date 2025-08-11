"""
View functions for the online judge.

The two primary views provided here are:

* ``problem_list`` – lists all available problems.
* ``problem_detail`` – displays a single problem, shows a CodeMirror
  editor for code submission, accepts form submissions, evaluates
  submitted code against the problem's test cases, and stores the
  results.
* ``submission_detail`` – shows the outcome of a submission.

Evaluation is performed by writing the submitted code to a temporary
file and running it using the system Python interpreter.  ``subprocess.run``
is used with ``capture_output=True`` and a small ``timeout`` to avoid
processes running indefinitely.  As noted in the referenced Stack
Exchange discussion, running untrusted code in process can be
dangerous; for a production system you should isolate execution via
containers or OS‑level sandboxing【645923053692825†L197-L210】.
"""

from __future__ import annotations

import tempfile
import subprocess
from pathlib import Path
from typing import List

from django.shortcuts import get_object_or_404, redirect, render  # type: ignore

from .models import Problem, Submission, TestCase
from .forms import SubmissionForm


def problem_list(request):
    """Render a list of all problems."""
    problems = Problem.objects.all()
    return render(request, 'judge/problem_list.html', {'problems': problems})


def problem_detail(request, pk: int):
    """Display a single problem and handle code submissions."""
    problem = get_object_or_404(Problem, pk=pk)
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            submission = Submission.objects.create(problem=problem, code=code)
            # Evaluate the code against all test cases
            passed_all = True
            outputs: List[str] = []
            errors: List[str] = []
            # Write code to a temporary file
            with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as tmp:
                tmp.write(code)
                tmp_path = Path(tmp.name)
            for case in problem.test_cases.all():
                try:
                    # Use subprocess to run the user's code with the test input
                    result = subprocess.run(
                        [
                            'python3',
                            str(tmp_path),
                        ],
                        input=case.input_data,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    output = result.stdout.strip()
                    outputs.append(f'Input:\n{case.input_data}\nOutput:\n{output}')
                    # Compare output to expected output (strip trailing whitespace)
                    if output != case.expected_output.strip():
                        passed_all = False
                except subprocess.TimeoutExpired:
                    passed_all = False
                    outputs.append(f'Input:\n{case.input_data}\nOutput:\nTIMEOUT')
                except Exception as exc:
                    passed_all = False
                    errors.append(str(exc))
            # Clean up temporary file
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
            submission.passed = passed_all
            submission.output = '\n\n'.join(outputs)
            submission.error = '\n'.join(errors)
            submission.save()
            return redirect('submission_detail', pk=submission.pk)
    else:
        form = SubmissionForm()
    return render(request, 'judge/problem_detail.html', {'problem': problem, 'form': form})


def submission_detail(request, pk: int):
    """Show the results of a submission."""
    submission = get_object_or_404(Submission, pk=pk)
    return render(request, 'judge/submission_detail.html', {'submission': submission})