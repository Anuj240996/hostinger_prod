# Reverts wide CRM merge (0016) and adds only lead/survey/workflow columns.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("quotation", "0016_quotation_merge_crm_fields"),
        ("crm_leads", "0002_rename_leads_lead_stage_4b0a5d_idx_crm_leads_l_stage_4bd3a6_idx_and_more"),
        ("surveys", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="quotation", name="crm_approval_date"),
        migrations.RemoveField(model_name="quotation", name="crm_created_by"),
        migrations.RemoveField(model_name="quotation", name="crm_customer_approved"),
        migrations.RemoveField(model_name="quotation", name="crm_estimated_generation"),
        migrations.RemoveField(model_name="quotation", name="crm_gst_amount"),
        migrations.RemoveField(model_name="quotation", name="crm_gst_percentage"),
        migrations.RemoveField(model_name="quotation", name="crm_internal_approved"),
        migrations.RemoveField(model_name="quotation", name="crm_internal_notes"),
        migrations.RemoveField(model_name="quotation", name="crm_lead"),
        migrations.RemoveField(model_name="quotation", name="crm_monthly_emi"),
        migrations.RemoveField(model_name="quotation", name="crm_monthly_savings"),
        migrations.RemoveField(model_name="quotation", name="crm_negotiation_notes"),
        migrations.RemoveField(model_name="quotation", name="crm_net_cost"),
        migrations.RemoveField(model_name="quotation", name="crm_payback_years"),
        migrations.RemoveField(model_name="quotation", name="crm_quote_number"),
        migrations.RemoveField(model_name="quotation", name="crm_roi"),
        migrations.RemoveField(model_name="quotation", name="crm_sent_date"),
        migrations.RemoveField(model_name="quotation", name="crm_status"),
        migrations.RemoveField(model_name="quotation", name="crm_subsidy_amount"),
        migrations.RemoveField(model_name="quotation", name="crm_subtotal"),
        migrations.RemoveField(model_name="quotation", name="crm_survey"),
        migrations.RemoveField(model_name="quotation", name="crm_total_cost"),
        migrations.RemoveField(model_name="quotation", name="crm_valid_until"),
        migrations.RemoveField(model_name="quotation", name="crm_version"),
        migrations.RemoveField(model_name="quotation", name="crm_approved_by"),
        migrations.AddField(
            model_name="quotation",
            name="lead",
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
            name="survey",
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
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="quotations_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="quotations_approved",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="approved_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="sent_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="sent_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="quotations_sent",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="quotation",
            name="valid_until",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="quotation",
            name="status",
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
            name="version",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
