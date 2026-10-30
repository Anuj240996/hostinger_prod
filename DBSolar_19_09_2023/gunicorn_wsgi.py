"""Gunicorn entrypoint: gunicorn gunicorn_wsgi:application"""
import os
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventoryproject.settings")

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    app = application
    try:
        from django.db import connection
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT setval('auth_user_id_seq', "
                    "(SELECT GREATEST(COALESCE(MAX(id), 1), 1) FROM auth_user), true);"
                )
            print("gunicorn_wsgi: auth_user_id_seq resynced")
    except Exception as seq_exc:
        print(f"gunicorn_wsgi: auth_user sequence resync skipped: {seq_exc}")
except Exception:
    traceback.print_exc()
    raise
