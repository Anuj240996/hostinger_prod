from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm_leads', '0002_rename_leads_lead_stage_4b0a5d_idx_crm_leads_l_stage_4bd3a6_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='associate',
            field=models.ForeignKey(
                blank=True,
                help_text='Team member who sourced or assists with this lead.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='crm_associate_leads',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Associate',
            ),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['associate'], name='crm_leads_l_associate_idx'),
        ),
    ]
