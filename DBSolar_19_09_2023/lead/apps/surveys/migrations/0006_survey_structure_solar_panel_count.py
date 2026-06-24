from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0005_survey_structure_rafter_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='structure_solar_panel_count',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Physical PV modules mounted on structure (typically 1 per 2 purlins)',
                null=True,
            ),
        ),
    ]
