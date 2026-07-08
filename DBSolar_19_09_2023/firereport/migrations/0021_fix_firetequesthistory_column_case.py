# Ensure Firetequesthistory columns match production after AssignBy rename.
from django.db import migrations, models


RENAME_ASSIGNBY_SQL = """
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'firereport_firetequesthistory'
          AND column_name = 'AssignBy'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'firereport_firetequesthistory'
          AND column_name = 'assignby'
    ) THEN
        ALTER TABLE firereport_firetequesthistory RENAME COLUMN "AssignBy" TO assignby;
    END IF;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("firereport", "0020_mobile_app_api_columns"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=RENAME_ASSIGNBY_SQL,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="firetequesthistory",
                    name="AssignBy",
                    field=models.IntegerField(db_column="assignby", default=0),
                ),
                migrations.AlterField(
                    model_name="firetequesthistory",
                    name="postingDate",
                    field=models.DateTimeField(auto_now_add=True, db_column="postingDate"),
                ),
            ],
        ),
    ]
