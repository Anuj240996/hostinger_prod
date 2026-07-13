from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm_leads', '0007_lead_rooftop_area_finance_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='roof_type',
            field=models.CharField(
                choices=[
                    ('flat', 'SLap'),
                    ('sloped', 'Sloped'),
                    ('metal', 'Metal'),
                    ('tile', 'Tile'),
                    ('mixed', 'Mixed'),
                    ('other', 'Other'),
                ],
                default='flat',
                max_length=20,
            ),
        ),
    ]
