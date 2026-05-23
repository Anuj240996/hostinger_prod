from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.dateparse import parse_datetime
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import timedelta
import csv

from .models import Survey, SurveyImage
from .forms import SurveyForm, SurveyImageForm, engineer_users_queryset
from apps.leads.models import Lead

SURVEY_ACTIVE_STATUSES = ('scheduled', 'in_progress')


def sync_lead_stage_for_survey(survey):
    """Keep CRM lead stage aligned with site survey lifecycle."""
    if not survey.lead_id:
        return
    if survey.status in SURVEY_ACTIVE_STATUSES:
        Lead.objects.filter(pk=survey.lead_id).exclude(stage__in=('won', 'lost')).update(stage='survey')
        return
    if survey.status == 'completed':
        try:
            from quotation.models import Quotation

            has_quotation = Quotation.objects.filter(lead_id=survey.lead_id).exists()
        except Exception:
            has_quotation = False
        if has_quotation:
            Lead.objects.filter(pk=survey.lead_id).exclude(stage__in=('won', 'lost')).update(stage='quote')
        else:
            Lead.objects.filter(pk=survey.lead_id).exclude(stage__in=('won', 'lost')).update(stage='survey')
        return
    if survey.status == 'cancelled':
        Lead.objects.filter(pk=survey.lead_id).exclude(stage__in=('won', 'lost')).update(stage='survey')


# Card/board view columns (surveys list Kanban)
SURVEY_LIST_BOARD_COLUMNS = (
    {'key': 'scheduled', 'label': 'Scheduled', 'statuses': ('scheduled',)},
    {'key': 'in_progress', 'label': 'In Progress', 'statuses': ('in_progress',)},
    {'key': 'completed', 'label': 'Completed', 'statuses': ('completed',)},
    {'key': 'cancelled', 'label': 'Cancelled', 'statuses': ('cancelled',)},
)


def build_survey_list_board_columns(surveys_qs):
    """Group filtered surveys into board columns with counts."""
    columns = []
    for col in SURVEY_LIST_BOARD_COLUMNS:
        column_surveys = surveys_qs.filter(status__in=col['statuses']).select_related(
            'lead', 'engineer',
        )
        columns.append({
            'key': col['key'],
            'label': col['label'],
            'count': column_surveys.count(),
            'surveys': list(column_surveys),
        })
    return columns


@login_required
def survey_list(request):
    """
    List all surveys with filters
    """
    surveys = Survey.objects.all().select_related('lead', 'engineer')

    # Apply filters
    status = request.GET.get('status')
    if status:
        surveys = surveys.filter(status=status)

    engineer = request.GET.get('engineer')
    if engineer:
        surveys = surveys.filter(engineer_id=engineer)

    from_date = request.GET.get('from_date')
    if from_date:
        surveys = surveys.filter(scheduled_date__date__gte=from_date)

    to_date = request.GET.get('to_date')
    if to_date:
        surveys = surveys.filter(scheduled_date__date__lte=to_date)

    context = {
        'surveys': surveys,
        'engineers': engineer_users_queryset(),
        'board_columns': build_survey_list_board_columns(surveys),
    }

    return render(request, 'surveys/survey_list.html', context)


@login_required
def survey_detail(request, pk):
    """
    Display detailed view of a survey
    """
    survey = get_object_or_404(
        Survey.objects.select_related('lead', 'engineer', 'created_by'),
        pk=pk,
    )
    from apps.leads.timeline import build_survey_detail_timeline

    context = {
        'survey': survey,
        'survey_timeline_entries': build_survey_detail_timeline(survey),
    }

    return render(request, 'surveys/survey_detail.html', context)


@login_required
def survey_create(request):
    """
    Create a new survey
    """
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.save()
            try:
                from apps.leads.timeline import log_survey_timeline_activity
                event = 'scheduled' if survey.status == 'scheduled' else 'pending'
                log_survey_timeline_activity(survey, request.user, event=event)
            except Exception:
                pass

            sync_lead_stage_for_survey(survey)

            messages.success(request, 'Survey scheduled successfully!')
            return redirect('survey_detail', pk=survey.id)
    else:
        lead_id = request.GET.get('lead')
        initial = {}
        if lead_id:
            initial['lead'] = lead_id
        form = SurveyForm(initial=initial)

    context = {
        'form': form,
        'title': 'Schedule New Survey'
    }

    return render(request, 'surveys/survey_form.html', context)


