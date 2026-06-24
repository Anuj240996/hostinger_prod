from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.dateparse import parse_datetime
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse, FileResponse
from datetime import timedelta
import csv

from .models import Survey, SurveyImage
from .forms import SurveyForm, SurveyCompletionForm, SurveyImageForm, engineer_users_queryset
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
    """List surveys with filters, search, pagination, and export support."""
    surveys_qs = Survey.objects.all().select_related('lead', 'engineer')

    engineer = request.GET.get('engineer')
    if engineer:
        surveys_qs = surveys_qs.filter(engineer_id=engineer)

    from_date = request.GET.get('from_date')
    if from_date:
        surveys_qs = surveys_qs.filter(scheduled_date__date__gte=from_date)

    to_date = request.GET.get('to_date')
    if to_date:
        surveys_qs = surveys_qs.filter(scheduled_date__date__lte=to_date)

    search_query = (request.GET.get('q') or '').strip()
    if search_query:
        surveys_qs = surveys_qs.filter(
            Q(lead__name__icontains=search_query)
            | Q(lead__phone__icontains=search_query)
            | Q(engineer__first_name__icontains=search_query)
            | Q(engineer__last_name__icontains=search_query)
            | Q(engineer__username__icontains=search_query)
            | Q(status__icontains=search_query)
            | Q(feasibility__icontains=search_query)
            | Q(recommended_size__icontains=search_query)
        ).distinct()

    total_count = surveys_qs.count()
    scheduled_count = surveys_qs.filter(status='scheduled').count()
    in_progress_count = surveys_qs.filter(status='in_progress').count()
    completed_count = surveys_qs.filter(status='completed').count()
    cancelled_count = surveys_qs.filter(status='cancelled').count()

    surveys_for_board = surveys_qs
    status = request.GET.get('status')
    if status:
        surveys_qs = surveys_qs.filter(status=status)

    per_page_raw = (request.GET.get('per_page') or '20').strip().lower()
    if per_page_raw == 'all':
        per_page = max(1, surveys_qs.count())
    else:
        try:
            per_page = int(per_page_raw)
        except (TypeError, ValueError):
            per_page = 20
        if per_page not in (10, 20, 50):
            per_page = 20

    paginator = Paginator(surveys_qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)

    context = {
        'surveys': page_obj.object_list,
        'export_surveys': surveys_qs,
        'page_obj': page_obj,
        'surveys_total_count': total_count,
        'scheduled_count': scheduled_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'engineers': engineer_users_queryset(),
        'board_columns': build_survey_list_board_columns(surveys_for_board),
        'pagination_query': pagination_params.urlencode(),
    }

    return render(request, 'surveys/survey_list.html', context)


@login_required
def survey_detail(request, pk):
    """
    Display detailed view of a survey
    """
    survey = get_object_or_404(
        Survey.objects.select_related('lead', 'engineer', 'created_by').prefetch_related('roof_images'),
        pk=pk,
    )
    from apps.leads.timeline import build_survey_detail_timeline

    completion_form = None
    if survey.status not in ('completed', 'cancelled'):
        completion_form = SurveyCompletionForm(instance=survey)

    context = {
        'survey': survey,
        'survey_timeline_entries': build_survey_detail_timeline(survey),
        'completion_form': completion_form,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }

    return render(request, 'surveys/survey_detail.html', context)


def _survey_report_queryset():
    return Survey.objects.select_related('lead', 'engineer').prefetch_related('roof_images')


def _survey_report_context(request, survey):
    from .report_utils import get_survey_report_branding
    from .structure_diagram_svg import (
        build_structure_diagram_svg_document,
        build_structure_front3d_svg_document,
        structure_measurement_rows,
        build_structure_legend_for_survey,
        structure_diagram_summary_text,
        survey_has_structure_layout,
    )

    branding = get_survey_report_branding(request)
    structure_svg = build_structure_diagram_svg_document(survey) or ''
    structure_front3d_svg = build_structure_front3d_svg_document(survey) or ''
    if structure_svg.startswith('<?xml'):
        structure_svg = structure_svg.split('?>', 1)[-1].strip()
    if structure_front3d_svg.startswith('<?xml'):
        structure_front3d_svg = structure_front3d_svg.split('?>', 1)[-1].strip()
    return {
        'survey': survey,
        'lead': survey.lead,
        'has_structure_layout': survey_has_structure_layout(survey),
        'structure_diagram_svg': structure_svg,
        'structure_front3d_svg': structure_front3d_svg,
        'structure_measurement_rows': structure_measurement_rows(survey),
        'structure_legend_svg': build_structure_legend_for_survey(survey),
        'structure_diagram_summary': structure_diagram_summary_text(survey),
        **branding,
    }


