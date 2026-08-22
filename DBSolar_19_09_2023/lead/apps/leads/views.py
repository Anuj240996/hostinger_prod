from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Prefetch
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
import csv

from apps.surveys.models import Survey
from .models import Lead, LeadActivity, FollowUp, LeadSource
from .forms import LeadForm, LeadActivityForm, lead_list_filter_sales_users_queryset
from .timeline import (
    build_lead_detail_stage_context,
    build_lead_pipeline_context,
    build_lead_timeline,
    lead_has_converted_estimate,
    resolve_pipeline_dropdown_stage,
)

User = get_user_model()

# Card/board view columns (leads list Kanban)
LEAD_LIST_BOARD_COLUMNS = (
    {'key': 'new', 'label': 'New Lead', 'stages': ('new', 'qualified')},
    {'key': 'survey', 'label': 'Survey Pending', 'stages': ('survey',)},
    {'key': 'quote', 'label': 'Sent Quotation', 'stages': ('quote', 'negotiation')},
    {'key': 'won', 'label': 'Won', 'stages': ('won',)},
    {'key': 'lost', 'label': 'Lost', 'stages': ('lost',)},
)
LEAD_LIST_BOARD_PRICE_COLUMNS = frozenset({'quote', 'won', 'lost'})
SURVEY_ACTIVE_STATUSES = ('scheduled', 'in_progress')


def leads_queryset_with_surveys(qs):
    """Prefetch latest surveys per lead for list/board status labels."""
    return qs.prefetch_related(
        Prefetch(
            'surveys',
            queryset=Survey.objects.order_by('-scheduled_date', '-created'),
        )
    ).select_related('assigned_to')


def _latest_survey_for_lead(lead):
    prefetched = getattr(lead, '_prefetched_objects_cache', {}).get('surveys')
    if prefetched is not None:
        return prefetched[0] if prefetched else None
    return None


def _latest_survey_by_lead_id(lead_ids):
    latest = {}
    if not lead_ids:
        return latest
    for survey in Survey.objects.filter(lead_id__in=lead_ids).order_by(
        'lead_id', '-scheduled_date', '-created'
    ):
        if survey.lead_id not in latest:
            latest[survey.lead_id] = survey
    return latest


def _pending_survey_lead_ids(leads_qs):
    return set(
        Survey.objects.filter(
            lead_id__in=leads_qs.values_list('pk', flat=True),
            status__in=SURVEY_ACTIVE_STATUSES,
        ).values_list('lead_id', flat=True)
    )


SURVEY_LIST_STATUS_DISPLAY = {
    'scheduled': ('Survey scheduled', 'lead-status-survey-scheduled'),
    'in_progress': ('Survey pending', 'lead-status-survey-pending'),
    'completed': ('Survey completed', 'lead-status-survey-completed'),
    'cancelled': ('Cancel survey', 'lead-status-survey-cancelled'),
}

# Pipeline column key -> leads list Kanban column key
LEAD_LIST_COLUMN_FROM_PIPELINE = {
    'new': 'new',
    'qualified': 'new',
    'survey': 'survey',
    'quote': 'quote',
    'negotiation': 'quote',
    'won': 'won',
    'lost': 'lost',
}


def _normalize_lead_list_badge_class(badge_class: str) -> str:
    """Map pipeline badge classes to list CSS (stage-* / lead-status-* with styles)."""
    if not badge_class:
        return 'stage-new'
    badge_class = badge_class.replace('pipeline-badge-', 'lead-status-')
    if badge_class.startswith('lead-status-stage-'):
        return badge_class.replace('lead-status-stage-', 'stage-')
    return badge_class


def _apply_lead_list_status_label(lead, survey=None, quotation=None):
    if quotation:
        from apps.leads.pipeline_board import resolve_pipeline_column_for_lead

        _, label, badge = resolve_pipeline_column_for_lead(lead, survey, quotation)
        lead.list_status_label = label or lead.get_stage_display() or 'New Lead'
        lead.list_status_badge_class = _normalize_lead_list_badge_class(badge)
        return
    if survey and survey.status in SURVEY_LIST_STATUS_DISPLAY:
        lead.list_status_label, lead.list_status_badge_class = SURVEY_LIST_STATUS_DISPLAY[survey.status]
    elif lead.stage == 'survey':
        lead.list_status_label = 'Survey pending'
        lead.list_status_badge_class = 'lead-status-survey-pending'
    else:
        stage = (lead.stage or 'new').strip() or 'new'
        lead.list_status_label = lead.get_stage_display() or 'New Lead'
        lead.list_status_badge_class = 'stage-' + stage


