"""Option A mobile API namespace — Django owns the database; phone uses these HTTP APIs."""

from django.urls import path

from . import associate_views, mobile_consumer_views, v1_views

urlpatterns = [
    path("status/", v1_views.api_status, name="api-v1-status"),
    # Associate
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
    # Consumer Option A
    path("auth/login/", mobile_consumer_views.consumer_login, name="api-v1-auth-login"),
    path("auth/signup/", mobile_consumer_views.consumer_signup, name="api-v1-auth-signup"),
    path("projects/", mobile_consumer_views.projects_list, name="api-v1-projects"),
    path("complaints/", mobile_consumer_views.complaints_list, name="api-v1-complaints"),
    path(
        "complaints/create/",
        mobile_consumer_views.complaints_create,
        name="api-v1-complaints-create",
    ),
    path("services/", mobile_consumer_views.services_list, name="api-v1-services"),
    path(
        "services/create/",
        mobile_consumer_views.services_create,
        name="api-v1-services-create",
    ),
    path(
        "services/remarks/",
        mobile_consumer_views.services_remarks,
        name="api-v1-services-remarks",
    ),
]
