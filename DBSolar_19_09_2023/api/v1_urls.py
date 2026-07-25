"""Option A mobile API namespace — Django owns the database; phone uses these HTTP APIs."""

from django.urls import path

from . import v1_views

urlpatterns = [
    path("status/", v1_views.api_status, name="api-v1-status"),
]
