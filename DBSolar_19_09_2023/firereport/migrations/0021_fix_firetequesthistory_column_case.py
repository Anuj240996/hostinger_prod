# Align Firetequesthistory ORM columns with production PostgreSQL mixed-case names.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("firereport", "0020_mobile_app_api_columns"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="firetequesthistory",
                    name="AssignBy",
                    field=models.IntegerField(db_column="AssignBy", default=0),
                ),
                migrations.AlterField(
                    model_name="firetequesthistory",
                    name="postingDate",
                    field=models.DateTimeField(auto_now_add=True, db_column="postingDate"),
                ),
            ],
        ),
    ]