def attach_lead_list_status_labels(leads, quotation_map=None):
    """Survey- and quotation-aware status labels for leads list table and cards."""
    lead_list = list(leads)
    if not lead_list:
        return lead_list

    lead_ids = [lead.pk for lead in lead_list]
    if quotation_map is None:
        from apps.leads.pipeline_board import _latest_quotation_map_all_leads

        quotation_map = _latest_quotation_map_all_leads(lead_ids)

    fallback_survey_map = _latest_survey_by_lead_id(
        [lead.pk for lead in lead_list if _latest_survey_for_lead(lead) is None]
    )
    for lead in lead_list:
        survey = _latest_survey_for_lead(lead) or fallback_survey_map.get(lead.pk)
        quotation = quotation_map.get(lead.pk)
        _apply_lead_list_status_label(lead, survey, quotation)
    return lead_list


QUOTE_SENT_APPROVED_LABELS = frozenset({'Sent', 'Approved'})


def _quote_sent_approved_lead_ids(leads_qs):
    """Lead IDs whose latest quotation shows Sent or Approved in the list/pipeline."""
    from apps.leads.pipeline_board import (
        _latest_quotation_map_all_leads,
        resolve_pipeline_column_for_lead,
    )

    leads = list(leads_queryset_with_surveys(leads_qs))
    if not leads:
        return set()

    lead_ids = [lead.pk for lead in leads]
    survey_map = _latest_survey_by_lead_id(
        [lead.pk for lead in leads if _latest_survey_for_lead(lead) is None]
    )
    quote_map = _latest_quotation_map_all_leads(lead_ids)

    matching = set()
    for lead in leads:
        quotation = quote_map.get(lead.pk)
        if not quotation:
            continue
        survey = _latest_survey_for_lead(lead) or survey_map.get(lead.pk)
        _, label, _ = resolve_pipeline_column_for_lead(lead, survey, quotation)
        if (label or '').strip() in QUOTE_SENT_APPROVED_LABELS:
            matching.add(lead.pk)
    return matching


def _filter_leads_quote_sent_approved(leads_qs):
    """Filter queryset to leads with Sent or Approved quotation status."""
    matching_ids = _quote_sent_approved_lead_ids(leads_qs)
    if not matching_ids:
        return leads_qs.none()
    return leads_qs.filter(pk__in=matching_ids)


def _erp_quotation_sort_key(quotation):
    """Latest revision first — same quote# ordering as CRM quotation list."""
    no = (getattr(quotation, 'quotation_no', None) or '').strip()
    if not no:
        return (0, 0, getattr(quotation, 'pk', None) or 0)
    parts = no.split('_')
    try:
        base = int(parts[0])
    except (ValueError, TypeError):
        base = 0
    try:
        rev = int(parts[1]) if len(parts) > 1 else 0
    except (ValueError, TypeError):
        rev = 0
    return (base, rev, getattr(quotation, 'pk', None) or 0)


def _latest_erp_quotation_prices_by_lead(lead_ids, user):
    """
    Map lead id -> total from ERP quotation table (quotation_quotation.final_amount).
    Uses the latest quote revision per lead, scoped like /new-lead/quotations/.
    """
    if not lead_ids:
        return {}
    from customer.staff_access import quotation_queryset_for_request

    quotations = quotation_queryset_for_request(user).filter(
        lead_id__in=lead_ids,
    ).only('lead_id', 'final_amount', 'net_amount', 'quotation_no', 'pk')

    latest_by_lead = {}
    for quote in quotations:
        lead_id = quote.lead_id
        if lead_id not in latest_by_lead:
            latest_by_lead[lead_id] = quote
            continue
        if _erp_quotation_sort_key(quote) > _erp_quotation_sort_key(latest_by_lead[lead_id]):
            latest_by_lead[lead_id] = quote

    prices = {}
    for lead_id, quote in latest_by_lead.items():
        amount = quote.final_amount or quote.net_amount
        prices[lead_id] = amount if amount is not None else None
    return prices


