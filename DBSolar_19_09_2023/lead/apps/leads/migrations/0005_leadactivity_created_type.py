# Generated for Lead Created timeline activity type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm_leads', '0004_remove_lead_associate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadactivity',
            name='activity_type',
            field=models.CharField(
                choices=[
                    ('created', 'Lead Created'),
                    ('call', 'Call'),
                    ('whatsapp', 'WhatsApp'),
                    ('email', 'Email'),
                    ('note', 'Note'),
                    ('followup', 'Follow-up'),
                    ('stage_change', 'Stage Change'),
                    ('quotation', 'Quotation'),
                    ('survey', 'Survey'),
                ],
                max_length=20,
            ),
        ),
    ]
