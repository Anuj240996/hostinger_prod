from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0003_alter_survey_estimated_generation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='structure_leg_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='structure_purlin_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
