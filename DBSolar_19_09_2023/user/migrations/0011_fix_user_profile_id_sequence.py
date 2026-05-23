from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column, is_pg_identity_column


def fix_user_profile_id_sequence(apps, schema_editor):
  if schema_editor.connection.vendor != "postgresql":
    return

  with schema_editor.connection.cursor() as cursor:
    if is_pg_identity_column(cursor, "user_profile", "id"):
      return
    fix_pg_serial_column(cursor, schema_editor, "user_profile", "id", "user_profile_id_seq")


class Migration(migrations.Migration):
  dependencies = [
    ("user", "0010_fix_auth_user_id_sequence"),
  ]

  operations = [
    migrations.RunPython(fix_user_profile_id_sequence, reverse_code=migrations.RunPython.noop),
  ]
