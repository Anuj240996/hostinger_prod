# Assignment activity type for timeline (after Lead Created)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm_leads', '0005_leadactivity_created_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadactivity',
            name='activity_type',
            field=models.CharField(
                choices=[
                    ('created', 'Lead Created'),
                    ('assignment', 'Assigned'),
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
