from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column, is_pg_identity_column


def fix_auth_group_id_sequence(apps, schema_editor):
  if schema_editor.connection.vendor != "postgresql":
    return

  with schema_editor.connection.cursor() as cursor:
    if is_pg_identity_column(cursor, "auth_group", "id"):
      return
    fix_pg_serial_column(cursor, schema_editor, "auth_group", "id", "auth_group_id_seq")


class Migration(migrations.Migration):
  dependencies = [
    ("user", "0011_fix_user_profile_id_sequence"),
  ]

  operations = [
    migrations.RunPython(fix_auth_group_id_sequence, reverse_code=migrations.RunPython.noop),
  ]