def attach_erp_quotation_display_to_leads(leads, user):
    """Attach pipeline_quotation_amount / pipeline_quotation_display from ERP quotations."""
    from apps.core.templatetags.indian_numbers import format_indian_card_price_display

    lead_list = list(leads)
    if not lead_list:
        return lead_list

    price_map = _latest_erp_quotation_prices_by_lead([lead.pk for lead in lead_list], user)
    for lead in lead_list:
        amount = price_map.get(lead.pk)
        lead.pipeline_quotation_amount = amount
        lead.pipeline_quotation_display = format_indian_card_price_display(amount)
    return lead_list


def build_lead_list_board_columns(leads_qs, user=None):
    """Group filtered leads into board columns (survey + quotation rules, not stage alone)."""
    from apps.leads.pipeline_board import (
        _latest_quotation_map_all_leads,
        resolve_pipeline_column_for_lead,
    )

    all_leads = list(leads_qs.order_by('-created'))
    lead_ids = [lead.pk for lead in all_leads]
    survey_map = _latest_survey_by_lead_id(lead_ids)
    quotation_map = _latest_quotation_map_all_leads(lead_ids)

    buckets = {col['key']: [] for col in LEAD_LIST_BOARD_COLUMNS}
    for lead in all_leads:
        pipeline_col, _, _ = resolve_pipeline_column_for_lead(
            lead,
            survey_map.get(lead.pk),
            quotation_map.get(lead.pk),
        )
        list_col = LEAD_LIST_COLUMN_FROM_PIPELINE.get(pipeline_col, 'new')
        buckets[list_col].append(lead)

    attach_lead_list_status_labels(all_leads, quotation_map=quotation_map)

    columns = []
    price_lead_ids = []
    for col in LEAD_LIST_BOARD_COLUMNS:
        leads_list = buckets[col['key']]
        show_price = col['key'] in LEAD_LIST_BOARD_PRICE_COLUMNS
        if show_price:
            price_lead_ids.extend(lead.pk for lead in leads_list)
        columns.append({
            'key': col['key'],
            'label': col['label'],
            'stages': col['stages'],
            'count': len(leads_list),
            'show_quotation_price': show_price,
            'leads': leads_list,
        })

    from apps.core.templatetags.indian_numbers import format_indian_card_price_display

    price_map = _latest_erp_quotation_prices_by_lead(set(price_lead_ids), user)
    for col in columns:
        if not col['show_quotation_price']:
            continue
        for lead in col['leads']:
            amount = price_map.get(lead.pk)
            lead.board_quotation_price = amount
            lead.board_quotation_price_display = format_indian_card_price_display(amount)

    return columns


def _lead_list_kpi_url(request, stage=None):
    """KPI card link preserving active sidebar/search filters."""
    params = request.GET.copy()
    params.pop('page', None)
    if stage:
        params['stage'] = stage
    else:
        params.pop('stage', None)
    qs = params.urlencode()
    from django.urls import reverse
    return reverse('lead_list') + ('?' + qs if qs else '')


