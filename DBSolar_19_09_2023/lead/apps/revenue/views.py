# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.db.models import Sum, Count, Avg
# from django.utils import timezone
# from django.http import JsonResponse, HttpResponse
# from datetime import datetime, timedelta
# import csv
# import json
# from calendar import monthrange
#
# from .models import Revenue, RevenueTarget
# from .forms import RevenueForm, RevenueTargetForm
# from apps.leads.models import Lead
# from django.contrib.auth.models import User
#
#
# @login_required
# def revenue_dashboard(request):
#     """
#     Revenue dashboard with KPIs and charts
#     """
#     today = timezone.now().date()
#     first_day_month = today.replace(day=1)
#     last_day_month = today.replace(day=monthrange(today.year, today.month)[1])
#
#     # Revenue by month
#     months = []
#     revenue_data = []
#     for i in range(6):
#         month = today.replace(day=1) - timedelta(days=30 * i)
#         month_start = month.replace(day=1)
#         month_end = month.replace(day=monthrange(month.year, month.month)[1])
#
#         months.append(month.strftime('%b %Y'))
#         month_revenue = Revenue.objects.filter(
#             date__gte=month_start,
#             date__lte=month_end,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#         revenue_data.append(float(month_revenue))
#
#     # Revenue by sales person
#     sales_revenue = []
#     sales_labels = []
#     sales_users = User.objects.filter(groups__name='Sales')
#     for user in sales_users:
#         total = Revenue.objects.filter(
#             lead__assigned_to=user,
#             date__gte=first_day_month,
#             date__lte=last_day_month,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#         if total > 0:
#             sales_revenue.append(float(total))
#             sales_labels.append(user.get_full_name() or user.username)
#
#     # Revenue by source
#     source_revenue = []
#     source_labels = []
#     from apps.leads.models import LeadSource
#     for source in LeadSource.objects.all():
#         total = Revenue.objects.filter(
#             lead__source=source,
#             date__gte=first_day_month,
#             date__lte=last_day_month,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#         if total > 0:
#             source_revenue.append(float(total))
#             source_labels.append(source.name)
#
#     # Recent deals
#     recent_deals = Revenue.objects.filter(
#         payment_status='paid'
#     ).select_related('lead', 'lead__assigned_to').order_by('-date')[:10]
#
#     # KPIs
#     total_revenue = Revenue.objects.filter(
#         date__gte=first_day_month,
#         date__lte=last_day_month,
#         payment_status='paid'
#     ).aggregate(total=Sum('amount'))['total'] or 0
#
#     pending_revenue = Revenue.objects.filter(
#         payment_status__in=['pending', 'partial']
#     ).aggregate(total=Sum('amount'))['total'] or 0
#
#     avg_deal_size = Revenue.objects.filter(
#         payment_status='paid'
#     ).aggregate(avg=Avg('amount'))['avg'] or 0
#
#     # Forecast (next 3 months)
#     forecast = 0
#     for i in range(1, 4):
#         month = today.replace(day=1) + timedelta(days=32 * i)
#         month = month.replace(day=1)
#
#         # Add quotations expected to close
#         from apps.quotations.models import Quotation
#         forecast += Quotation.objects.filter(
#             status='approved',
#             approval_date__year=month.year,
#             approval_date__month=month.month
#         ).aggregate(total=Sum('total_cost'))['total'] or 0
#
#     context = {
#         'total_revenue': total_revenue,
#         'pending_revenue': pending_revenue,
#         'forecast_revenue': forecast,
#         'avg_deal_size': avg_deal_size,
#         'recent_deals': recent_deals,
#         'revenue_months': json.dumps(months[::-1]),
#         'revenue_data': json.dumps(revenue_data[::-1]),
#         'sales_labels': json.dumps(sales_labels),
#         'sales_data': json.dumps(sales_revenue),
#         'source_labels': json.dumps(source_labels),
#         'source_data': json.dumps(source_revenue),
#     }
#
#     return render(request, 'revenue/revenue.html', context)
#
#
# @login_required
# def add_revenue(request):
#     """
#     Add revenue record
#     """
#     if request.method == 'POST':
#         form = RevenueForm(request.POST)
#         if form.is_valid():
#             revenue = form.save()
#
#             # Update lead
#             revenue.lead.stage = 'won'
#             revenue.lead.converted_at = revenue.date
#             revenue.lead.save()
#
#             messages.success(request, 'Revenue recorded successfully!')
#             return redirect('revenue_dashboard')
#     else:
#         lead_id = request.GET.get('lead')
#         initial = {}
#         if lead_id:
#             initial['lead'] = lead_id
#         form = RevenueForm(initial=initial)
#
#     context = {
#         'form': form,
#         'title': 'Record Revenue'
#     }
#
#     return render(request, 'revenue/revenue_form.html', context)
#
#
# @login_required
# def revenue_export(request):
#     """
#     Export revenue data to CSV
#     """
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="revenue_{timezone.now().date()}.csv"'
#
#     writer = csv.writer(response)
#     writer.writerow(['Lead', 'Amount', 'Date', 'Payment Status', 'Payment Method', 'Transaction ID'])
#
#     revenues = Revenue.objects.all().select_related('lead')
#     for rev in revenues:
#         writer.writerow([
#             rev.lead.name,
#             rev.amount,
#             rev.date.strftime('%Y-%m-%d'),
#             rev.get_payment_status_display(),
#             rev.payment_method,
#             rev.transaction_id,
#         ])
#
#     return response
#
# @login_required
# def mark_revenue_paid(request, pk):
#     revenue = get_object_or_404(Revenue, pk=pk)
#     if request.method == 'POST':
#         revenue.payment_status = 'paid'
#         revenue.save()
#         messages.success(request, 'Revenue marked as paid.')
#     return redirect('revenue')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
import csv
import json
from calendar import monthrange

