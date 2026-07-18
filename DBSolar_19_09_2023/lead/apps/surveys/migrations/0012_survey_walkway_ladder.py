from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0011_alter_survey_panel_count_to_charfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='structure_has_walkway',
            field=models.BooleanField(
                default=False,
                help_text='Optional walkway between panel rows (+2 rafters, +4 purlins)',
            ),
        ),
        migrations.AddField(
            model_name='survey',
            name='structure_has_ladder',
            field=models.BooleanField(
                default=False,
                help_text='Optional ladder attached to the walkway',
            ),
        ),
        migrations.AddField(
            model_name='survey',
            name='structure_square_pipe_count',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Square pipe quantity for ladder (shown when ladder is selected)',
                null=True,
            ),
        ),
    ]
