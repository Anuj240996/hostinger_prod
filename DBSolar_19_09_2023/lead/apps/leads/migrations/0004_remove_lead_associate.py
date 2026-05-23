from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm_leads', '0003_lead_associate'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='lead',
            name='crm_leads_l_associate_idx',
        ),
        migrations.RemoveField(
            model_name='lead',
            name='associate',
        ),
    ]