@login_required
def survey_edit(request, pk):
    """
    Edit an existing survey
    """
    survey = get_object_or_404(Survey, pk=pk)

    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            survey = form.save()
            sync_lead_stage_for_survey(survey)
            messages.success(request, 'Survey updated successfully!')
            return redirect('survey_detail', pk=survey.id)
    else:
        form = SurveyForm(instance=survey)

    context = {
        'form': form,
        'survey': survey,
        'title': f'Edit Survey - {survey.lead.name}'
    }

    return render(request, 'surveys/survey_form.html', context)


def _survey_action_redirect(request, pk):
    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        return redirect(next_url)
    return redirect('survey_detail', pk=pk)


@login_required
def survey_reschedule(request, pk):
    """Reschedule survey date and set status to scheduled."""
    survey = get_object_or_404(Survey, pk=pk)
    if request.method != 'POST':
        return redirect('survey_edit', pk=pk)

    scheduled_raw = request.POST.get('scheduled_date', '').strip()
    if scheduled_raw:
        parsed = parse_datetime(scheduled_raw)
        if parsed is None and 'T' not in scheduled_raw:
            parsed = parse_datetime(scheduled_raw.replace(' ', 'T'))
        if parsed:
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed)
            survey.scheduled_date = parsed

    survey.status = 'scheduled'
    survey.save()
    sync_lead_stage_for_survey(survey)

    try:
        from apps.leads.timeline import log_survey_timeline_activity
        log_survey_timeline_activity(survey, request.user, event='rescheduled')
    except Exception:
        pass

    messages.success(request, 'Survey rescheduled successfully.')
    return _survey_action_redirect(request, pk)


@login_required
def survey_complete(request, pk):
    """
    Mark survey as complete
    """
    if request.method == 'POST':
        survey = get_object_or_404(Survey, pk=pk)
        survey.status = 'completed'
        survey.completed_date = timezone.now()
        survey.save()

        try:
            from apps.leads.timeline import log_survey_timeline_activity
            log_survey_timeline_activity(survey, request.user, event='completed')
        except Exception:
            pass

        sync_lead_stage_for_survey(survey)

        messages.success(request, 'Survey marked as complete!')
        return _survey_action_redirect(request, pk)

    return redirect('survey_detail', pk=pk)


@login_required
def survey_cancel(request, pk):
    """
    Cancel survey
    """
    if request.method == 'POST':
        survey = get_object_or_404(Survey, pk=pk)
        survey.status = 'cancelled'
        survey.save()
        sync_lead_stage_for_survey(survey)

        try:
            from apps.leads.timeline import log_survey_timeline_activity
            log_survey_timeline_activity(survey, request.user, event='cancelled')
        except Exception:
            pass

        messages.info(request, 'Survey cancelled.')
        return _survey_action_redirect(request, pk)

    return redirect('survey_detail', pk=pk)


@login_required
def upload_survey_image(request, pk):
    """
    Upload images for survey
    """
    survey = get_object_or_404(Survey, pk=pk)

    if request.method == 'POST' and request.FILES.get('image'):
        image = SurveyImage(
            survey=survey,
            image=request.FILES['image'],
            caption=request.POST.get('caption', ''),
            is_primary=request.POST.get('is_primary') == 'on'
        )
        image.save()

        # If this is primary, unset other primary images
        if image.is_primary:
            SurveyImage.objects.filter(survey=survey).exclude(pk=image.pk).update(is_primary=False)

        return JsonResponse({'success': True, 'image_id': image.id})

    return JsonResponse({'success': False}, status=400)


@login_required
def survey_export(request):
    """
    Export surveys to CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="surveys_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['Lead Name', 'Engineer', 'Scheduled Date', 'Status', 'Feasibility', 'System Size', 'Completed Date'])

    surveys = Survey.objects.all().select_related('lead', 'engineer')
    for survey in surveys:
        writer.writerow([
            survey.lead.name,
            survey.engineer.get_full_name() if survey.engineer else 'Unassigned',
            survey.scheduled_date.strftime('%Y-%m-%d %H:%M'),
            survey.get_status_display(),
            survey.get_feasibility_display() if survey.feasibility else '',
            survey.recommended_size,
            survey.completed_date.strftime('%Y-%m-%d') if survey.completed_date else '',
        ])

    return response