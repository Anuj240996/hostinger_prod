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


def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        LIMIT 1
        """,
        [table, column],
    )
    return cursor.fetchone() is not None


def fake_contenttypes_0002_if_name_gone() -> None:
    """
    Production DB already dropped django_content_type.name (MySQL import).
    contenttypes.0002 then fails and blocks every later migration, including
    auth_user sequence fixes. Fake it so migrate can continue.
    """
    from django.db import connection

    with connection.cursor() as cursor:
        if not table_exists(cursor, "django_content_type"):
            return
        if column_exists(cursor, "django_content_type", "name"):
            return
        if not migration_recorded(cursor, "contenttypes", "0001_initial"):
            fake_record(cursor, "contenttypes", "0001_initial")
        fake_record(cursor, "contenttypes", "0002_remove_content_type_name")


def resync_auth_user_id_sequence() -> None:
    """Prevent new-consumer 500: serial/identity sequence lag after imports."""
    from django.db import connection

    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        if not table_exists(cursor, "auth_user"):
            return
        cursor.execute(
            """
            DO $$
            DECLARE
              seq_name text;
              max_id bigint;
              is_identity boolean := false;
            BEGIN
              SELECT COALESCE(MAX(id), 0) INTO max_id FROM auth_user;
              seq_name := pg_get_serial_sequence('public.auth_user', 'id');
              SELECT COALESCE(a.attidentity <> '', false) INTO is_identity
              FROM pg_attribute a
              JOIN pg_class c ON c.oid = a.attrelid
              JOIN pg_namespace n ON n.oid = c.relnamespace
              WHERE n.nspname = 'public' AND c.relname = 'auth_user' AND a.attname = 'id';

              IF seq_name IS NOT NULL THEN
                IF max_id > 0 THEN
                  PERFORM setval(seq_name, max_id, true);
                ELSE
                  PERFORM setval(seq_name, 1, false);
                END IF;
              ELSIF is_identity THEN
                EXECUTE format(
                  'ALTER TABLE public.auth_user ALTER COLUMN id RESTART WITH %s',
                  GREATEST(max_id, 0) + 1
                );
              ELSE
                IF NOT EXISTS (
                  SELECT 1 FROM pg_class c
                  JOIN pg_namespace n ON n.oid = c.relnamespace
                  WHERE c.relkind = 'S' AND c.relname = 'auth_user_id_seq'
                ) THEN
                  CREATE SEQUENCE auth_user_id_seq;
                END IF;
                BEGIN
                  ALTER TABLE auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq');
                EXCEPTION WHEN others THEN
                  NULL;
                END;
                IF max_id > 0 THEN
                  PERFORM setval('auth_user_id_seq', max_id, true);
                ELSE
                  PERFORM setval('auth_user_id_seq', 1, false);
                END IF;
              END IF;
            END $$;
            """
        )
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM auth_user;")
        max_id = cursor.fetchone()[0]
        cursor.execute("SELECT pg_get_serial_sequence('public.auth_user', 'id');")
        seq_name = cursor.fetchone()[0]
        last_val = None
        if seq_name:
            cursor.execute("SELECT last_value FROM %s;" % seq_name)
            last_val = cursor.fetchone()[0]
    print(f"Resynced auth_user id sequence last={last_val} max_id={max_id}")


def run_migrate() -> None:
    from django.core.management import call_command

    call_command("migrate", interactive=False, fake_initial=True, verbosity=1)


def main() -> int:
    print("=== fix_startup_migrations v8 (auto) ===")
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

    try:
        fake_contenttypes_0002_if_name_gone()
    except Exception as exc:
        print(f"WARNING: contenttypes.0002 fake failed: {exc}")

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
        resync_auth_user_id_sequence()
    except Exception as exc:
        print(f"WARNING: auth_user sequence resync failed: {exc}")

    try:
        run_migrate()
        print("Database migrations completed.")
    except Exception as exc:
        print(f"WARNING: migrate failed ({type(exc).__name__}): {exc}")
        try:
            pre_fake_existing_initials()
            fake_contenttypes_0002_if_name_gone()
            run_migrate()
            print("Database migrations completed on retry.")
        except Exception as exc2:
            print(f"WARNING: retry migrate failed: {exc2}")
            print("App will still start (no crash-loop). Do NOT drop the database.")

    try:
        resync_auth_user_id_sequence()
    except Exception as exc:
        print(f"WARNING: auth_user sequence resync failed: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
