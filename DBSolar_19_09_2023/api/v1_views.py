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
        }
    )