@login_required
def lead_list(request):
    """List leads with filters, search, pagination, and export support."""
    from apps.leads.pipeline_board import _latest_quotation_map_all_leads

    leads_qs = Lead.objects.all().select_related('assigned_to', 'source')

    search_query = (request.GET.get('q') or request.GET.get('search') or '').strip()
    if search_query:
        leads_qs = leads_qs.filter(
            Q(name__icontains=search_query)
            | Q(phone__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(address__icontains=search_query)
            | Q(city__icontains=search_query)
        ).distinct()

    if request.GET.get('score'):
        leads_qs = leads_qs.filter(score=request.GET.get('score'))
    if request.GET.get('assigned_to'):
        leads_qs = leads_qs.filter(assigned_to_id=request.GET.get('assigned_to'))
    if request.GET.get('source'):
        leads_qs = leads_qs.filter(source_id=request.GET.get('source'))
    if request.GET.get('city'):
        leads_qs = leads_qs.filter(city__icontains=request.GET.get('city'))

    date_range = request.GET.get('date_range')
    today = timezone.now().date()
    if date_range == 'today':
        leads_qs = leads_qs.filter(created__date=today)
    elif date_range == 'yesterday':
        yesterday = today - timedelta(days=1)
        leads_qs = leads_qs.filter(created__date=yesterday)
    elif date_range == 'this_week':
        start = today - timedelta(days=today.weekday())
        leads_qs = leads_qs.filter(created__date__gte=start)
    elif date_range == 'this_month':
        leads_qs = leads_qs.filter(created__month=today.month, created__year=today.year)

    followup = request.GET.get('followup')
    if followup == 'due_today':
        leads_qs = leads_qs.filter(next_followup__date=today)
    elif followup == 'overdue':
        leads_qs = leads_qs.filter(next_followup__date__lt=today)

    total_count = leads_qs.count()
    new_count = leads_qs.filter(stage__in=('new', 'qualified')).count()
    survey_count = leads_qs.filter(stage='survey').count()
    quote_count = len(_quote_sent_approved_lead_ids(leads_qs))
    won_count = leads_qs.filter(stage='won').count()
    lost_count = leads_qs.filter(stage='lost').count()

    stage_filter = request.GET.get('stage')
    if stage_filter == 'survey_pending':
        pending_ids = _pending_survey_lead_ids(leads_qs)
        leads_qs = leads_qs.filter(Q(stage='survey') | Q(pk__in=pending_ids)).distinct()
    elif stage_filter == 'quote':
        leads_qs = _filter_leads_quote_sent_approved(leads_qs)
    elif stage_filter == 'new':
        leads_qs = leads_qs.filter(stage__in=('new', 'qualified'))
    elif stage_filter:
        leads_qs = leads_qs.filter(stage=stage_filter)

    board_leads_count = leads_qs.count()

    order_by = request.GET.get('order_by', '-created')
    leads_qs = leads_qs.order_by(order_by)
    leads_qs = leads_queryset_with_surveys(leads_qs)

    per_page_raw = (request.GET.get('per_page') or '20').strip().lower()
    if per_page_raw == 'all':
        per_page = max(1, leads_qs.count())
    else:
        try:
            per_page = int(per_page_raw)
        except (TypeError, ValueError):
            per_page = 20
        if per_page not in (10, 20, 50):
            per_page = 20

    paginator = Paginator(leads_qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    leads_page = page_obj.object_list

    quote_map = _latest_quotation_map_all_leads([lead.pk for lead in leads_page])
    attach_lead_list_status_labels(leads_page, quotation_map=quote_map)

    export_leads = list(leads_qs)
    export_quote_map = _latest_quotation_map_all_leads([lead.pk for lead in export_leads])
    attach_lead_list_status_labels(export_leads, quotation_map=export_quote_map)

    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)

    context = {
        'leads': leads_page,
        'export_leads': export_leads,
        'search_query': search_query,
        'page_obj': page_obj,
        'leads_total_count': total_count,
        'new_count': new_count,
        'survey_count': survey_count,
        'quote_count': quote_count,
        'won_count': won_count,
        'lost_count': lost_count,
        'board_columns': build_lead_list_board_columns(leads_qs, request.user),
        'board_leads_count': board_leads_count,
        'stage_filter': stage_filter or '',
        'kpi_url_total': _lead_list_kpi_url(request),
        'kpi_url_new': _lead_list_kpi_url(request, 'new'),
        'kpi_url_survey': _lead_list_kpi_url(request, 'survey'),
        'kpi_url_quote': _lead_list_kpi_url(request, 'quote'),
        'kpi_url_won': _lead_list_kpi_url(request, 'won'),
        'kpi_url_lost': _lead_list_kpi_url(request, 'lost'),
        'sales_users': lead_list_filter_sales_users_queryset(),
        'lead_sources': LeadSource.objects.filter(is_active=True),
        'stage_choices': list(Lead.STAGE_CHOICES) + [('survey_pending', 'Survey Pending')],
        'pagination_query': pagination_params.urlencode(),
        'now': timezone.now(),
    }

    return render(request, 'leads/lead_list.html', context)


@login_required
def lead_detail(request, pk):
    """
    Display detailed view of a single lead
    """
    lead = get_object_or_404(
        leads_queryset_with_surveys(
            Lead.objects.select_related('assigned_to', 'assigned_by', 'source', 'campaign')
        ),
        pk=pk,
    )
    activities = lead.activities.all().select_related('user').order_by('-created')[:50]
    followups = lead.followups.all()
    timeline_entries = build_lead_timeline(lead, activities)
    lead_is_locked = lead_has_converted_estimate(lead)

    context = {
        'lead': lead,
        'activities': activities,
        'timeline_entries': timeline_entries,
        'followups': followups,
        'lead_is_locked': lead_is_locked,
    }
    pipeline_ctx = build_lead_pipeline_context(lead)
    if not lead_is_locked:
        dropdown_stage = resolve_pipeline_dropdown_stage(lead, pipeline_ctx)
        if dropdown_stage != lead.stage and dropdown_stage in dict(Lead.STAGE_CHOICES):
            lead.stage = dropdown_stage
            lead.save(update_fields=['stage'])
    context.update(pipeline_ctx)
    context.update(build_lead_detail_stage_context(lead, pipeline_ctx))

    return render(request, 'new_lead/leads/lead_detail.html', context)

#
# @login_required
# def lead_create(request):
#     """
#     Create a new lead
#     """
#     if request.method == 'POST':
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             lead = form.save(commit=False)
#             lead.assigned_by = request.user
#             lead.save()
#
#             # Create activity
#             LeadActivity.objects.create(
#                 lead=lead,
#                 user=request.user,
#                 activity_type='note',
#                 description=f'Lead created by {request.user.get_full_name()}'
#             )
#
#             messages.success(request, 'Lead created successfully!')
#             return redirect('lead_detail', pk=lead.id)
#     else:
#         form = LeadForm()
#
#     context = {
#         'form': form,
#         'title': 'Create New Lead'
#     }
#
#     return render(request, 'leads/lead_form.html', context)


@login_required
def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST, organization=request.organization)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.organization = request.organization
            assignee = lead.assigned_to
            # Save lead first without assignment so timeline order is: Created → Assigned
            lead.assigned_to = None
            lead.assigned_by = None
            lead.assigned_date = None
            lead.save()

            creator_name = (request.user.get_full_name() or '').strip() or request.user.username
            LeadActivity.objects.create(
                lead=lead,
                user=request.user,
                activity_type='created',
                description=f'Lead created by {creator_name}',
            )

            if assignee:
                lead.assigned_to = assignee
                lead.assigned_by = request.user
                lead.assigned_date = timezone.now()
                lead.save(update_fields=['assigned_to', 'assigned_by', 'assigned_date'])
                assignee_name = (assignee.get_full_name() or '').strip() or assignee.username
                LeadActivity.objects.create(
                    lead=lead,
                    user=request.user,
                    activity_type='assignment',
                    description=f'Assigned to {assignee_name}',
                )

            messages.success(request, 'Lead created successfully!')
            return redirect(f'/new-lead/leads/{lead.id}/')
    else:
        form = LeadForm(organization=request.organization)

    context = {
        'form': form,
        'title': 'Create New Lead'
    }
    return render(request, 'leads/lead_form.html', context)

