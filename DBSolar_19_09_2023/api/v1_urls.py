"""Option A mobile API namespace — Django owns the database; phone uses these HTTP APIs."""

from django.urls import path

from . import associate_views, v1_views

urlpatterns = [
    path("status/", v1_views.api_status, name="api-v1-status"),
    path("associate/login/", associate_views.associate_login, name="api-v1-associate-login"),
    path(
        "associate/dashboard/",
        associate_views.associate_dashboard,
        name="api-v1-associate-dashboard",
    ),
    path(
        "associate/projects/",
        associate_views.associate_projects,
        name="api-v1-associate-projects",
    ),
    path(
        "associate/tasks/",
        associate_views.associate_tasks,
        name="api-v1-associate-tasks",
    ),
]
