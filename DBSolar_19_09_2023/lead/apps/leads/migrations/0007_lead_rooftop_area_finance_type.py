from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm_leads', '0006_leadactivity_assignment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='rooftop_area',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Total rooftop area',
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='lead',
            name='rooftop_area_unit',
            field=models.CharField(
                blank=True,
                choices=[('m2', 'm²'), ('ft2', 'ft²')],
                default='m2',
                max_length=5,
            ),
        ),
        migrations.AddField(
            model_name='lead',
            name='finance_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('finance', 'Finance'),
                    ('cash', 'Cash'),
                    ('netbanking', 'Netbanking'),
                    ('upi', 'UPI'),
                ],
                default='',
                max_length=20,
                verbose_name='Finance',
            ),
        ),
    ]
