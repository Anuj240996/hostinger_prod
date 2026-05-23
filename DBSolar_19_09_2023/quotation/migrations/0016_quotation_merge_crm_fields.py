# Merged Lead CRM (apps.quotations) snapshot fields onto ERP quotation_quotation.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("quotation", "0015_quotation_assigned_associate"),
        ("crm_leads", "0002_rename_leads_lead_stage_4b0a5d_idx_crm_leads_l_stage_4bd3a6_idx_and_more"),
        ("surveys", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="quotation",
            name="crm_lead",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="erp_quotations",
                to="crm_leads.lead",
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_survey",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="erp_quotations",
                to="surveys.survey",
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_quote_number",
            field=models.CharField(
                blank=True,
                help_text="Optional Q-YYYY-NNNN style number from CRM.",
                max_length=50,
                verbose_name="CRM quote number",
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("sent", "Sent"),
                    ("viewed", "Viewed"),
                    ("negotiating", "Negotiating"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("expired", "Expired"),
                ],
                default="draft",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_subtotal",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_gst_percentage",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_gst_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_total_cost",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_subsidy_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_net_cost",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_roi",
            field=models.DecimalField(
                blank=True, decimal_places=2, help_text="%", max_digits=5, null=True
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_payback_years",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_monthly_emi",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_monthly_savings",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_estimated_generation",
            field=models.IntegerField(
                blank=True,
                help_text="Annual generation (kWh/year), aligned with CRM quotation.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_valid_until",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_sent_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_approval_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_negotiation_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_internal_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_customer_approved",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_internal_approved",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="crm_approved_erp_quotations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="crm_created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="crm_created_erp_quotations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
