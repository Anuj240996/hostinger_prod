# Fresh PostgreSQL: 0001 creates boolean; model uses bit varying — convert safely.

import quotation.models
from django.db import migrations

from inventoryproject.migration_pg_serial import convert_boolean_column_to_bit_varying


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        convert_boolean_column_to_bit_varying(
            cursor, "quotation_quotation", "system_na"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("quotation", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(forwards, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="quotation",
                    name="system_na",
                    field=quotation.models.BitVaryingBooleanField(
                        default=False, verbose_name="N.A."
                    ),
                ),
            ],
        ),
    ]
