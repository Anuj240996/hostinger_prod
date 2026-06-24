from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0010_alter_survey_building_height'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='panel_count',
            field=models.CharField(blank=True, help_text='kW', max_length=32, null=True),
        ),
    ]

