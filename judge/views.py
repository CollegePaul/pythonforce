from __future__ import annotations
from django.utils import timezone
import tempfile,subprocess, os
from pathlib import Path
from typing import List, Dict

from django.shortcuts import get_object_or_404, redirect, render  # type: ignore

from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from .models import Problem, Submission, TestCase, Solution
from .models import UserProblemStat 
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, F, Sum, IntegerField
from .forms import SubmissionForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.urls import reverse
from django.db.models.functions import Coalesce


def leaderboard(request):
    total_problems = Problem.objects.count()
    User = get_user_model()
    qs = (
        User.objects
        .annotate(
            completed=Count(
                'submissions__problem',
                filter=Q(submissions__passed=True),
                distinct=True,
            )
        )
        .annotate(
            percent_completed=100.0 * F('completed') / (total_problems or 1)
        )
        .order_by('-percent_completed', 'username')
    )
    return render(request, 'judge/leaderboard.html', {
        'leaders': qs,
        'total_problems': total_problems
    })

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # log them in after signup
            return redirect('problem_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def my_progress(request):
    user = request.user
    passed_sub_qs = Submission.objects.filter(
        user=user,
        problem=OuterRef('pk'),
        passed=True
    )
    problems = Problem.objects.all().annotate(
        passed=Exists(passed_sub_qs)
    )
    # Optionally: count attempts per problem for this user
    attempts_qs = Submission.objects.filter(user=user, problem=OuterRef('pk'))
    problems = problems.annotate(
        # latest attempt time or count if you want
    )
    return render(request, 'judge/my_progress.html', {'problems': problems})

def problem_list(request):
    """Render a list of all problems."""
    problems = Problem.objects.all()
    return render(request, 'judge/problem_list.html', {'problems': problems})


def problem_detail(request, pk: int):
    """Display a single problem and handle code submissions."""
    problem = get_object_or_404(Problem, pk=pk)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        form = SubmissionForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            per_results: List[Dict[str, object]] = []
            all_passed = True
            combined_lines: List[str] = []
            tmp_path: Path | None = None

            try:
                # Write submitted code to a temp file
                with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as tmp:
                    tmp.write(code)
                    tmp_path = Path(tmp.name)

                # Evaluate against each test case (ordered for stable numbering)
                for idx, case in enumerate(problem.test_cases.all().order_by('id'), start=1):
                    try:
                        result = subprocess.run(
                            ['python3', str(tmp_path)],
                            input=case.input_data,
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        actual = (result.stdout or '').strip()
                        expected = (case.expected_output or '').strip()
                        passed = (actual == expected) and result.returncode == 0

                        per_results.append({
                            'index': idx,
                            'input': case.input_data,
                            'expected': expected,
                            'actual': actual,
                            'passed': passed,
                            'stderr': (result.stderr or '').strip(),
                            'returncode': result.returncode,
                        })

                        combined_lines.append(f'#{idx} -> {actual}')
                        if not passed:
                            all_passed = False

                    except subprocess.TimeoutExpired:
                        per_results.append({
                            'index': idx,
                            'input': case.input_data,
                            'expected': (case.expected_output or '').strip(),
                            'actual': '',
                            'passed': False,
                            'stderr': 'Time limit exceeded',
                            'returncode': None,
                        })
                        combined_lines.append(f'#{idx} -> [TLE]')
                        all_passed = False

            finally:
                if tmp_path is not None:
                    try:
                        tmp_path.unlink(missing_ok=True)
                    except Exception:
                        pass

            # Create the submission with per-test breakdown
            submission = Submission.objects.create(
                problem=problem,
                code=code,
                passed=all_passed,
                output='\n'.join(combined_lines),
                per_test_results=per_results,
                user=request.user,
            )

            if all_passed and request.user.is_authenticated:
                Solution.objects.update_or_create(
                    user=request.user,
                    problem=problem,
                    defaults={'submission': submission, 'code': code},
                )
            

            if request.user.is_authenticated:
                stat, _ = UserProblemStat.objects.get_or_create(
                    user=request.user, problem=problem,
                    defaults={'attempts': 0}
                )
                stat.attempts = (stat.attempts or 0) + 1
                if all_passed and not stat.passed:
                    stat.passed = True
                    stat.first_accepted_at = timezone.now()
                stat.last_submission_at = timezone.now()
                stat.save()

            return redirect('submission_detail', pk=submission.pk)

        # Invalid form: fall through to re-render with errors
        return render(request, 'judge/problem_detail.html', {'problem': problem, 'form': form})

    # GET request → render blank form
    form = SubmissionForm()
    return render(request, 'judge/problem_detail.html', {'problem': problem, 'form': form})


def submission_detail(request, pk: int):
    """Show the results of a submission."""
    submission = get_object_or_404(Submission, pk=pk)
    return render(request, 'judge/submission_detail.html', {'submission': submission})



def leaderboard(request):
    total = Problem.objects.count()

    rows = (
        UserProblemStat.objects
        .values('user_id', 'user__username')
        .annotate(
            completed=Count('problem', filter=Q(passed=True), distinct=True),
            attempts=Coalesce(Sum('attempts'), 0, output_field=IntegerField()),
        )
    )

    # Compute percent in Python and sort
    data = []
    for r in rows:
        percent = (r['completed'] * 100.0 / total) if total else 0.0
        data.append({
            'user_id': r['user_id'],
            'username': r['user__username'],
            'completed': r['completed'],
            'attempts': r['attempts'],
            'percent': percent,
        })

    # Sort: highest % first, then fewer attempts, then username
    data.sort(key=lambda d: (-d['percent'], d['attempts'], d['username'].lower()))

    return render(request, 'judge/leaderboard.html', {
        'leaders': data,
        'total_problems': total,
    })