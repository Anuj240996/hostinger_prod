#!/usr/bin/env python
"""
Startup migration helper for EasyPanel / existing production DBs.

Handles: ProgrammingError relation "django_content_type" already exists
when tables exist but django_migrations is missing initial rows.
"""
from __future__ import annotations

import os
import sys


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
    print(f"Faked migration record: {app}.{name}")


def pre_fake_existing_initials() -> None:
    import django
    from django.db import connection

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventoryproject.settings")
    django.setup()

    # Core Django initials that commonly pre-exist on restored DBs
    core = [
        ("contenttypes", "0001_initial", "django_content_type"),
        ("auth", "0001_initial", "auth_user"),
        ("sessions", "0001_initial", "django_session"),
        ("admin", "0001_initial", "django_admin_log"),
    ]

    with connection.cursor() as cursor:
        if not table_exists(cursor, "django_migrations"):
            print("django_migrations missing — letting migrate create it.")
            return
        for app, name, table in core:
            if table_exists(cursor, table) and not migration_recorded(cursor, app, name):
                fake_record(cursor, app, name)


def main() -> int:
    if os.environ.get("SKIP_MIGRATE", "0") == "1":
        print("SKIP_MIGRATE=1 — skipping migrations.")
        return 0

    print("Pre-faking initial migrations for tables that already exist...")
    try:
        pre_fake_existing_initials()
    except Exception as exc:
        print(f"WARNING: pre-fake step failed: {exc}")

    from django.core.management import call_command
    from django.db.utils import ProgrammingError

    try:
        call_command("migrate", interactive=False, fake_initial=True, verbosity=1)
        print("Database migrations completed.")
        return 0
    except ProgrammingError as exc:
        msg = str(exc)
        print(f"WARNING: migrate ProgrammingError: {exc}")
        if "already exists" in msg:
            print("Retrying after second pre-fake pass...")
            try:
                pre_fake_existing_initials()
                call_command("migrate", interactive=False, fake_initial=True, verbosity=1)
                print("Database migrations completed on retry.")
                return 0
            except Exception as exc2:
                print(f"WARNING: retry migrate failed: {exc2}")
        print("Continuing app startup so EasyPanel does not crash-loop.")
        print("Do NOT drop the production database.")
        return 0
    except Exception as exc:
        print(f"WARNING: migrate failed: {exc}")
        print("Continuing app startup so EasyPanel does not crash-loop.")
        print("Do NOT drop the production database.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