from .models import Revenue, RevenueTarget
from .forms import RevenueForm, RevenueTargetForm
from apps.leads.models import Lead
from django.contrib.auth.models import User
#
# @login_required
# def revenue_dashboard(request):
#     """
#     Revenue dashboard with KPIs and charts
#     """
#     today = timezone.now().date()
#     first_day_month = today.replace(day=1)
#     last_day_month = today.replace(day=monthrange(today.year, today.month)[1])
#
#     # Revenue by month (last 6 months)
#     months = []
#     revenue_data = []
#     for i in range(6):
#         month = today.replace(day=1) - timedelta(days=30 * i)
#         month_start = month.replace(day=1)
#         month_end = month.replace(day=monthrange(month.year, month.month)[1])
#
#         months.append(month.strftime('%b %Y'))
#         month_revenue = Revenue.objects.filter(
#             date__gte=month_start,
#             date__lte=month_end,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#         revenue_data.append(float(month_revenue))
#
#     # Revenue by sales person (this month, paid)
#     sales_revenue = []
#     sales_labels = []
#     sales_users = User.objects.filter(groups__name='Sales')
#     for user in sales_users:
#         total = Revenue.objects.filter(
#             lead__assigned_to=user,
#             date__gte=first_day_month,
#             date__lte=last_day_month,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#         if total > 0:
#             sales_revenue.append(float(total))
#             sales_labels.append(user.get_full_name() or user.username)
#
#     # Revenue by source (this month, paid)
#     source_revenue = []
#     source_labels = []
#     from apps.leads.models import LeadSource
#     for source in LeadSource.objects.all():
#         total = Revenue.objects.filter(
#             lead__source=source,
#             date__gte=first_day_month,
#             date__lte=last_day_month,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#         if total > 0:
#             source_revenue.append(float(total))
#             source_labels.append(source.name)
#
#     # Recent deals (include both paid and pending)
#     recent_deals = Revenue.objects.all().select_related('lead', 'lead__assigned_to').order_by('-date')[:10]
#
#     # KPIs
#     total_revenue = Revenue.objects.filter(
#         date__gte=first_day_month,
#         date__lte=last_day_month,
#         payment_status='paid'
#     ).aggregate(total=Sum('amount'))['total'] or 0
#
#     pending_revenue = Revenue.objects.filter(
#         payment_status__in=['pending', 'partial']
#     ).aggregate(total=Sum('amount'))['total'] or 0
#
#     avg_deal_size = Revenue.objects.filter(
#         payment_status='paid'
#     ).aggregate(avg=Avg('amount'))['avg'] or 0
#
#     # Counts for KPI cards
#     closed_deals = Revenue.objects.filter(payment_status='paid').count()
#     pending_deals = Revenue.objects.filter(payment_status__in=['pending', 'partial']).count()
#
#     # Forecast (next 3 months) based on approved quotations
#     forecast = 0
#     for i in range(1, 4):
#         month = today.replace(day=1) + timedelta(days=32 * i)
#         month = month.replace(day=1)
#
#         from apps.quotations.models import Quotation
#         forecast += Quotation.objects.filter(
#             status='approved',
#             approval_date__year=month.year,
#             approval_date__month=month.month
#         ).aggregate(total=Sum('total_cost'))['total'] or 0
#
#     # (Optional) Additional metrics – you can compute these later
#     revenue_growth = 0
#     avg_closing_days = 0
#     win_rate = 0
#     active_deals = 0
#
#     context = {
#         'total_revenue': total_revenue,
#         'pending_revenue': pending_revenue,
#         'forecast_revenue': forecast,
#         'avg_deal_size': avg_deal_size,
#         'recent_deals': recent_deals,
#         'closed_deals': closed_deals,
#         'pending_deals': pending_deals,
#         'revenue_months': json.dumps(months[::-1]),
#         'revenue_data': json.dumps(revenue_data[::-1]),
#         'sales_labels': json.dumps(sales_labels),
#         'sales_data': json.dumps(sales_revenue),
#         'source_labels': json.dumps(source_labels),
#         'source_data': json.dumps(source_revenue),
#         'revenue_growth': revenue_growth,
#         'avg_closing_days': avg_closing_days,
#         'win_rate': win_rate,
#         'active_deals': active_deals,
#     }
#
#     return render(request, 'revenue/revenue.html', context)

