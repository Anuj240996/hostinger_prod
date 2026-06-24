from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0007_survey_building_height'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='length_north_ft',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='length_south_ft',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='length_east_ft',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='length_west_ft',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='area_use_north',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='survey',
            name='area_use_south',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='survey',
            name='area_use_east',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='survey',
            name='area_use_west',
            field=models.BooleanField(default=False),
        ),
    ]
