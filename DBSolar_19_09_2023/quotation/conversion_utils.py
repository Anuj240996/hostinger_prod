"""Shared helpers for ERP quotation → consumer conversion."""

from django.db import connection
from django.utils import timezone


def sync_consumer_name_from_crm_lead(quotation, lead):
    """Keep denormalized consumer_name aligned with the selected CRM lead."""
    if lead and (lead.name or "").strip():
        quotation.consumer_name = (lead.name or "")[:255]


def sync_quotation_consumer_names_for_lead(lead):
    """Push lead.name onto all ERP quotations linked to this lead."""
    if not lead or not (lead.name or "").strip():
        return 0
    from quotation.models import Quotation

    return Quotation.objects.filter(lead_id=lead.pk).update(
        consumer_name=(lead.name or "")[:255]
    )


def finalize_quotation_conversion(quotation, converted_by=None):
    """
    Mark an approved ERP quotation as converted after consumer form submit.
    Idempotent: safe to call if already converted.
    """
    if quotation is None:
        return False

    if quotation.status not in ('approved', 'converted'):
        return False

    updated_fields = []
    if not quotation.convert_consumer:
        quotation.convert_consumer = True
        updated_fields.append('convert_consumer')
    if quotation.status != 'converted':
        quotation.status = 'converted'
        updated_fields.append('status')
    if updated_fields:
        quotation.save(update_fields=updated_fields)

    try:
        from quotation.models import QuotationConversionRecord

        if QuotationConversionRecord._meta.db_table in set(connection.introspection.table_names()):
            if not QuotationConversionRecord.objects.filter(quotation=quotation).exists():
                QuotationConversionRecord.objects.create(
                    quotation=quotation,
                    converted_by=converted_by,
                )
    except Exception:
        pass

    if quotation.lead_id:
        try:
            from apps.leads.timeline import log_quotation_timeline_activity

            log_quotation_timeline_activity(quotation, converted_by, event='converted')
        except Exception:
            pass
        try:
            from apps.leads.pipeline_board import sync_lead_stage_from_pipeline_rules

            sync_lead_stage_from_pipeline_rules(quotation.lead_id, converted_by)
        except Exception:
            pass

    try:
        from apps.revenue.models import Revenue

        if quotation.lead_id:
            amount_value = quotation.final_amount or quotation.net_amount or 0
            Revenue.objects.get_or_create(
                erp_quotation=quotation,
                defaults={
                    'lead': quotation.lead,
                    'amount': amount_value,
                    'date': timezone.now().date(),
                    'payment_status': 'pending',
                },
            )
    except Exception:
        pass

    return True


def finalize_quotation_conversion_by_id(quotation_id, converted_by=None):
    from quotation.models import Quotation

    try:
        quotation = Quotation.objects.get(pk=quotation_id)
    except Quotation.DoesNotExist:
        return False
    return finalize_quotation_conversion(quotation, converted_by=converted_by)
