"""
URL configuration for the online judge project.

This module routes incoming URLs to the appropriate view functions.
It includes the Django admin and the URLs defined in the ``judge`` app.
"""

from __future__ import annotations

from django.contrib import admin  # type: ignore
from django.urls import include, path  # type: ignore
from judge import views as judge_views  # for signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('judge.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout/password views
    path('accounts/signup/', judge_views.signup, name='signup'),  # custom signup
]