from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("firereport", "0024_complaintactionotp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servicerequest",
            name="Status",
            field=models.CharField(
                blank=True,
                db_column="status",
                default="Pending",
                max_length=150,
                null=True,
            ),
        ),
    ]
