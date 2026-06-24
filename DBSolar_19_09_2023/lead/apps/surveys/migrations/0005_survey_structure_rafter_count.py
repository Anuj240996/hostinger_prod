from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0004_survey_structure_leg_purlin'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='structure_rafter_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
