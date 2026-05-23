from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv
import json

from apps.leads.models import Lead, LeadSource
from apps.leads.forms import pipeline_quotation_filter_assigned_users_queryset
from apps.leads.pipeline_board import build_pipeline_board
from .models import PipelineStage, PipelineHistory

User = get_user_model()


@login_required
def pipeline_view(request):
    """
    Kanban-style pipeline view
    """
    # Get filter parameters
    assigned_to_id = request.GET.get('assigned_to')
    source = request.GET.get('source')
    date_range = request.GET.get('date_range')

    # Base queryset
    leads = Lead.objects.all()

    # Apply filters
    if assigned_to_id:
        leads = leads.filter(assigned_to_id=assigned_to_id)
    if source:
        leads = leads.filter(source_id=source)
    if date_range == 'today':
        leads = leads.filter(created__date=timezone.now().date())
    elif date_range == 'week':
        week_ago = timezone.now().date() - timedelta(days=7)
        leads = leads.filter(created__date__gte=week_ago)
    elif date_range == 'month':
        month_ago = timezone.now().date() - timedelta(days=30)
        leads = leads.filter(created__date__gte=month_ago)

    pipeline_data, pipeline_counts = build_pipeline_board(leads, request.user)

    context = {
        'pipeline_data': pipeline_data,
        'pipeline_counts': pipeline_counts,
        'sales_users': pipeline_quotation_filter_assigned_users_queryset(
            selected_pk=assigned_to_id,
        ),
        'lead_sources': LeadSource.objects.filter(is_active=True),
    }

    return render(request, 'pipeline/pipeline.html', context)



@login_required
def update_lead_stage(request, pk):
    """
    AJAX endpoint to update lead stage via drag and drop
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        lead = get_object_or_404(Lead, pk=pk)
        new_stage = request.POST.get('stage')
        old_stage = lead.stage

        if new_stage and new_stage in dict(Lead.STAGE_CHOICES):
            # Create history record
            PipelineHistory.objects.create(
                lead=lead,
                from_stage=old_stage,
                to_stage=new_stage,
                user=request.user
            )

            # Update lead
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

            return JsonResponse({
                'success': True,
                'message': f'Lead moved to {dict(Lead.STAGE_CHOICES)[new_stage]}'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def pipeline_export(request):
    """
    Export pipeline data to CSV
    """
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pipeline_export_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Lead Name', 'Stage', 'Score', 'Assigned To', 'Value', 'Probability', 'Created Date'])

    leads = Lead.objects.all().select_related('assigned_to')
    for lead in leads:
        writer.writerow([
            lead.name,
            lead.get_stage_display(),
            lead.get_score_display(),
            lead.assigned_to.get_full_name() if lead.assigned_to else 'Unassigned',
            lead.estimated_value or 0,
            lead.probability,
            lead.created.date(),
        ])

    return response