"""Pipeline Kanban column placement and card status badges."""

from __future__ import annotations

from apps.leads.views import (
    SURVEY_LIST_STATUS_DISPLAY,
    _latest_survey_by_lead_id,
    attach_erp_quotation_display_to_leads,
    leads_queryset_with_surveys,
)
from apps.leads.timeline import (
    QUOTATION_PIPELINE_ACTIVITY_LABELS,
    _latest_quotation_for_lead,
    _quotation_pipeline_activity_key,
    _quotation_revision_label,
)

PIPELINE_COLUMNS = (
    'new',
    'qualified',
    'survey',
    'quote',
    'negotiation',
    'won',
    'lost',
)

QUOTE_COLUMN_STATUSES = frozenset({'draft', 'sent', 'viewed'})

QUOTATION_PIPELINE_BADGES = {
    'draft': ('Draft', 'pipeline-badge-quote-draft'),
    'sent': ('Sent', 'pipeline-badge-quote-sent'),
    'revised': ('Revised', 'pipeline-badge-quote-revised'),
    'approved': ('Approved', 'pipeline-badge-quote-approved'),
    'converted': ('Converted', 'pipeline-badge-quote-converted'),
    'rejected': ('Quotation cancelled', 'pipeline-badge-quote-rejected'),
    'negotiating': ('In review', 'pipeline-badge-quote-sent'),
    'expired': ('Expired', 'pipeline-badge-quote-rejected'),
    'viewed': ('Sent', 'pipeline-badge-quote-sent'),
}


def _quotation_map_from_queryset(quotations):
    from apps.leads.views import _erp_quotation_sort_key

    latest = {}
    for quote in quotations:
        lid = quote.lead_id
        if lid not in latest:
            latest[lid] = quote
            continue
        if _erp_quotation_sort_key(quote) > _erp_quotation_sort_key(latest[lid]):
            latest[lid] = quote
    return latest


def _latest_quotation_map_all_leads(lead_ids):
    """Latest quotation per lead (no staff filter — used for stage sync and list columns)."""
    if not lead_ids:
        return {}
    try:
        from quotation.models import Quotation

        quotations = Quotation.objects.filter(lead_id__in=lead_ids).only(
            'lead_id', 'status', 'quotation_no', 'pk', 'created_at'
        )
        return _quotation_map_from_queryset(quotations)
    except Exception:
        return {}


def _latest_quotation_map_for_leads(lead_ids, user):
    """Latest ERP quotation per lead (same ordering as CRM list)."""
    if not lead_ids:
        return {}
    try:
        from customer.staff_access import quotation_queryset_for_request

        quotations = quotation_queryset_for_request(user).filter(
            lead_id__in=lead_ids,
        ).only('lead_id', 'status', 'quotation_no', 'pk', 'created_at')
        return _quotation_map_from_queryset(quotations)
    except Exception:
        return {}


def _is_negotiation_revision_quotation(quotation) -> bool:
    """True for revised quote numbers (e.g. 601_1, 601_2) — card stays in Negotiation column."""
    q_no = (getattr(quotation, 'quotation_no', None) or '').strip()
    if '_' not in q_no:
        return False
    suffix = q_no.rsplit('_', 1)[-1]
    try:
        return int(suffix) >= 1
    except ValueError:
        return False


def _revised_pipeline_label(quotation) -> str:
    """Display label: Revise v2, Revise v3, …"""
    rev = (_quotation_revision_label(quotation) or '').strip()
    if rev.startswith('v'):
        return 'Revise ' + rev
    if rev:
        return 'Revise' + rev
    return 'Revised'


def resolve_pipeline_column_for_lead(lead, latest_survey=None, latest_quotation=None):
    """
    Return (column_key, status_label, badge_class) for pipeline Kanban.
    Survey states stay in survey column until a quotation exists.
    """
    if latest_quotation:
        status = (getattr(latest_quotation, 'status', None) or 'draft').strip().lower()
        activity_key = _quotation_pipeline_activity_key(latest_quotation)

        if status == 'converted' or activity_key == 'converted':
            return 'won', 'Converted', 'pipeline-badge-quote-converted'

        if status in ('rejected', 'expired'):
            return 'lost', 'Quotation cancelled', 'pipeline-badge-quote-rejected'

        is_revision_negotiation = _is_negotiation_revision_quotation(latest_quotation)

        if activity_key == 'approved' or status == 'approved':
            return 'negotiation', 'Approved', 'pipeline-badge-quote-approved'

        if activity_key == 'negotiating' or status == 'negotiating':
            return 'negotiation', 'In review', 'pipeline-badge-quote-sent'

        if activity_key == 'draft' or status == 'draft':
            if is_revision_negotiation:
                return 'negotiation', 'Draft', 'pipeline-badge-quote-draft'
            return 'quote', 'Draft', 'pipeline-badge-quote-draft'

        if activity_key in ('sent', 'viewed') or status in ('sent', 'viewed'):
            if is_revision_negotiation:
                return 'negotiation', 'Sent', 'pipeline-badge-quote-sent'
            return 'quote', 'Sent', 'pipeline-badge-quote-sent'

        label, badge = QUOTATION_PIPELINE_BADGES.get(
            activity_key,
            (
                QUOTATION_PIPELINE_ACTIVITY_LABELS.get(activity_key, status.title()),
                'pipeline-badge-quote-draft',
            ),
        )
        column = 'negotiation' if is_revision_negotiation else 'quote'
        return column, label, badge

    if latest_survey:
        survey_status = (latest_survey.status or '').strip().lower()
        if survey_status in SURVEY_LIST_STATUS_DISPLAY:
            label, badge = SURVEY_LIST_STATUS_DISPLAY[survey_status]
            pipeline_badge = badge.replace('lead-status-', 'pipeline-badge-')
            return 'survey', label, pipeline_badge
        return 'survey', 'Survey pending', 'pipeline-badge-survey-pending'

    stage = (lead.stage or 'new').strip().lower()
    if stage in ('quote', 'negotiation'):
        return stage if stage == 'negotiation' else 'quote', lead.get_stage_display(), f'pipeline-badge-stage-{stage}'
    if stage in PIPELINE_COLUMNS:
        return stage, lead.get_stage_display(), f'pipeline-badge-stage-{stage}'
    return 'new', lead.get_stage_display(), 'pipeline-badge-stage-new'


