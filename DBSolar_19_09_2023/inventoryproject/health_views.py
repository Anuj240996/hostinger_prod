from django.http import HttpResponse


def health_check(request):
    """Plain 200 for EasyPanel / load-balancer probes (no DB)."""
    return HttpResponse("ok", content_type="text/plain")
