"""
Drop legacy ``leads`` app tables (names matching ``^leads_``) and clear ``django_migrations``.

Run once before removing the ``leads`` package from the codebase:
    python manage.py drop_legacy_leads_app
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'DROP legacy leads_* tables and delete django_migrations rows for app leads.'

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql':
            self.stderr.write(self.style.ERROR('This command only supports PostgreSQL.'))
            return

        dropped = []
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public' AND tablename ~ '^leads_'
                ORDER BY tablename;
                """
            )
            tables = [row[0] for row in cursor.fetchall()]
            for t in tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{t}" CASCADE')
                dropped.append(t)
                self.stdout.write(f'Dropped table "{t}"')

            cursor.execute("DELETE FROM django_migrations WHERE app = %s", ['leads'])
            deleted_m = cursor.rowcount

        self.stdout.write(
            self.style.SUCCESS(f'Done. Dropped {len(dropped)} table(s), removed {deleted_m} migration row(s).')
        )
