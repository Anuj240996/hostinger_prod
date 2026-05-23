from __future__ import annotations

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column, is_pg_identity_column


def fix_firereport_id_sequence(apps, schema_editor):
  """Repair firereport_firereport.id serial default after legacy MySQL import."""
  if schema_editor.connection.vendor != "postgresql":
    return

  table = "firereport_firereport"
  with schema_editor.connection.cursor() as cursor:
    if is_pg_identity_column(cursor, table, "id"):
      return
    fix_pg_serial_column(
      cursor,
      schema_editor,
      table,
      "id",
      "firereport_firereport_id_seq",
    )


class Migration(migrations.Migration):
  dependencies = [
    ("firereport", "0003_alter_firereport_message"),
  ]

  operations = [
    migrations.RunPython(fix_firereport_id_sequence, reverse_code=migrations.RunPython.noop),
  ]
