"""Gunicorn entrypoint: gunicorn gunicorn_wsgi:application"""
import os
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventoryproject.settings")

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    app = application
except Exception:
    traceback.print_exc()
    raise