@login_required
def survey_report(request, pk):
    """Print-friendly HTML report for completed surveys."""
    survey = get_object_or_404(_survey_report_queryset(), pk=pk)
    if survey.status != 'completed':
        messages.warning(request, 'Report is only available for completed surveys.')
        return redirect('survey_detail', pk=pk)
    return render(request, 'surveys/survey_report_print.html', _survey_report_context(request, survey))


@login_required
def survey_structure_3d_embed(request, pk):
    """Minimal page used to render the same Three.js front view for PDF capture."""
    survey = get_object_or_404(_survey_report_queryset(), pk=pk)
    if survey.status != 'completed':
        return redirect('survey_detail', pk=pk)
    from .structure_diagram_svg import survey_has_structure_layout

    if not survey_has_structure_layout(survey):
        return redirect('survey_report', pk=pk)
    return render(request, 'surveys/survey_structure_3d_embed.html', {'survey': survey})


@login_required
def survey_report_pdf(request, pk):
    """Downloadable PDF report for completed surveys."""
    import base64

    survey = get_object_or_404(_survey_report_queryset(), pk=pk)
    if survey.status != 'completed':
        messages.warning(request, 'Report is only available for completed surveys.')
        return redirect('survey_detail', pk=pk)

    from .report_utils import build_survey_report_pdf, get_survey_report_branding

    structure_3d_png = None
    if request.method == 'POST':
        data_url = request.POST.get('structure_3d_png', '')
        if data_url.startswith('data:image') and ',' in data_url:
            try:
                structure_3d_png = base64.b64decode(data_url.split(',', 1)[1])
            except (ValueError, TypeError):
                structure_3d_png = None

    try:
        branding = get_survey_report_branding(request)
        buffer = build_survey_report_pdf(survey, branding, structure_3d_png=structure_3d_png)
    except ImportError:
        messages.error(request, 'PDF generation is not available. Please install reportlab.')
        return redirect('survey_report', pk=pk)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'site_survey_{pk}_report.pdf',
        content_type='application/pdf',
    )


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
    """Mark survey complete and save technical fields from the completion modal."""
    survey = get_object_or_404(Survey, pk=pk)

    if request.method != 'POST':
        return redirect('survey_detail', pk=pk)

    if survey.status in ('completed', 'cancelled'):
        messages.warning(request, 'This survey cannot be marked complete again.')
        return redirect('survey_detail', pk=pk)

    form = SurveyCompletionForm(request.POST, request.FILES, instance=survey)
    if not form.is_valid():
        for field, errors in form.errors.items():
            label = form.fields.get(field).label if field in form.fields else field
            for err in errors:
                messages.error(request, f'{label}: {err}')
        return redirect('survey_detail', pk=pk)

    uploaded = getattr(form, 'uploaded_completion_images', None) or request.FILES.getlist('completion_images')
    remove_ids = getattr(form, 'remove_photo_ids', None) or []
    if remove_ids:
        SurveyImage.objects.filter(survey=survey, id__in=remove_ids).delete()

    existing_count = SurveyImage.objects.filter(survey=survey).count()
    if existing_count + len(uploaded) > 3:
        messages.error(request, f'You can upload maximum 3 photos. Already uploaded: {existing_count}.')
        return redirect('survey_detail', pk=pk)

    survey = form.save(commit=False)
    survey.status = 'completed'
    survey.completed_date = timezone.now()
    survey.save()

    # Persist exact site coordinates (captured/applied in completion modal) to Lead.
    lat_raw = (request.POST.get('survey_latitude') or '').strip()
    lng_raw = (request.POST.get('survey_longitude') or '').strip()
    if lat_raw and lng_raw and survey.lead_id:
        try:
            lat = float(lat_raw)
            lng = float(lng_raw)
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                lead_obj = survey.lead
                lead_obj.latitude = round(lat, 6)
                lead_obj.longitude = round(lng, 6)
                lead_obj.save(update_fields=['latitude', 'longitude'])
        except (TypeError, ValueError):
            pass

    saved_photos = 0
    for f in uploaded[: max(0, 3 - existing_count)]:
        SurveyImage.objects.create(survey=survey, image=f)
        saved_photos += 1

    try:
        from apps.leads.timeline import log_survey_timeline_activity
        log_survey_timeline_activity(survey, request.user, event='completed')
    except Exception:
        pass

    sync_lead_stage_for_survey(survey)

    if saved_photos:
        messages.success(request, f'Survey marked as complete! {saved_photos} photo(s) saved.')
    else:
        messages.success(request, 'Survey marked as complete!')
    return _survey_action_redirect(request, pk)


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