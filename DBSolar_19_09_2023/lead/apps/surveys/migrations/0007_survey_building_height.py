from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0006_survey_structure_solar_panel_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='building_height',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='m',
                max_digits=7,
                null=True,
            ),
        ),
    ]