#
# @login_required
# def lead_edit(request, pk):
#     """
#     Edit an existing lead
#     """
#     lead = get_object_or_404(Lead, pk=pk)
#
#     if request.method == 'POST':
#         form = LeadForm(request.POST, instance=lead)
#         if form.is_valid():
#             form.save()
#
#             messages.success(request, 'Lead updated successfully!')
#             return redirect('lead_detail', pk=lead.id)
#     else:
#         form = LeadForm(instance=lead)
#
#     context = {
#         'form': form,
#         'lead': lead,
#         'title': f'Edit Lead: {lead.name}'
#     }
#
#     return render(request, 'leads/lead_form.html', context)

@login_required
def lead_edit(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=request.organization)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead, organization=request.organization)
        if form.is_valid():
            form.save()
            from quotation.conversion_utils import sync_quotation_consumer_names_for_lead

            sync_quotation_consumer_names_for_lead(lead)
            messages.success(request, 'Lead updated successfully!')
            return redirect(f'/new-lead/leads/{lead.id}/')
    else:
        form = LeadForm(instance=lead, organization=request.organization)

    context = {
        'form': form,
        'lead': lead,
        'title': f'Edit Lead: {lead.name}'
    }
    return render(request, 'leads/lead_form.html', context)


@login_required
def lead_update_stage(request, pk):
    """
    Update lead stage
    """
    if request.method == 'POST':
        lead = get_object_or_404(Lead, pk=pk)
        if lead_has_converted_estimate(lead):
            messages.warning(request, 'Pipeline stage cannot be changed after an estimate is converted.')
            return redirect(f'/new-lead/leads/{lead.id}/')
        old_stage = lead.stage
        new_stage = request.POST.get('stage')

        if new_stage and new_stage in dict(Lead.STAGE_CHOICES):
            lead.stage = new_stage

            # Update probability based on stage
            stage_probabilities = {
                'new': 10,
                'qualified': 30,
                'survey': 50,
                'quote': 70,
                'negotiation': 85,
                'won': 100,
                'lost': 0,
            }
            lead.probability = stage_probabilities.get(new_stage, 0)

            if new_stage == 'won':
                lead.converted_at = timezone.now()
            elif new_stage == 'lost':
                lead.lost_at = timezone.now()

            lead.save()

            # Log activity
            LeadActivity.objects.create(
                lead=lead,
                user=request.user,
                activity_type='stage_change',
                description=f'Stage changed from {dict(Lead.STAGE_CHOICES)[old_stage]} to {dict(Lead.STAGE_CHOICES)[new_stage]}'
            )

            messages.success(request, f'Lead stage updated to {dict(Lead.STAGE_CHOICES)[new_stage]}')

    return redirect(f'/new-lead/leads/{lead.id}/')


