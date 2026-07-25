from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0012_survey_walkway_ladder"),
    ]

    operations = [
        migrations.AlterField(
            model_name="survey",
            name="panel_count",
            field=models.CharField(
                blank=True, help_text="W", max_length=32, null=True
            ),
        ),
    ]