def sync_lead_stage_from_pipeline_rules(lead_id, user=None):
    """Align lead.stage with survey/quotation pipeline rules."""
    from apps.leads.models import Lead

    lead = Lead.objects.filter(pk=lead_id).first()
    if not lead or lead.stage in ('won', 'lost') and not _should_override_terminal(lead, user):
        return

    survey_map = _latest_survey_by_lead_id([lead_id])
    quote_map = _latest_quotation_map_all_leads([lead_id])

    column, _, _ = resolve_pipeline_column_for_lead(
        lead,
        survey_map.get(lead_id),
        quote_map.get(lead_id),
    )
    stage_by_column = {
        'new': 'new',
        'qualified': 'qualified',
        'survey': 'survey',
        'quote': 'quote',
        'negotiation': 'negotiation',
        'won': 'won',
        'lost': 'lost',
    }
    new_stage = stage_by_column.get(column)
    if not new_stage or new_stage == lead.stage:
        return
    if lead.stage in ('won', 'lost') and new_stage not in ('won', 'lost'):
        return
    from django.utils import timezone as tz

    updates = {'stage': new_stage}
    if new_stage == 'won':
        updates['converted_at'] = tz.now()
    elif new_stage == 'lost':
        updates['lost_at'] = tz.now()
    Lead.objects.filter(pk=lead_id).update(**updates)


def _should_override_terminal(lead, user):
    quote_map = _latest_quotation_map_for_leads([lead.pk], user) if user else {}
    q = quote_map.get(lead.pk) or _latest_quotation_for_lead(lead)
    if not q:
        return False
    status = (getattr(q, 'status', None) or '').strip().lower()
    return status in ('converted', 'rejected', 'expired')


def pipeline_card_detail_url(lead, column: str, survey=None, quotation=None) -> str:
    """Open survey, quotation, or lead detail based on pipeline column."""
    from django.urls import reverse

    if column == 'survey' and survey:
        return reverse('survey_detail', kwargs={'pk': survey.pk})
    if column in ('quote', 'negotiation', 'won', 'lost') and quotation:
        return reverse('quotation_detail', kwargs={'pk': quotation.pk})
    return reverse('lead_detail', kwargs={'pk': lead.pk})


def build_pipeline_board(leads_qs, user):
    """Group leads into pipeline columns with status badges."""
    leads = leads_queryset_with_surveys(leads_qs)
    lead_list = list(leads)
    lead_ids = [lead.pk for lead in lead_list]

    survey_map = _latest_survey_by_lead_id(lead_ids)
    quote_map = _latest_quotation_map_for_leads(lead_ids, user)

    columns = {key: [] for key in PIPELINE_COLUMNS}
    quote_price_ids = []

    for lead in lead_list:
        survey = survey_map.get(lead.pk)
        quotation = quote_map.get(lead.pk)
        column, label, badge_class = resolve_pipeline_column_for_lead(
            lead,
            survey,
            quotation,
        )
        lead.pipeline_column = column
        lead.pipeline_status_label = label
        lead.pipeline_status_badge_class = badge_class
        lead.pipeline_card_href = pipeline_card_detail_url(lead, column, survey, quotation)
        lead.pipeline_survey_id = survey.pk if survey else None
        lead.pipeline_quotation_id = quotation.pk if quotation else None
        columns[column].append(lead)
        if column in ('quote', 'negotiation', 'won', 'lost'):
            quote_price_ids.append(lead.pk)

    attach_erp_quotation_display_to_leads(
        [lead for col in ('quote', 'negotiation', 'won', 'lost') for lead in columns[col]],
        user,
    )

    counts = {key: len(columns[key]) for key in PIPELINE_COLUMNS}
    return columns, counts