@login_required
def lead_mark_lost(request, pk):
    """
    Mark a lead as lost with reason
    """
    if request.method == 'POST':
        lead = get_object_or_404(Lead, pk=pk)
        lead.stage = 'lost'
        lead.lost_reason = request.POST.get('lost_reason')
        lead.competitor = request.POST.get('competitor')
        lead.notes = request.POST.get('notes')
        lead.lost_at = timezone.now()
        lead.probability = 0
        lead.save()

        # Log activity
        LeadActivity.objects.create(
            lead=lead,
            user=request.user,
            activity_type='note',
            description=f'Lead marked as lost. Reason: {lead.lost_reason}'
        )

        messages.info(request, 'Lead marked as lost')

    return redirect(f'/new-lead/leads/{lead.id}/')


@login_required
def lead_add_activity(request, pk):
    """
    Add an activity to a lead
    """
    if request.method == 'POST':
        lead = get_object_or_404(Lead, pk=pk)
        if lead_has_converted_estimate(lead):
            messages.warning(request, 'Cannot add activities after an estimate is converted.')
            return redirect(f'/new-lead/leads/{lead.id}/')

        activity_type = request.POST.get('activity_type')
        description = request.POST.get('description')

        metadata = {}
        if activity_type == 'call':
            metadata = {
                'duration': request.POST.get('duration'),
                'outcome': request.POST.get('outcome'),
            }
        elif activity_type == 'followup':
            followup_date = (request.POST.get('followup_date') or '').strip()
            if followup_date:
                parsed_followup = None
                for fmt in (
                    '%Y-%m-%dT%H:%M',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%Y-%m-%d %H:%M:%S',
                    '%d/%m/%Y %I:%M %p',
                    '%d/%m/%Y %I:%M%p',
                    '%d/%m/%Y %H:%M',
                ):
                    try:
                        from datetime import datetime
                        parsed_followup = datetime.strptime(followup_date, fmt)
                        if timezone.is_naive(parsed_followup):
                            parsed_followup = timezone.make_aware(
                                parsed_followup, timezone.get_current_timezone()
                            )
                        break
                    except ValueError:
                        continue
                if parsed_followup:
                    metadata['followup_date'] = followup_date
                    lead.next_followup = parsed_followup
                    lead.save(update_fields=['next_followup'])

                    # Create follow-up record
                    FollowUp.objects.create(
                        lead=lead,
                        user=request.user,
                        scheduled_date=parsed_followup,
                        notes=description
                    )

        # Create activity
        LeadActivity.objects.create(
            lead=lead,
            user=request.user,
            activity_type=activity_type,
            description=description,
            metadata=metadata
        )

        # Update last contacted
        lead.last_contacted = timezone.now()
        lead.save()

        messages.success(request, 'Activity added successfully!')

    return redirect(f'/new-lead/leads/{lead.id}/')


@login_required
def lead_export(request):
    """
    Export leads to CSV
    """
    leads = Lead.objects.all()

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="leads_export_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['Name', 'Phone', 'Email', 'City', 'Stage', 'Score', 'Assigned To', 'Created Date', 'Value']
    )

    for lead in leads:
        writer.writerow([
            lead.name,
            lead.phone,
            lead.email,
            lead.city,
            lead.get_stage_display(),
            lead.get_score_display(),
            lead.assigned_to.get_full_name() if lead.assigned_to else '',
            lead.created.date(),
            lead.estimated_value or 0,
        ])

    return response