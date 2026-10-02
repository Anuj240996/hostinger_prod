#!/usr/bin/env python
"""
Auto-fix production startup migrations.

Fixes EasyPanel crash-loop:
  ProgrammingError: relation "django_content_type" already exists

No manual env vars required. Always returns 0 so entrypoint continues to Gunicorn.
"""
from __future__ import annotations

import os
import sys


def _setup():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventoryproject.settings")
    import django

    django.setup()


def table_exists(cursor, name: str) -> bool:
    cursor.execute("SELECT to_regclass(%s)", [f"public.{name}"])
    row = cursor.fetchone()
    return bool(row and row[0])


def migration_recorded(cursor, app: str, name: str) -> bool:
    if not table_exists(cursor, "django_migrations"):
        return False
    cursor.execute(
        "SELECT 1 FROM django_migrations WHERE app=%s AND name=%s LIMIT 1",
        [app, name],
    )
    return cursor.fetchone() is not None


def fake_record(cursor, app: str, name: str) -> None:
    if migration_recorded(cursor, app, name):
        return
    cursor.execute(
        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
        [app, name],
    )
    print(f"AUTO-FAKE: {app}.{name}")


def pre_fake_existing_initials() -> int:
    from django.db import connection

    # (app, migration_name, witness_table)
    core = [
        ("contenttypes", "0001_initial", "django_content_type"),
        ("auth", "0001_initial", "auth_user"),
        ("sessions", "0001_initial", "django_session"),
        ("admin", "0001_initial", "django_admin_log"),
    ]
    count = 0
    with connection.cursor() as cursor:
        if not table_exists(cursor, "django_migrations"):
            print("django_migrations missing — migrate will create it.")
            return 0
        for app, name, table in core:
            if table_exists(cursor, table) and not migration_recorded(cursor, app, name):
                fake_record(cursor, app, name)
                count += 1
    return count


def run_migrate() -> None:
    from django.core.management import call_command

    call_command("migrate", interactive=False, fake_initial=True, verbosity=1)


def main() -> int:
    print("=== fix_startup_migrations v3 (auto) ===")
    if os.environ.get("SKIP_MIGRATE", "0") == "1":
        print("SKIP_MIGRATE=1 — skipping.")
        return 0

    try:
        _setup()
    except Exception as exc:
        print(f"WARNING: Django setup failed: {exc}")
        print("Continuing to Gunicorn anyway.")
        return 0

    try:
        n = pre_fake_existing_initials()
        print(f"Pre-faked {n} initial migration(s).")
    except Exception as exc:
        print(f"WARNING: pre-fake failed: {exc}")

    # Prefer manage.py --fake for contenttypes if table exists (belt and suspenders)
    try:
        from django.core.management import call_command
        from django.db import connection

        with connection.cursor() as cursor:
            if table_exists(cursor, "django_content_type") and not migration_recorded(
                cursor, "contenttypes", "0001_initial"
            ):
                print("Forcing: migrate contenttypes 0001 --fake")
                call_command("migrate", "contenttypes", "0001", fake=True, interactive=False, verbosity=1)
    except Exception as exc:
        print(f"WARNING: contenttypes --fake failed: {exc}")

    try:
        run_migrate()
        print("Database migrations completed.")
    except Exception as exc:
        print(f"WARNING: migrate failed ({type(exc).__name__}): {exc}")
        try:
            pre_fake_existing_initials()
            run_migrate()
            print("Database migrations completed on retry.")
        except Exception as exc2:
            print(f"WARNING: retry migrate failed: {exc2}")
            print("App will still start (no crash-loop). Do NOT drop the database.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