@login_required
def revenue_dashboard(request):
    """
    Revenue dashboard with KPIs and charts
    """
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    last_day_month = today.replace(day=monthrange(today.year, today.month)[1])

    # ---------------------------
    # 1. Revenue by month (last 6 months, paid only)
    # ---------------------------
    months = []
    revenue_data = []
    for i in range(6):
        month = today.replace(day=1) - timedelta(days=30 * i)
        month_start = month.replace(day=1)
        month_end = month.replace(day=monthrange(month.year, month.month)[1])

        months.append(month.strftime('%b %Y'))
        month_revenue = Revenue.objects.filter(
            date__gte=month_start,
            date__lte=month_end,
            payment_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        revenue_data.append(float(month_revenue))

    # ---------------------------
    # 2. Revenue by sales person (this month, paid)
    # ---------------------------
    sales_revenue = []
    sales_labels = []
    sales_users = User.objects.filter(groups__name='Sales')
    for user in sales_users:
        total = Revenue.objects.filter(
            lead__assigned_to=user,
            date__gte=first_day_month,
            date__lte=last_day_month,
            payment_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        if total > 0:
            sales_revenue.append(float(total))
            sales_labels.append(user.get_full_name() or user.username)

    # ---------------------------
    # 3. Revenue by lead source (this month, paid)
    # ---------------------------
    source_revenue = []
    source_labels = []
    from apps.leads.models import LeadSource
    for source in LeadSource.objects.all():
        total = Revenue.objects.filter(
            lead__source=source,
            date__gte=first_day_month,
            date__lte=last_day_month,
            payment_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        if total > 0:
            source_revenue.append(float(total))
            source_labels.append(source.name)

    # ---------------------------
    # 4. Revenue by campaign (this month, paid)
    # ---------------------------
    campaign_revenue = {}
    revenues = Revenue.objects.filter(
        date__gte=first_day_month,
        date__lte=last_day_month,
        payment_status='paid'
    ).select_related('lead__campaign')
    for rev in revenues:
        campaign_name = rev.lead.campaign.name if rev.lead.campaign else "Uncategorized"
        campaign_revenue[campaign_name] = campaign_revenue.get(campaign_name, 0) + float(rev.amount)
    campaign_labels = list(campaign_revenue.keys())
    campaign_data = list(campaign_revenue.values())

    # ---------------------------
    # 5. Conversion ratio by stage (percentage of total leads in each stage)
    # ---------------------------
    from apps.leads.models import Lead
    total_leads = Lead.objects.count()
    if total_leads == 0:
        conversion_data = [0, 0, 0, 0, 0, 0]
    else:
        stage_counts = []
        stages = ['new', 'qualified', 'survey', 'quote', 'negotiation', 'won']
        for stage in stages:
            count = Lead.objects.filter(stage=stage).count()
            stage_counts.append(count)
        # Convert to percentages
        conversion_data = [round((count / total_leads) * 100, 1) for count in stage_counts]

    # ---------------------------
    # 6. Recent revenue records (all, for table)
    # ---------------------------
    recent_deals = Revenue.objects.all().select_related('lead', 'lead__assigned_to').order_by('-date')[:10]

    # ---------------------------
    # 7. KPI calculations
    # ---------------------------
    total_revenue = Revenue.objects.filter(
        date__gte=first_day_month,
        date__lte=last_day_month,
        payment_status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0

    pending_revenue = Revenue.objects.filter(
        payment_status__in=['pending', 'partial']
    ).aggregate(total=Sum('amount'))['total'] or 0

    avg_deal_size = Revenue.objects.filter(
        payment_status='paid'
    ).aggregate(avg=Avg('amount'))['avg'] or 0

    closed_deals = Revenue.objects.filter(payment_status='paid').count()
    pending_deals = Revenue.objects.filter(payment_status__in=['pending', 'partial']).count()

    # ---------------------------
    # 8. Forecast (next 3 months based on approved quotations)
    # ---------------------------
    forecast = 0
    for i in range(1, 4):
        month = today.replace(day=1) + timedelta(days=32 * i)
        month = month.replace(day=1)
        from apps.quotations.models import Quotation
        forecast += Quotation.objects.filter(
            status='approved',
            approval_date__year=month.year,
            approval_date__month=month.month
        ).aggregate(total=Sum('total_cost'))['total'] or 0

    # Placeholders for other KPIs (can be computed later)
    revenue_growth = 0
    avg_closing_days = 0
    win_rate = 0
    active_deals = 0

    context = {
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'forecast_revenue': forecast,
        'avg_deal_size': avg_deal_size,
        'recent_deals': recent_deals,
        'closed_deals': closed_deals,
        'pending_deals': pending_deals,
        'revenue_months': json.dumps(months[::-1]),
        'revenue_data': json.dumps(revenue_data[::-1]),
        'sales_labels': json.dumps(sales_labels),
        'sales_data': json.dumps(sales_revenue),
        'source_labels': json.dumps(source_labels),
        'source_data': json.dumps(source_revenue),
        'campaign_labels': json.dumps(campaign_labels),
        'campaign_data': json.dumps(campaign_data),
        'conversion_data': json.dumps(conversion_data),
        'revenue_growth': revenue_growth,
        'avg_closing_days': avg_closing_days,
        'win_rate': win_rate,
        'active_deals': active_deals,
    }

    return render(request, 'revenue/revenue.html', context)

@login_required
def add_revenue(request):
    """
    Add revenue record
    """
    if request.method == 'POST':
        form = RevenueForm(request.POST)
        if form.is_valid():
            revenue = form.save()
            # Update lead stage
            revenue.lead.stage = 'won'
            revenue.lead.converted_at = revenue.date
            revenue.lead.save()

            messages.success(request, 'Revenue recorded successfully!')
            return redirect('revenue_dashboard')
    else:
        lead_id = request.GET.get('lead')
        initial = {}
        if lead_id:
            initial['lead'] = lead_id
        form = RevenueForm(initial=initial)

    context = {
        'form': form,
        'title': 'Record Revenue'
    }
    return render(request, 'revenue/revenue_form.html', context)

@login_required
def revenue_export(request):
    """
    Export revenue data to CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="revenue_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Lead', 'Amount', 'Date', 'Payment Status', 'Payment Method', 'Transaction ID'])

    revenues = Revenue.objects.all().select_related('lead')
    for rev in revenues:
        writer.writerow([
            rev.lead.name,
            rev.amount,
            rev.date.strftime('%Y-%m-%d'),
            rev.get_payment_status_display(),
            rev.payment_method,
            rev.transaction_id,
        ])

    return response

@login_required
def mark_revenue_paid(request, pk):
    """
    Mark a pending revenue record as paid
    """
    revenue = get_object_or_404(Revenue, pk=pk)
    if request.method == 'POST':
        revenue.payment_status = 'paid'
        revenue.save()
        messages.success(request, 'Revenue marked as paid.')
    return redirect('revenue')