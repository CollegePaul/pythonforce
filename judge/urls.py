"""
URL patterns for the judge app.

This module maps URLs to the view functions defined in
``judge.views``.  It uses Django's ``path`` function for clarity.
"""

from __future__ import annotations
from django.urls import path  # type: ignore
from . import views


urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('problems/<int:pk>/', views.problem_detail, name='problem_detail'),
    path('submission/<int:pk>/', views.submission_detail, name='submission_detail'),
    path('progress/', views.my_progress, name='my_progress'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]