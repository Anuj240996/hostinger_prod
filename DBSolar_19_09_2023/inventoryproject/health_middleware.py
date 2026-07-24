from django.http import HttpResponse


class HealthCheckMiddleware:
    """Return 200 for /health/ before ALLOWED_HOSTS / auth can fail the probe."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path == "/health" or path == "/health/":
            return HttpResponse("ok", content_type="text/plain")
        return self.get_response(request)
