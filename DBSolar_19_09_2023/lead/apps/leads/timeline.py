"""Build unified timeline entries for lead detail (Quickest CRM-style feed)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime


TIMELINE_STYLES: dict[str, dict[str, str]] = {
    'created': {'color': '#10b981', 'icon': 'fa-plus-circle'},
    'assignment': {'color': '#6366f1', 'icon': 'fa-user-check'},
    'call': {'color': '#22c55e', 'icon': 'fa-phone'},
    'whatsapp': {'color': '#25d366', 'icon': 'fa-whatsapp'},
    'email': {'color': '#0ea5e9', 'icon': 'fa-envelope'},
    'note': {'color': '#f59e0b', 'icon': 'fa-sticky-note'},
    'followup': {'color': '#a855f7', 'icon': 'fa-calendar-check'},
    'stage_change': {'color': '#64748b', 'icon': 'fa-exchange-alt'},
    'quotation': {'color': '#ec4899', 'icon': 'fa-file-invoice'},
    'survey': {'color': '#14b8a6', 'icon': 'fa-clipboard-list'},
    'message': {'color': '#3b82f6', 'icon': 'fa-paper-plane'},
}


def _user_display(user) -> str:
    if not user:
        return 'System'
    return (user.get_full_name() or '').strip() or user.username


def _status_label(status: str) -> str:
    if not status:
        return ''
    return status.replace('_', ' ').title()


def lead_has_converted_estimate(lead) -> bool:
    """True when any ERP quotation linked to this lead has status converted."""
    try:
        return lead.erp_quotations.filter(status='converted').exists()
    except Exception:
        return False


def _quotation_timeline_created(quotation) -> datetime:
    """Use conversion time for converted estimates; otherwise quotation created_at."""
    status = (getattr(quotation, 'status', None) or '').strip().lower()
    if status == 'converted':
        try:
            from django.db import connection
            from quotation.models import QuotationConversionRecord

            if QuotationConversionRecord._meta.db_table in set(connection.introspection.table_names()):
                conv = (
                    QuotationConversionRecord.objects.filter(quotation=quotation)
                    .order_by('-created_at')
                    .first()
                )
                if conv and getattr(conv, 'created_at', None):
                    return _coerce_datetime(conv.created_at)
        except Exception:
            pass
        for attr in ('approved_date', 'sent_date', 'created_at'):
            val = getattr(quotation, attr, None)
            if val:
                return _coerce_datetime(val)
    return _coerce_datetime(getattr(quotation, 'created_at', None))


def _coerce_datetime(value) -> datetime:
    """Normalize DB/datetime-local strings so timeline sort never mixes types."""
    if value is None or value == '':
        return timezone.now()
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime.combine(value, datetime.min.time())
    elif isinstance(value, (int, float)):
        try:
            dt = datetime.fromtimestamp(value, tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return timezone.now()
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            return timezone.now()
        dt = parse_datetime(raw.replace(' ', 'T', 1) if ' ' in raw and 'T' not in raw else raw)
        if dt is None:
            dt = parse_datetime(raw)
        if dt is None and len(raw) >= 10:
            d = parse_date(raw[:10])
            if d is not None:
                dt = datetime.combine(d, datetime.min.time())
        if dt is None:
            return timezone.now()
    else:
        return timezone.now()
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def _timeline_sort_key(value) -> float:
    """Float timestamp for stable sort (never compare datetime to str)."""
    return _coerce_datetime(value).timestamp()


# When timestamps tie: created is oldest, then assignment, then other events.
_TIMELINE_KIND_RANK = {
    'created': 0,
    'assignment': 1,
    'survey': 2,
    'quotation': 3,
}

SURVEY_EVENT_LABELS = {
    'pending': 'Survey pending',
    'scheduled': 'Survey scheduled',
    'rescheduled': 'Survey rescheduled',
    'in_progress': 'Survey in progress',
    'completed': 'Survey completed',
    'cancelled': 'Survey cancelled',
}


def _survey_timeline_marker_class(event: str) -> str:
    event = (event or '').strip().lower()
    if event == 'completed':
        return 'bg-success'
    if event == 'cancelled':
        return 'bg-danger'
    if event in ('scheduled', 'rescheduled'):
        return 'bg-primary'
    if event == 'in_progress':
        return 'bg-warning text-dark'
    if event == 'assignment':
        return 'bg-info'
    return 'bg-primary'


def _survey_timeline_icon_class(event: str) -> str:
    event = (event or '').strip().lower()
    if event == 'completed':
        return 'fa-check'
    if event == 'cancelled':
        return 'fa-times'
    if event in ('scheduled', 'rescheduled'):
        return 'fa-calendar-alt'
    if event == 'in_progress':
        return 'fa-spinner'
    if event == 'assignment':
        return 'fa-user-check'
    return 'fa-calendar-plus'


def build_survey_detail_timeline(survey) -> list[dict[str, Any]]:
    """Timeline entries for survey detail page (from LeadActivity + survey fields)."""
    from apps.leads.models import LeadActivity

    entries: list[dict[str, Any]] = []
    survey_pk = int(survey.pk)

    activities = (
        LeadActivity.objects.filter(lead_id=survey.lead_id, activity_type='survey')
        .select_related('user')
        .order_by('created')
    )
    for activity in activities:
        meta = activity.metadata if isinstance(activity.metadata, dict) else {}
        sid = meta.get('survey_id')
        if sid is not None and int(sid) != survey_pk:
            continue
        event = (meta.get('event') or meta.get('status') or 'pending').strip().lower()
        if sid is None:
            desc = activity.description or ''
            if str(survey_pk) not in desc:
                continue
        entries.append({
            'created': activity.created,
            'title': (activity.description or '').strip() or _survey_event_title(survey, event),
            'subtitle': '',
            'user_name': _user_display(activity.user),
            'event': event,
            'marker_class': _survey_timeline_marker_class(event),
            'icon_class': _survey_timeline_icon_class(event),
        })

    has_assigned = any(e.get('event') == 'assignment' for e in entries)
    if survey.assigned_date and survey.engineer and not has_assigned:
        entries.append({
            'created': _coerce_datetime(survey.assigned_date),
            'title': 'Engineer assigned — ' + _user_display(survey.engineer),
            'subtitle': '',
            'user_name': _user_display(survey.created_by),
            'event': 'assignment',
            'marker_class': _survey_timeline_marker_class('assignment'),
            'icon_class': _survey_timeline_icon_class('assignment'),
        })

    if not entries:
        entries.append({
            'created': _coerce_datetime(survey.created),
            'title': _survey_event_title(survey, 'pending'),
            'subtitle': '',
            'user_name': _user_display(survey.created_by),
            'event': 'pending',
            'marker_class': _survey_timeline_marker_class('pending'),
            'icon_class': _survey_timeline_icon_class('pending'),
        })
        if survey.scheduled_date:
            entries.append({
                'created': _coerce_datetime(survey.scheduled_date),
                'title': _survey_event_title(survey, 'scheduled'),
                'subtitle': '',
                'user_name': _user_display(survey.created_by),
                'event': 'scheduled',
                'marker_class': _survey_timeline_marker_class('scheduled'),
                'icon_class': _survey_timeline_icon_class('scheduled'),
            })
        if survey.completed_date:
            entries.append({
                'created': _coerce_datetime(survey.completed_date),
                'title': _survey_event_title(survey, 'completed'),
                'subtitle': '',
                'user_name': _user_display(survey.created_by),
                'event': 'completed',
                'marker_class': _survey_timeline_marker_class('completed'),
                'icon_class': _survey_timeline_icon_class('completed'),
            })
        elif survey.status == 'cancelled':
            entries.append({
                'created': _coerce_datetime(survey.modified),
                'title': _survey_event_title(survey, 'cancelled'),
                'subtitle': '',
                'user_name': _user_display(survey.created_by),
                'event': 'cancelled',
                'marker_class': _survey_timeline_marker_class('cancelled'),
                'icon_class': _survey_timeline_icon_class('cancelled'),
            })

    entries.sort(key=lambda e: _coerce_datetime(e['created']), reverse=True)
    return entries

QUOTATION_EVENT_LABELS = {
    'created': 'Quotation created (Draft)',
    'draft': 'Quotation draft',
    'sent': 'Quotation sent',
    'revised': 'Revised quotation',
    'approved': 'Quotation approved',
    'rejected': 'Quotation rejected',
    'converted': 'Quotation converted',
}

QUOTATION_PIPELINE_ACTIVITY_LABELS = {
    'draft': 'Draft',
    'sent': 'Sent',
    'revised': 'Revised',
    'approved': 'Approved',
    'converted': 'Converted',
    'rejected': 'Rejected',
    'negotiating': 'In review',
    'expired': 'Expired',
    'viewed': 'Sent',
}


def _quotation_revision_label(quotation) -> str:
    """e.g. quotation_no EST-601_2 → ' v2'"""
    q_no = (getattr(quotation, 'quotation_no', None) or '').strip()
    if '_' in q_no:
        suffix = q_no.rsplit('_', 1)[-1]
        try:
            return ' v' + str(int(suffix))
        except ValueError:
            return ' (' + suffix + ')'
    version = getattr(quotation, 'version', None)
    try:
        if version and int(version) > 1:
            return ' v' + str(int(version))
    except (TypeError, ValueError):
        pass
    return ''


def _quotation_amount_str(quotation) -> str:
    amount = getattr(quotation, 'final_amount', None) or getattr(quotation, 'net_amount', None)
    if amount is None:
        return ''
    try:
        return ' ₹{:,.0f}'.format(float(amount))
    except (TypeError, ValueError):
        return ' ₹' + str(amount)


def _quotation_timeline_title(quotation) -> str:
    status_text = _status_label((getattr(quotation, 'status', None) or 'draft').strip())
    q_no = (getattr(quotation, 'quotation_no', None) or '').strip() or ('#' + str(quotation.pk))
    title = 'Estimate'
    if status_text:
        title += ' [' + status_text + ']'
    title += ' ' + q_no + _quotation_amount_str(quotation)
    return title


def _quotation_event_title(quotation, event: str) -> str:
    q_no = (getattr(quotation, 'quotation_no', None) or '').strip() or ('#' + str(quotation.pk))
    rev = _quotation_revision_label(quotation)
    base = QUOTATION_EVENT_LABELS.get(event, 'Quotation update')
    if event == 'revised':
        return f'{base}{rev} — {q_no}'
    if event in ('sent', 'approved', 'rejected', 'converted'):
        return f'{base} — {q_no}{rev}'
    if event in ('created', 'draft'):
        return f'{base} — {q_no}'
    return f'{base} — {q_no}{rev}'


def _build_quotation_timeline_entry(quotation, event: str = '', event_note: str = '') -> dict[str, Any]:
    q_status = (getattr(quotation, 'status', '') or 'draft').strip().lower()
    extra_lines: list[str] = []
    if not event:
        event = 'converted' if q_status == 'converted' else ('sent' if q_status == 'sent' else 'draft')
    title = _quotation_event_title(quotation, event) if event else _quotation_timeline_title(quotation)
    if event_note and event_note not in title:
        extra_lines.append(event_note)
    extra_lines.append('Status: ' + _status_label(q_status or 'draft'))
    return {
        'kind': 'quotation',
        'created': _quotation_timeline_created(quotation),
        'title': title,
        'description': '',
        'user': getattr(quotation, 'created_by', None),
        'metadata': {
            'quotation_id': quotation.pk,
            'status': getattr(quotation, 'status', 'draft'),
            'event': event,
        },
        'extra_lines': extra_lines,
    }


def log_quotation_timeline_activity(quotation, user=None, event: str = 'created'):
    """
    Record quotation lifecycle on the lead timeline (draft, sent, revised, approved, converted).
    """
    if not getattr(quotation, 'lead_id', None):
        return None
    from apps.leads.models import LeadActivity

    title = _quotation_event_title(quotation, event)
    activity = LeadActivity.objects.create(
        lead_id=quotation.lead_id,
        user=user,
        activity_type='quotation',
        description=title,
        metadata={
            'quotation_id': quotation.pk,
            'status': getattr(quotation, 'status', 'draft'),
            'event': event,
            'quotation_no': (getattr(quotation, 'quotation_no', None) or '').strip(),
            'revision': _quotation_revision_label(quotation).strip(),
        },
    )
    try:
        from apps.leads.pipeline_board import sync_lead_stage_from_pipeline_rules

        sync_lead_stage_from_pipeline_rules(quotation.lead_id, user)
    except Exception:
        pass
    return activity


def _survey_event_title(survey, event: str) -> str:
    label = SURVEY_EVENT_LABELS.get(event, SURVEY_EVENT_LABELS.get(survey.status, 'Site Survey'))
    survey_ref = 'Survey #' + str(survey.pk)
    if survey.scheduled_date:
        survey_ref += ' — ' + _coerce_datetime(survey.scheduled_date).strftime('%d %b %Y')
    return label + ' (' + survey_ref + ')'


def log_survey_timeline_activity(survey, user=None, event: str = 'pending'):
    """Record site survey pending / complete on the lead timeline."""
    if not getattr(survey, 'lead_id', None):
        return None
    from apps.leads.models import LeadActivity

    if not event or event == 'pending':
        event = survey.status if survey.status in SURVEY_EVENT_LABELS else 'pending'
    title = _survey_event_title(survey, event)
    created = _coerce_datetime(survey.completed_date if event == 'completed' else survey.scheduled_date or survey.created)
    activity = LeadActivity.objects.create(
        lead_id=survey.lead_id,
        user=user,
        activity_type='survey',
        description=title,
        metadata={
            'survey_id': survey.pk,
            'status': survey.status,
            'event': event,
        },
    )
    try:
        from apps.leads.pipeline_board import sync_lead_stage_from_pipeline_rules

        sync_lead_stage_from_pipeline_rules(survey.lead_id, user)
    except Exception:
        pass
    return activity


def _build_survey_timeline_entry(survey, event: str = '') -> dict[str, Any]:
    if not event:
        if survey.status == 'completed':
            event = 'completed'
        elif survey.status == 'cancelled':
            event = 'cancelled'
        else:
            event = 'pending'
    return {
        'kind': 'survey',
        'created': _coerce_datetime(
            survey.completed_date if event == 'completed' else (survey.scheduled_date or survey.created)
        ),
        'title': _survey_event_title(survey, event),
        'description': '',
        'user': getattr(survey, 'created_by', None),
        'metadata': {'survey_id': survey.pk, 'status': survey.status, 'event': event},
        'extra_lines': [],
    }


def _survey_pipeline_activity_key(survey) -> str:
    """CSS helper for survey pipeline badge styling."""
    status = (getattr(survey, 'status', None) or '').strip().lower()
    if status == 'completed':
        return 'complete'
    if status == 'cancelled':
        return 'cancelled'
    return 'pending'


def _quotation_pipeline_activity_key(quotation) -> str:
    """Granular quotation status from DB (draft, sent, approved, …) — not overridden by revision suffix."""
    status = (getattr(quotation, 'status', None) or 'draft').strip().lower()
    if status in ('viewed',):
        return 'sent'
    if status in QUOTATION_PIPELINE_ACTIVITY_LABELS:
        return status
    return 'draft'


def _latest_quotation_for_lead(lead):
    try:
        from quotation.models import Quotation

        return (
            Quotation.objects.filter(lead_id=lead.pk)
            .order_by('-created_at')
            .first()
        )
    except Exception:
        return None


def build_lead_pipeline_context(lead) -> dict[str, Any]:
    """Pipeline activity badges (original labels) + flags for stage dropdown."""
    ctx: dict[str, Any] = {
        'pipeline_survey_label': None,
        'pipeline_survey_status': None,
        'pipeline_survey_activity_key': None,
        'pipeline_quotation_label': None,
        'pipeline_quotation_status': None,
        'pipeline_quotation_activity_key': None,
        'pipeline_quotation_no': None,
        'pipeline_has_survey': False,
        'pipeline_has_quotation': False,
    }
    try:
        latest_survey = lead.surveys.order_by('-scheduled_date', '-created').first()
        if latest_survey:
            ctx['pipeline_has_survey'] = True
            ctx['pipeline_survey_status'] = latest_survey.status
            ctx['pipeline_survey_activity_key'] = _survey_pipeline_activity_key(latest_survey)
            if latest_survey.status == 'completed':
                ctx['pipeline_survey_label'] = 'Survey complete'
            elif latest_survey.status == 'cancelled':
                ctx['pipeline_survey_label'] = 'Survey cancelled'
            else:
                ctx['pipeline_survey_label'] = 'Survey pending'
    except Exception:
        pass

    latest_q = _latest_quotation_for_lead(lead)
    if latest_q:
        ctx['pipeline_has_quotation'] = True
        status = (getattr(latest_q, 'status', None) or 'draft').strip().lower()
        activity_key = _quotation_pipeline_activity_key(latest_q)
        ctx['pipeline_quotation_activity_key'] = activity_key
        ctx['pipeline_quotation_status'] = status
        ctx['pipeline_quotation_no'] = (getattr(latest_q, 'quotation_no', None) or '').strip()
        rev = _quotation_revision_label(latest_q)
        if activity_key == 'revised':
            ctx['pipeline_quotation_label'] = QUOTATION_EVENT_LABELS.get('revised', 'Revised quotation') + rev
        else:
            status_map = {
                'draft': 'Quotation draft',
                'sent': 'Quotation sent',
                'viewed': 'Quotation sent',
                'negotiating': 'Quotation in review',
                'approved': 'Quotation approved',
                'converted': 'Quotation converted',
                'rejected': 'Quotation rejected',
                'expired': 'Quotation expired',
            }
            ctx['pipeline_quotation_label'] = status_map.get(
                status, 'Quotation ' + _status_label(status)
            )
            if rev and status == 'draft':
                ctx['pipeline_quotation_label'] += rev

    return ctx


def resolve_pipeline_dropdown_stage(lead, pipeline_ctx: dict[str, Any]) -> str:
    """
    Which CRM stage the Current Stage dropdown should select:
    Survey while site survey is scheduled/pending; Quotation when a quote exists.
    """
    if lead.stage in ('won', 'lost'):
        return lead.stage
    survey_status = (pipeline_ctx.get('pipeline_survey_status') or '').strip().lower()
    if survey_status in ('scheduled', 'in_progress'):
        return 'survey'
    if pipeline_ctx.get('pipeline_has_quotation'):
        q_key = pipeline_ctx.get('pipeline_quotation_activity_key') or ''
        if q_key not in ('rejected', 'expired', 'cancelled'):
            return 'quote'
    return lead.stage


def build_lead_detail_stage_context(lead, pipeline_ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    """High-level Current Stage dropdown: Survey / Quotation (not granular activity labels)."""
    from apps.leads.models import Lead

    if pipeline_ctx is None:
        pipeline_ctx = build_lead_pipeline_context(lead)

    stage_labels = dict(Lead.STAGE_CHOICES)
    stage_labels['survey'] = 'Survey'
    stage_labels['quote'] = 'Quotation'
    stage_labels['negotiation'] = 'Negotiation'

    stage_choices = [(value, stage_labels.get(value, label)) for value, label in Lead.STAGE_CHOICES]
    dropdown_stage = resolve_pipeline_dropdown_stage(lead, pipeline_ctx)

    display = stage_labels.get(dropdown_stage, lead.get_stage_display())
    badge_class = 'stage-' + dropdown_stage

    return {
        'stage_choices': stage_choices,
        'pipeline_dropdown_stage': dropdown_stage,
        'lead_stage_display': display,
        'lead_stage_badge_class': badge_class,
    }


def _entry_sort_key(entry: dict[str, Any]) -> tuple[float, int]:
    ts = _timeline_sort_key(entry['created'])
    kind_rank = _TIMELINE_KIND_RANK.get(entry.get('kind'), 2)
    return (ts, kind_rank)


def _has_assignment_activity(activities) -> bool:
    return any(a.activity_type == 'assignment' for a in activities)


def _assignment_timeline_created(lead, activities_list) -> datetime:
    """Assignment always sorts after lead created."""
    created_at = _coerce_datetime(lead.created)
    for activity in activities_list:
        if activity.activity_type == 'created':
            created_at = min(created_at, _coerce_datetime(activity.created))
    assigned_at = _coerce_datetime(lead.assigned_date) if lead.assigned_date else None
    if assigned_at and assigned_at > created_at:
        return assigned_at
    return created_at + timedelta(seconds=1)


def _has_lead_created_activity(activities) -> bool:
    for activity in activities:
        if activity.activity_type == 'created':
            return True
        if activity.activity_type == 'note' and 'lead created' in (activity.description or '').lower():
            return True
    return False


def build_lead_timeline(lead, activities) -> list[dict[str, Any]]:
    """Merge assignments, activities, and ERP quotations into one sorted feed."""
    entries: list[dict[str, Any]] = []
    activities_list = list(activities)

    if not _has_lead_created_activity(activities_list):
        creator = lead.assigned_by
        entries.append({
            'kind': 'created',
            'created': _coerce_datetime(lead.created),
            'title': 'Lead Created',
            'description': f'New lead added to CRM.',
            'user': creator,
            'metadata': {},
            'extra_lines': [],
        })

    if lead.assigned_to and not _has_assignment_activity(activities_list):
        entries.append({
            'kind': 'assignment',
            'created': _assignment_timeline_created(lead, activities_list),
            'title': 'Assigned to ' + _user_display(lead.assigned_to),
            'description': '',
            'user': lead.assigned_by,
            'metadata': {},
            'extra_lines': [],
        })

    for activity in activities_list:
        meta = activity.metadata or {}
        extra_lines: list[str] = []
        description = (activity.description or '').strip()
        title = activity.get_activity_type_display()
        if activity.activity_type == 'created':
            title = 'Lead Created'
            if not description:
                description = 'New lead added to CRM.'
        if activity.activity_type == 'assignment':
            title = description or (
                'Assigned to ' + _user_display(lead.assigned_to) if lead.assigned_to else 'Assigned'
            )
            description = ''
        if activity.activity_type == 'followup':
            title = 'Follow Up'
            if meta.get('followup_date'):
                extra_lines.append('New follow up date: ' + str(meta['followup_date']))
            if description:
                extra_lines.append('Notes: ' + description)
                description = ''
        if activity.activity_type == 'call':
            title = 'Call'
            if meta.get('outcome'):
                extra_lines.append('Outcome: ' + str(meta['outcome']).replace('_', ' ').title())
            if meta.get('duration'):
                extra_lines.append('Duration: ' + str(meta['duration']) + ' min')
        if activity.activity_type == 'survey':
            title = description or 'Site Survey'
            description = ''
            status_raw = (meta.get('status') or '').strip()
            if status_raw:
                extra_lines.append('Status: ' + _status_label(status_raw))
        if activity.activity_type == 'quotation':
            title = description or 'Quotation'
            description = ''
            status_raw = (meta.get('status') or '').strip()
            if status_raw:
                extra_lines.append('Status: ' + _status_label(status_raw))

        entries.append({
            'kind': activity.activity_type,
            'created': _coerce_datetime(activity.created),
            'title': title,
            'description': description,
            'user': activity.user,
            'metadata': meta,
            'extra_lines': extra_lines,
        })

    logged_quotation_ids = {
        (a.metadata or {}).get('quotation_id')
        for a in activities_list
        if a.activity_type == 'quotation' and (a.metadata or {}).get('quotation_id')
    }
    logged_survey_ids = {
        (a.metadata or {}).get('survey_id')
        for a in activities_list
        if a.activity_type == 'survey' and (a.metadata or {}).get('survey_id')
    }

    try:
        from apps.surveys.models import Survey

        for survey in Survey.objects.filter(lead_id=lead.pk).select_related('created_by').order_by('-scheduled_date')[:25]:
            if survey.pk in logged_survey_ids:
                continue
            entries.append(_build_survey_timeline_entry(survey))
    except Exception:
        pass

    try:
        from quotation.models import Quotation

        quotations = (
            Quotation.objects.filter(lead_id=lead.pk)
            .select_related('created_by')
            .order_by('-created_at')[:25]
        )
        for q in quotations:
            if q.pk in logged_quotation_ids:
                continue
            q_status = (getattr(q, 'status', '') or 'draft').strip().lower()
            q_no = (getattr(q, 'quotation_no', None) or '').strip()
            suffix = q_no.rsplit('_', 1)[-1] if '_' in q_no else ''
            if suffix.isdigit():
                event = 'revised'
            elif q_status == 'converted':
                event = 'converted'
            elif q_status in ('sent', 'viewed'):
                event = 'sent'
            elif q_status == 'approved':
                event = 'approved'
            elif q_status == 'rejected':
                event = 'rejected'
            else:
                event = 'created'
            entries.append(_build_quotation_timeline_entry(q, event=event))
    except Exception:
        pass

    entries.sort(key=_entry_sort_key, reverse=True)
    for entry in entries:
        style = TIMELINE_STYLES.get(entry['kind'], {'color': '#94a3b8', 'icon': 'fa-circle'})
        entry['icon_color'] = style['color']
        entry['icon_class'] = style['icon']
        entry['user_name'] = _user_display(entry.get('user'))
    return entries
