from django.http import JsonResponse


def api_status(request):
    """Unauthenticated readiness for Option A phone-app integration."""
    return JsonResponse(
        {
            "ok": True,
            "architecture": "option_a",
            "owner": "django",
            "message": (
                "Django owns the database. Phone app must call HTTP APIs "
                "(do not connect phone app directly to Postgres)."
            ),
            "health": "/health/",
            "auth": {
                "token": "/api/api-token-auth/",
                "profile": "/api/get-profile/",
                "jwt_obtain": "/api/token/",
            },
            "associate": {
                "login": "/api/v1/associate/login/",
                "dashboard": "/api/v1/associate/dashboard/",
                "projects": "/api/v1/associate/projects/",
                "tasks": "/api/v1/associate/tasks/",
            },
            "consumer": {
                "login": "/api/v1/auth/login/",
                "signup": "/api/v1/auth/signup/",
                "projects": "/api/v1/projects/",
                "complaints": "/api/v1/complaints/",
                "complaints_create": "/api/v1/complaints/create/",
                "services": "/api/v1/services/",
                "services_create": "/api/v1/services/create/",
                "services_remarks": "/api/v1/services/remarks/",
            },
            "web": {
                "search_by_associate": True,
                "standard_industrial_quotation": True,
                "build": "standard-industrial-quotation-20260814",
                "page_title": "Search Staff / Consumer / Associate",
            },
        }
    )
