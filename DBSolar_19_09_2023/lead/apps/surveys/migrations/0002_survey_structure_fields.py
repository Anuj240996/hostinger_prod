from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='structure_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('gi_structure', 'GI Structure'),
                    ('ms_structure', 'MS Structure'),
                    ('tin_shade', 'Tin Shade'),
                    ('gi_tin_shade', 'GI With Tin Shade'),
                    ('ms_tin_shade', 'MS with Tin Shade'),
                    ('gi_ms_structure', 'GI with MS Structure'),
                ],
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='survey',
            name='structure_back_height_ft',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='ft',
                max_digits=7,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='survey',
            name='structure_front_height_ft',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='ft',
                max_digits=7,
                null=True,
            ),
        ),
    ]
