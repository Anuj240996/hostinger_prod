# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.db.models import Q, Sum, Count
# from django.utils import timezone
# from django.http import JsonResponse, HttpResponse, FileResponse
# from datetime import timedelta
# import csv
# from reportlab.pdf import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# import io
#
# from .models import Quotation, QuotationItem, QuotationRevision
# from .forms import QuotationForm, QuotationItemForm
# from apps.leads.models import Lead
# from apps.surveys.models import Survey
#
#
# @login_required
# def quotation_list(request):
#     """
#     List all quotations with filters
#     """
#     quotations = Quotation.objects.all().select_related('lead', 'created_by')
#
#     # Apply filters
#     status = request.GET.get('status')
#     if status:
#         quotations = quotations.filter(status=status)
#
#     created_by = request.GET.get('created_by')
#     if created_by:
#         quotations = quotations.filter(created_by_id=created_by)
#
#     from_date = request.GET.get('from_date')
#     if from_date:
#         quotations = quotations.filter(created__date__gte=from_date)
#
#     to_date = request.GET.get('to_date')
#     if to_date:
#         quotations = quotations.filter(created__date__lte=to_date)
#
#     # Summary stats
#     total_quotations = quotations.count()
#     approved_count = quotations.filter(status='approved').count()
#     pending_count = quotations.filter(status__in=['draft', 'sent', 'viewed', 'negotiating']).count()
#     total_value = quotations.aggregate(total=Sum('total_cost'))['total'] or 0
#
#     context = {
#         'quotations': quotations,
#         'total_quotations': total_quotations,
#         'approved_count': approved_count,
#         'pending_count': pending_count,
#         'total_value': total_value,
#         'sales_users': User.objects.filter(groups__name='Sales'),
#     }
#
#     return render(request, 'quotations/quotation_list.html', context)
#
#
# @login_required
# def quotation_detail(request, pk):
#     """
#     Display detailed view of a quotation
#     """
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     context = {
#         'quotation': quotation,
#     }
#
#     return render(request, 'quotations/quotation_detail.html', context)
#
#
# @login_required
# def quotation_create(request):
#     """
#     Create a new quotation
#     """
#     if request.method == 'POST':
#         form = QuotationForm(request.POST)
#         if form.is_valid():
#             quotation = form.save(commit=False)
#             quotation.created_by = request.user
#
#             # Calculate financials
#             quotation.gst_amount = quotation.subtotal * (quotation.gst_percentage / 100)
#             quotation.total_cost = quotation.subtotal + quotation.gst_amount
#             quotation.net_cost = quotation.total_cost - quotation.subsidy_amount
#
#             quotation.save()
#
#             # Update lead stage
#             if quotation.lead.stage == 'survey':
#                 quotation.lead.stage = 'quote'
#                 quotation.lead.save()
#
#             messages.success(request, 'Quotation created successfully!')
#             return redirect('quotation_detail', pk=quotation.id)
#     else:
#         lead_id = request.GET.get('lead')
#         survey_id = request.GET.get('survey')
#         initial = {}
#         if lead_id:
#             initial['lead'] = lead_id
#         if survey_id:
#             initial['survey'] = survey_id
#         form = QuotationForm(initial=initial)
#
#     context = {
#         'form': form,
#         'title': 'Create New Quotation'
#     }
#
#     return render(request, 'quotations/quotation_form.html', context)
#
#
# @login_required
# def quotation_edit(request, pk):
#     """
#     Edit an existing quotation
#     """
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     if request.method == 'POST':
#         form = QuotationForm(request.POST, instance=quotation)
#         if form.is_valid():
#             quotation = form.save(commit=False)
#
#             # Recalculate financials
#             quotation.gst_amount = quotation.subtotal * (quotation.gst_percentage / 100)
#             quotation.total_cost = quotation.subtotal + quotation.gst_amount
#             quotation.net_cost = quotation.total_cost - quotation.subsidy_amount
#
#             # Create revision if total cost changed
#             if quotation.pk and 'total_cost' in form.changed_data:
#                 QuotationRevision.objects.create(
#                     quotation=quotation,
#                     version=quotation.version + 1,
#                     total_cost=quotation.total_cost,
#                     created_by=request.user
#                 )
#                 quotation.version += 1
#
#             quotation.save()
#
#             messages.success(request, 'Quotation updated successfully!')
#             return redirect('quotation_detail', pk=quotation.id)
#     else:
#         form = QuotationForm(instance=quotation)
#
#     context = {
#         'form': form,
#         'quotation': quotation,
#         'title': f'Edit Quotation #{quotation.quote_number}'
#     }
#
#     return render(request, 'quotations/quotation_form.html', context)
#
#
# @login_required
# def quotation_send(request, pk):
#     """
#     Mark quotation as sent
#     """
#     if request.method == 'POST':
#         quotation = get_object_or_404(Quotation, pk=pk)
#         quotation.status = 'sent'
#         quotation.sent_date = timezone.now()
#         quotation.save()
#
#         messages.success(request, 'Quotation marked as sent!')
#
#     return redirect('quotation_detail', pk=quotation.id)
#
#
# @login_required
# def quotation_approve(request, pk):
#     """
#     Approve quotation
#     """
#     if request.method == 'POST':
#         quotation = get_object_or_404(Quotation, pk=pk)
#         quotation.status = 'approved'
#         quotation.customer_approved = True
#         quotation.internal_approved = True
#         quotation.approval_date = timezone.now()
#         quotation.approved_by = request.user
#         quotation.save()
#
#         # Update lead
#         quotation.lead.stage = 'won'
#         quotation.lead.converted_at = timezone.now()
#         quotation.lead.save()
#
#         messages.success(request, 'Quotation approved!')
#
#     return redirect('quotation_detail', pk=quotation.id)
#
#
# @login_required
# def quotation_reject(request, pk):
#     """
#     Reject quotation
#     """
#     if request.method == 'POST':
#         quotation = get_object_or_404(Quotation, pk=pk)
#         quotation.status = 'rejected'
#         quotation.save()
#
#         messages.info(request, 'Quotation rejected.')
#
#     return redirect('quotation_detail', pk=quotation.id)
#
#
# @login_required
# def add_quotation_item(request, pk):
#     """
#     Add item to quotation
#     """
#     if request.method == 'POST':
#         quotation = get_object_or_404(Quotation, pk=pk)
#
#         form = QuotationItemForm(request.POST)
#         if form.is_valid():
#             item = form.save(commit=False)
#             item.quotation = quotation
#             item.total_price = item.quantity * item.unit_price
#             item.save()
#
#             # Update quotation subtotal
#             quotation.subtotal = quotation.items.aggregate(total=Sum('total_price'))['total'] or 0
#             quotation.gst_amount = quotation.subtotal * (quotation.gst_percentage / 100)
#             quotation.total_cost = quotation.subtotal + quotation.gst_amount
#             quotation.net_cost = quotation.total_cost - quotation.subsidy_amount
#             quotation.save()
#
#             return JsonResponse({'success': True})
#
#     return JsonResponse({'success': False}, status=400)
#
#
# @login_required
# def add_negotiation_note(request, pk):
#     """
#     Add negotiation note to quotation
#     """
#     if request.method == 'POST':
#         quotation = get_object_or_404(Quotation, pk=pk)
#         note = request.POST.get('note')
#
#         if note:
#             if quotation.negotiation_notes:
#                 quotation.negotiation_notes += f"\n\n{timezone.now().strftime('%Y-%m-%d %H:%M')} - {request.user.get_full_name()}:\n{note}"
#             else:
#                 quotation.negotiation_notes = f"{timezone.now().strftime('%Y-%m-%d %H:%M')} - {request.user.get_full_name()}:\n{note}"
#
#             quotation.status = 'negotiating'
#             quotation.save()
#
#             return JsonResponse({'success': True})
#
#     return JsonResponse({'success': False}, status=400)
#
#
# @login_required
# def quotation_pdf(request, pk):
#     """
#     Generate PDF for quotation
#     """
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     # Create PDF
#     buffer = io.BytesIO()
#     p = canvas.Canvas(buffer, pagesize=letter)
#     width, height = letter
#
#     # Header
#     p.setFont("Helvetica-Bold", 20)
#     p.drawString(50, height - 50, "SOLAR QUOTATION")
#
#     p.setFont("Helvetica", 12)
#     p.drawString(50, height - 80, f"Quote #: {quotation.quote_number}")
#     p.drawString(50, height - 95, f"Date: {quotation.created.strftime('%d-%m-%Y')}")
#     p.drawString(50, height - 110, f"Valid Until: {quotation.valid_until.strftime('%d-%m-%Y')}")
#
#     # Customer Details
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(50, height - 140, "Customer Details")
#
#     p.setFont("Helvetica", 12)
#     p.drawString(50, height - 160, f"Name: {quotation.lead.name}")
#     p.drawString(50, height - 175, f"Address: {quotation.lead.address}")
#     p.drawString(50, height - 190, f"Phone: {quotation.lead.phone}")
#
#     # System Details
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(50, height - 220, "System Details")
#
#     p.setFont("Helvetica", 12)
#     p.drawString(50, height - 240, f"System Size: {quotation.system_size} kW")
#     p.drawString(50, height - 255, f"Panel Type: {quotation.panel_type}")
#     p.drawString(50, height - 270, f"Panel Count: {quotation.panel_count}")
#     p.drawString(50, height - 285, f"Inverter: {quotation.inverter_type}")
#
#     # Cost Breakdown
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(50, height - 315, "Cost Breakdown")
#
#     y = height - 335
#     p.setFont("Helvetica-Bold", 10)
#     p.drawString(50, y, "Description")
#     p.drawString(300, y, "Qty")
#     p.drawString(350, y, "Unit Price")
#     p.drawString(450, y, "Total")
#
#     y -= 15
#     p.setFont("Helvetica", 10)
#
#     for item in quotation.items.all():
#         p.drawString(50, y, item.description[:30])
#         p.drawString(300, y, str(item.quantity))
#         p.drawString(350, y, f"₹{item.unit_price:,.2f}")
#         p.drawString(450, y, f"₹{item.total_price:,.2f}")
#         y -= 15
#
#         if y < 50:  # New page
#             p.showPage()
#             y = height - 50
#
#     # Totals
#     y -= 10
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(350, y, "Subtotal:")
#     p.drawString(450, y, f"₹{quotation.subtotal:,.2f}")
#
#     y -= 15
#     p.drawString(350, y, f"GST ({quotation.gst_percentage}%):")
#     p.drawString(450, y, f"₹{quotation.gst_amount:,.2f}")
#
#     y -= 15
#     p.drawString(350, y, "Total:")
#     p.drawString(450, y, f"₹{quotation.total_cost:,.2f}")
#
#     y -= 15
#     p.drawString(350, y, "Subsidy:")
#     p.drawString(450, y, f"-₹{quotation.subsidy_amount:,.2f}")
#
#     y -= 15
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(350, y, "Net Cost:")
#     p.drawString(450, y, f"₹{quotation.net_cost:,.2f}")
#
#     # Financial Analysis
#     y -= 30
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(50, y, "Financial Analysis")
#
#     y -= 20
#     p.setFont("Helvetica", 12)
#     p.drawString(50, y, f"ROI: {quotation.roi}%")
#     p.drawString(200, y, f"Payback Period: {quotation.payback_years} years")
#
#     y -= 15
#     p.drawString(50, y, f"Monthly EMI: ₹{quotation.monthly_emi:,.2f}")
#     p.drawString(200, y, f"Monthly Savings: ₹{quotation.monthly_savings:,.2f}")
#
#     # Terms
#     y -= 30
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(50, y, "Terms & Conditions:")
#
#     y -= 15
#     p.setFont("Helvetica", 10)
#     terms = quotation.terms_conditions.split('\n')
#     for line in terms:
#         p.drawString(50, y, line)
#         y -= 12
#
#     p.save()
#
#     buffer.seek(0)
#     return FileResponse(buffer, as_attachment=True, filename=f"Quotation_{quotation.quote_number}.pdf")
#
#
# @login_required
# def quotation_export(request):
#     """
#     Export quotations to CSV
#     """
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="quotations_{timezone.now().date()}.csv"'
#
#     writer = csv.writer(response)
#     writer.writerow(['Quote #', 'Lead', 'System Size', 'Total Cost', 'Status', 'Created By', 'Created Date'])
#
#     quotations = Quotation.objects.all().select_related('lead', 'created_by')
#     for quote in quotations:
#         writer.writerow([
#             quote.quote_number,
#             quote.lead.name,
#             f"{quote.system_size} kW",
#             quote.total_cost,
#             quote.get_status_display(),
#             quote.created_by.get_full_name() if quote.created_by else '',
#             quote.created.strftime('%Y-%m-%d'),
#         ])
#
#     return response

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.http import JsonResponse, HttpResponse
from datetime import date, datetime, timedelta
import csv
import hashlib
from collections import defaultdict

from .models import Quotation, QuotationItem, QuotationRevision
from .forms import QuotationForm, QuotationItemForm
from apps.leads.models import Lead
from apps.surveys.models import Survey
from django.contrib.auth.models import User

import logging

# Try to import reportlab, provide fallback if not available
try:
    from reportlab.pdfgen.canvas import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not installed. PDF generation will be disabled.")

from .models import Quotation, QuotationItem, QuotationRevision
from .forms import QuotationForm, QuotationItemForm
from apps.leads.models import Lead
from apps.surveys.models import Survey
from django.contrib.auth.models import User

from customer.staff_access import quotation_queryset_for_request
from apps.leads.forms import pipeline_quotation_filter_assigned_users_queryset

logger = logging.getLogger(__name__)


def _crm_erp_quotation_or_404(request, pk):
    """ERP quotation (quotation_quotation) scoped like list/detail — not legacy apps.quotations.Quotation."""
    return get_object_or_404(quotation_queryset_for_request(request.user), pk=pk)


def _erp_quotation_sort_key_by_quote_no(q):
    """
    Descending order by Quote# (numeric base, then revision suffix), aligned with
    /quotation/quotations/ ERP list. Non-numeric or empty numbers sort last.
    """
    no = (getattr(q, 'quotation_no', None) or '').strip()
    if not no:
        return (0, 0, getattr(q, 'pk', None) or 0)
    parts = no.split('_')
    try:
        base = int(parts[0])
    except (ValueError, TypeError):
        base = 0
    try:
        rev = int(parts[1]) if len(parts) > 1 else 0
    except (ValueError, TypeError):
        rev = 0
    pk = getattr(q, 'pk', None) or 0
    return (base, rev, pk)


def _crm_quotation_base_key(q):
    """
    Group rows by quotation number base (part before '_'), e.g. 1005 and 1005_1 together.
    Does not use lead name or consumer identity — same behaviour as ERP quotation list.
    """
    no = (getattr(q, 'quotation_no', None) or '').strip()
    if not no:
        return f'pk:{getattr(q, "pk", 0)}'
    base = no.split('_')[0].strip()
    return base if base else f'pk:{getattr(q, "pk", 0)}'


def _crm_quotations_latest_per_family(quotations_sorted):
    """One entry per quote-no base (latest revision only — revisions are not counted separately)."""
    groups = defaultdict(list)
    for q in quotations_sorted:
        groups[_crm_quotation_base_key(q)].append(q)
    latest = [
        max(members, key=_erp_quotation_sort_key_by_quote_no)
        for members in groups.values()
    ]
    return sorted(latest, key=_erp_quotation_sort_key_by_quote_no, reverse=True)


def _crm_expand_quotation_families_for_page(latest_on_page, all_quotations_sorted):
    """Include older revisions for families on this page so Details toggle still works."""
    if not latest_on_page:
        return []
    bases = {_crm_quotation_base_key(q) for q in latest_on_page}
    return [q for q in all_quotations_sorted if _crm_quotation_base_key(q) in bases]


_CRM_PENDING_QUOTATION_STATUSES = frozenset({
    'draft', 'sent', 'viewed', 'negotiating', 'expired',
})

# Card/board view columns (quotations list Kanban — matches KPI buckets)
QUOTATION_LIST_BOARD_COLUMNS = (
    {'key': 'pending', 'label': 'Pending'},
    {'key': 'approved', 'label': 'Approved'},
    {'key': 'converted', 'label': 'Converted'},
    {'key': 'rejected', 'label': 'Rejected'},
)


def _crm_quotation_board_column_key(status):
    """Map quotation status to a board column (unknown statuses → pending)."""
    s = (status or '').strip()
    if s in _CRM_PENDING_QUOTATION_STATUSES:
        return 'pending'
    if s == 'approved':
        return 'approved'
    if s == 'rejected':
        return 'rejected'
    if s == 'converted':
        return 'converted'
    return 'pending'


def build_quotation_list_board_columns(latest_quotations):
    """Group latest-per-family quotations into board columns with counts."""
    buckets = {col['key']: [] for col in QUOTATION_LIST_BOARD_COLUMNS}
    for q in latest_quotations:
        buckets[_crm_quotation_board_column_key(q.status)].append(q)
    columns = []
    for col in QUOTATION_LIST_BOARD_COLUMNS:
        items = buckets[col['key']]
        columns.append({
            'key': col['key'],
            'label': col['label'],
            'count': len(items),
            'quotations': items,
        })
    return columns


def _crm_summary_stats_for_latest_quotations(latest_quotations):
    """
    Summary cards: one count per quote family (latest revision).
    Status buckets are mutually exclusive and cover all quotations so
    Total = Pending + Approved + Rejected + Converted.
    """
    pending_count = 0
    approved_count = 0
    rejected_count = 0
    converted_count = 0
    other_count = 0
    total_value = 0

    for q in latest_quotations:
        status = (q.status or '').strip()
        if status in _CRM_PENDING_QUOTATION_STATUSES:
            pending_count += 1
        elif status == 'approved':
            approved_count += 1
        elif status == 'rejected':
            rejected_count += 1
        elif status == 'converted':
            converted_count += 1
            amount = q.final_amount if q.final_amount is not None else q.net_amount
            if amount is not None:
                total_value += amount
        else:
            other_count += 1

    # Unknown/legacy statuses roll into pending so the cards always reconcile.
    pending_count += other_count

    total_quotations = (
        pending_count + approved_count + rejected_count + converted_count
    )

    return {
        'total_quotations': total_quotations,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'converted_count': converted_count,
        'total_value': total_value,
    }


def crm_dashboard_total_quotations_count(user):
    """Latest revision per quote family — same count as /new-lead/quotations/ Total card."""
    from customer.staff_access import quotation_queryset_for_request

    quotations_all = sorted(
        list(quotation_queryset_for_request(user)),
        key=_erp_quotation_sort_key_by_quote_no,
        reverse=True,
    )
    latest = _crm_quotations_latest_per_family(quotations_all)
    return _crm_summary_stats_for_latest_quotations(latest)['total_quotations']


def _crm_attach_quotation_base_row_flags(quotations_sorted):
    """
    Per quotation-no base: latest revision visible; older revisions hidden until Details is toggled.
    """
    groups = defaultdict(list)
    for q in quotations_sorted:
        groups[_crm_quotation_base_key(q)].append(q)

    for key, members in groups.items():
        group_id = hashlib.md5(key.encode('utf-8')).hexdigest()[:16]
        latest = max(members, key=_erp_quotation_sort_key_by_quote_no)
        n = len(members)
        has_multi = n > 1
        for q in members:
            q.crm_quote_base_group_id = group_id
            q.crm_is_latest_for_quote_base = q.pk == latest.pk
            q.crm_quote_previous_count = max(0, n - 1)
            q.crm_has_multiple_quote_revisions = has_multi
            q.crm_hide_non_latest_row = q.pk != latest.pk


@login_required
def quotation_list(request):
    """
    List ERP quotations (quotation_quotation) — same records as /quotation/quotation/new/
    and the legacy inventory quotation table. Uses the same scoping as /quotation/quotations/.
    """
    base_quotations_qs = quotation_queryset_for_request(request.user)
    quotations_qs = base_quotations_qs.select_related(
        'lead', 'created_by', 'plant_capacity_kw', 'assigned_associate'
    )

    assigned_to = request.GET.get('assigned_to')

    # Status filter is applied after latest-per-family (see below) so KPI cards match the table.
    status_filter = (request.GET.get('status') or '').strip().lower()

    if assigned_to:
        quotations_qs = quotations_qs.filter(
            Q(lead__assigned_to_id=assigned_to) | Q(assigned_associate_id=assigned_to)
        )

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    from_date_parsed = parse_date(from_date.strip()) if from_date and from_date.strip() else None
    to_date_parsed = parse_date(to_date.strip()) if to_date and to_date.strip() else None

    search_query = (request.GET.get('q') or '').strip()
    if search_query:
        quotations_qs = quotations_qs.filter(
            Q(quotation_no__icontains=search_query)
            | Q(consumer_name__icontains=search_query)
            | Q(status__icontains=search_query)
            | Q(lead__name__icontains=search_query)
            | Q(created_by__first_name__icontains=search_query)
            | Q(created_by__last_name__icontains=search_query)
            | Q(created_by__username__icontains=search_query)
        ).distinct()

    # Table order: descending by Quote# (quotation_no base, then _revision), not by calendar date
    quotations_all = sorted(
        list(quotations_qs),
        key=_erp_quotation_sort_key_by_quote_no,
        reverse=True,
    )
    if from_date_parsed or to_date_parsed:
        quotations_all = [
            q for q in quotations_all
            if _erp_quotation_in_date_range(q, from_date_parsed, to_date_parsed)
        ]
    quotations_latest = _crm_quotations_latest_per_family(quotations_all)
    summary = _crm_summary_stats_for_latest_quotations(quotations_latest)

    if status_filter == 'pending':
        quotations_latest = [
            q for q in quotations_latest
            if (q.status or '').strip() in _CRM_PENDING_QUOTATION_STATUSES
        ]
    elif status_filter:
        quotations_latest = [
            q for q in quotations_latest
            if (q.status or '').strip() == status_filter
        ]

    per_page_raw = (request.GET.get('per_page') or '20').strip().lower()
    if per_page_raw == 'all':
        per_page = max(1, len(quotations_latest))
    else:
        try:
            per_page = int(per_page_raw)
        except (TypeError, ValueError):
            per_page = 20
        if per_page not in (10, 20, 50):
            per_page = 20
    paginator = Paginator(quotations_latest, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    page_quotations = _crm_expand_quotation_families_for_page(
        page_obj.object_list,
        quotations_all,
    )
    _crm_attach_quotation_base_row_flags(page_quotations)
    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)

    context = {
        'quotations': page_quotations,
        'export_quotations': quotations_latest,
        'page_obj': page_obj,
        'total_quotations': summary['total_quotations'],
        'approved_count': summary['approved_count'],
        'pending_count': summary['pending_count'],
        'rejected_count': summary['rejected_count'],
        'converted_count': summary['converted_count'],
        'total_value': summary['total_value'],
        'sales_users': pipeline_quotation_filter_assigned_users_queryset(
            lead_queryset=Lead.objects.filter(
                pk__in=base_quotations_qs.exclude(lead_id__isnull=True).values_list(
                    'lead_id', flat=True
                ).distinct()
            ),
            quotation_queryset=base_quotations_qs,
            selected_pk=assigned_to,
        ),
        'pagination_query': pagination_params.urlencode(),
        'board_columns': build_quotation_list_board_columns(quotations_latest),
        'quotations_latest_count': len(quotations_latest),
    }

    return render(request, 'quotations/quotation_list.html', context)


def _erp_quotation_payback_pdf_context(quotation):
    """
    Same PAYBACK CALCULATIONS inputs as quotation PDF (quotation_template / industrial flow).
    """
    plant_capacity = (
        float(quotation.plant_capacity_kw.capacity) if quotation.plant_capacity_kw else 0.0
    )
    unit_rate = float(quotation.electricity_unit_rate or 11.00)
    subsidy = 78000.0
    investment_cost = float(quotation.final_amount or quotation.net_amount or 0)
    units_generated_per_year = plant_capacity * 4 * 365
    yearly_saving = units_generated_per_year * unit_rate
    after_subsidy_amount = investment_cost - subsidy
    payback_period = round(after_subsidy_amount / yearly_saving, 1) if yearly_saving > 0 else 0
    return {
        'plant_capacity_kw': plant_capacity,
        'units_generated_per_year': units_generated_per_year,
        'unit_rate': unit_rate,
        'yearly_saving': yearly_saving,
        'investment_cost': investment_cost,
        'subsidy_amount': subsidy,
        'after_subsidy_amount': after_subsidy_amount,
        'payback_period': payback_period,
    }


def _erp_quotation_date_as_python_date(value):
    """Normalize quotation.date / created_at / string DB values to datetime.date."""
    if value is None or value == '':
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
            for n in (26, 19, 10):
                if len(s) < n:
                    continue
                try:
                    return datetime.strptime(s[:n], fmt).date()
                except ValueError:
                    continue
    return None


def _erp_quotation_in_date_range(quotation, from_date, to_date):
    """
    Inclusive date-range filter for CRM quotation list.
    Uses quotation.date then created_at (Python-side) to avoid PostgreSQL
    AT TIME ZONE errors when legacy DB columns are not true timestamps.
    """
    qd = _erp_quotation_date_as_python_date(getattr(quotation, 'date', None))
    if qd is None:
        qd = _erp_quotation_date_as_python_date(getattr(quotation, 'created_at', None))
    if qd is None:
        return False
    if from_date and qd < from_date:
        return False
    if to_date and qd > to_date:
        return False
    return True


def _erp_quotation_datetime_for_template(value):
    """
    Build a datetime Django's date filter can always format (handles date field as date, datetime, or string).
    """
    if value is None or value == '':
        return None
    if isinstance(value, datetime):
        return value
    d = _erp_quotation_date_as_python_date(value)
    if d is not None:
        return datetime.combine(d, datetime.min.time())
    return None


def _erp_quotation_sidebar_dates(quotation):
    """
    Dates card — Created row: quotation_quotation.date (fallback: created_at).
    Valid until: 10 calendar days including the start day → last valid day = start + 9.
    Start day: quotation.date, else created_at.date().
    """
    q_date = getattr(quotation, 'date', None)
    created_at = getattr(quotation, 'created_at', None)

    dates_created_display = _erp_quotation_datetime_for_template(q_date)
    if dates_created_display is None and created_at is not None:
        dates_created_display = created_at

    start = _erp_quotation_date_as_python_date(q_date)
    if start is None and created_at is not None:
        start = created_at.date() if hasattr(created_at, 'date') else None

    valid_until_display = None
    if start is not None:
        valid_until_display = start + timedelta(days=9)

    return {
        'dates_created_display': dates_created_display,
        'dates_valid_until_display': valid_until_display,
    }


@login_required
def quotation_detail(request, pk):
    """
    CRM-styled read-only detail for an ERP quotation (quotation_quotation), same rows as the list.
    Scoped with quotation_queryset_for_request like /new-lead/quotations/.
    """
    from django.db.models import Prefetch
    from quotation.models import (
        QuotationApprovalRecord,
        QuotationConversionRecord,
        QuotationRejectionRecord,
    )

    qs = quotation_queryset_for_request(request.user).select_related(
        'lead',
        'survey',
        'plant_capacity_kw',
        'assigned_associate',
        'created_by',
        'approved_by',
        'sent_by',
        'organization',
    )

    # Avoid 500 if migrations for history tables are not applied yet.
    existing_tables = set(connection.introspection.table_names())
    approval_history_available = QuotationApprovalRecord._meta.db_table in existing_tables
    conversion_history_available = QuotationConversionRecord._meta.db_table in existing_tables
    rejection_history_available = QuotationRejectionRecord._meta.db_table in existing_tables

    if approval_history_available:
        qs = qs.prefetch_related(
            Prefetch(
                'approval_records',
                queryset=QuotationApprovalRecord.objects.select_related(
                    'approved_by',
                ).order_by('-created_at'),
            ),
        )
    if rejection_history_available:
        qs = qs.prefetch_related(
            Prefetch(
                'rejection_records',
                queryset=QuotationRejectionRecord.objects.select_related(
                    'rejected_by',
                ).order_by('-created_at'),
            ),
        )
    if conversion_history_available:
        qs = qs.prefetch_related(
            Prefetch(
                'conversion_records',
                queryset=QuotationConversionRecord.objects.select_related(
                    'converted_by',
                ).order_by('-created_at'),
            ),
        )

    quotation = get_object_or_404(qs, pk=pk)

    sidebar_dates = _erp_quotation_sidebar_dates(quotation)

    # One card per revision, same data as revise page.
    from quotation.views import (
        quotation_family_cards_for_request,
        quotation_is_latest_in_family_for_request,
    )

    quotation_family_cards = quotation_family_cards_for_request(request, quotation)
    quotation_detail_actions_allowed = quotation_is_latest_in_family_for_request(
        request, quotation
    )
    approval_history_records = []
    if approval_history_available:
        approval_history_records = list(quotation.approval_records.all())
    if not approval_history_records and quotation.approved_date:
        approval_history_records = [
            {
                'created_at': quotation.approved_date,
                'status_snapshot': 'approved',
                'approved_by': quotation.approved_by,
                'payment_type_snapshot': quotation.payment_type or '',
                'payment_mode_snapshot': quotation.payment_mode or '',
                'hybrid_mode_snapshot': quotation.hybrid_mode or '',
                'po_order_no_snapshot': quotation.po_order_no or '',
                'po_date_snapshot': quotation.po_date,
            }
        ]
    conversion_history_records = []
    if conversion_history_available:
        conversion_history_records = list(quotation.conversion_records.all())
    elif quotation.status == 'converted':
        conversion_history_records = [
            {
                'created_at': quotation.approved_date or quotation.sent_date or quotation.created_at,
                'converted_by': quotation.approved_by,
            }
        ]
    dates_converted_display = None
    if conversion_history_records:
        first_conv = conversion_history_records[0]
        if isinstance(first_conv, dict):
            dates_converted_display = first_conv.get('created_at')
        else:
            dates_converted_display = getattr(first_conv, 'created_at', None)
    elif quotation.status == 'converted':
        dates_converted_display = quotation.approved_date or quotation.sent_date or quotation.created_at
    rejection_history_records = []
    if rejection_history_available:
        rejection_history_records = list(quotation.rejection_records.all())
    if not rejection_history_records and quotation.status == 'rejected':
        rejection_history_records = [
            {
                'created_at': quotation.approved_date or quotation.sent_date or quotation.created_at,
                'reason': '',
                'rejected_by': None,
            }
        ]

    dates_rejected_display = None
    if rejection_history_records:
        latest_rej = rejection_history_records[0]
        if isinstance(latest_rej, dict):
            dates_rejected_display = latest_rej.get('created_at')
        else:
            dates_rejected_display = getattr(latest_rej, 'created_at', None)
    elif quotation.status == 'rejected':
        dates_rejected_display = quotation.approved_date or quotation.sent_date or quotation.created_at

    context = {
        'quotation': quotation,
        'payback': _erp_quotation_payback_pdf_context(quotation),
        **sidebar_dates,
        'dates_converted_display': dates_converted_display,
        'dates_rejected_display': dates_rejected_display,
        'quotation_family_cards': quotation_family_cards,
        'quotation_detail_actions_allowed': quotation_detail_actions_allowed,
        'approval_history_records': approval_history_records,
        'rejection_history_records': rejection_history_records,
        'conversion_history_records': conversion_history_records,
        'approval_history_available': approval_history_available,
        'conversion_history_available': conversion_history_available,
        'rejection_history_available': rejection_history_available,
    }

    return render(request, 'quotations/quotation_detail_erp.html', context)

#
# @login_required
# def quotation_create(request):
#     """
#     Create a new quotation
#     """
#     if request.method == 'POST':
#         form = QuotationForm(request.POST)
#         if form.is_valid():
#             quotation = form.save(commit=False)
#             quotation.created_by = request.user
#
#             # Calculate financials
#             quotation.gst_amount = quotation.subtotal * (quotation.gst_percentage / 100)
#             quotation.total_cost = quotation.subtotal + quotation.gst_amount
#             quotation.net_cost = quotation.total_cost - quotation.subsidy_amount
#
#             quotation.save()
#
#             # Update lead stage
#             if quotation.lead.stage == 'survey':
#                 quotation.lead.stage = 'quote'
#                 quotation.lead.save()
#
#             messages.success(request, 'Quotation created successfully!')
#             return redirect('quotation_detail', pk=quotation.id)
#     else:
#         lead_id = request.GET.get('lead')
#         survey_id = request.GET.get('survey')
#         initial = {}
#         if lead_id:
#             initial['lead'] = lead_id
#         if survey_id:
#             initial['survey'] = survey_id
#         form = QuotationForm(initial=initial)
#
#     context = {
#         'form': form,
#         'title': 'Create New Quotation'
#     }
#
#     return render(request, 'quotations/quotation_form.html', context)

@login_required
def quotation_create(request):
    """
    Same full ERP create quotation screen as /quotation/quotation/new/, served here under CRM
    (no redirect — stays on /new-lead/quotations/create/).
    """
    try:
        from quotation.views import create_quotation as erp_create_quotation
    except ImportError:
        messages.error(
            request,
            'The full quotation module is not available in this deployment.',
        )
        return redirect('quotation_list')
    return erp_create_quotation(request)


@login_required
def quotation_edit(request, pk):
    """
    Full ERP edit quotation screen under Lead CRM (/new-lead/quotations/<pk>/edit/),
    same as /quotation/quotation/<pk>/edit/ but with CRM base layout.
    """
    _crm_erp_quotation_or_404(request, pk)
    try:
        from quotation.views import edit_quotation as erp_edit_quotation
    except ImportError:
        messages.error(
            request,
            'The full quotation module is not available in this deployment.',
        )
        return redirect('quotation_list')
    return erp_edit_quotation(request, pk)


@login_required
def quotation_send(request, pk):
    """
    Mark ERP quotation as sent (same workflow as legacy CRM detail page).
    """
    if request.method == 'POST':
        quotation = _crm_erp_quotation_or_404(request, pk)
        if quotation.status != 'draft':
            messages.warning(request, 'Only draft quotations can be sent.')
        else:
            quotation.status = 'sent'
            quotation.sent_date = timezone.now()
            quotation.sent_by = request.user
            quotation.save()
            try:
                from apps.leads.timeline import log_quotation_timeline_activity
                log_quotation_timeline_activity(
                    quotation,
                    request.user if request.user.is_authenticated else None,
                    event='sent',
                )
            except Exception:
                pass
            messages.success(request, 'Quotation marked as sent!')

    return redirect('quotation_detail', pk=pk)

#
# @login_required
# def quotation_approve(request, pk):
#     """
#     Approve quotation
#     """
#     if request.method == 'POST':
#         quotation = get_object_or_404(Quotation, pk=pk)
#         quotation.status = 'approved'
#         quotation.customer_approved = True
#         quotation.internal_approved = True
#         quotation.approval_date = timezone.now()
#         quotation.approved_by = request.user
#         quotation.save()
#
#         # Update lead
#         quotation.lead.stage = 'won'
#         quotation.lead.converted_at = timezone.now()
#         quotation.lead.save()
#
#         messages.success(request, 'Quotation approved!')
#
#     return redirect('quotation_detail', pk=quotation.id)

@login_required
def quotation_approve(request, pk):
    if request.method != 'POST':
        return redirect('quotation_detail', pk=pk)
    quotation = _crm_erp_quotation_or_404(request, pk)
    if quotation.status not in ('sent', 'viewed', 'negotiating'):
        messages.warning(request, 'Only sent or in-review quotations can be approved.')
        return redirect('quotation_detail', pk=pk)
    payment_type = (request.POST.get('payment_type') or '').strip()
    payment_mode = (request.POST.get('payment_mode') or '').strip()
    hybrid_mode = (request.POST.get('hybrid_mode') or '').strip()
    po_order_no = (request.POST.get('po_order_no') or '').strip()
    po_date_str = (request.POST.get('po_date') or '').strip()

    if payment_type:
        quotation.payment_type = payment_type
    if payment_mode:
        quotation.payment_mode = payment_mode
    quotation.hybrid_mode = hybrid_mode if payment_mode == 'Hybrid' else ''
    quotation.po_order_no = po_order_no
    if po_date_str:
        try:
            quotation.po_date = datetime.strptime(po_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    else:
        quotation.po_date = None
    from quotation.models import QuotationApprovalRecord

    quotation.status = 'approved'
    quotation.customer_approval = True
    quotation.internal_approval = True
    quotation.approved_date = timezone.now()
    quotation.approved_by = request.user
    quotation.save()
    if QuotationApprovalRecord._meta.db_table in set(connection.introspection.table_names()):
        QuotationApprovalRecord.objects.create(
            quotation=quotation,
            status_snapshot='approved',
            payment_type_snapshot=quotation.payment_type or '',
            payment_mode_snapshot=quotation.payment_mode or '',
            hybrid_mode_snapshot=quotation.hybrid_mode or '',
            po_order_no_snapshot=quotation.po_order_no or '',
            po_date_snapshot=quotation.po_date,
            approved_by=request.user if request.user.is_authenticated else None,
        )

    if quotation.lead_id:
        try:
            from apps.leads.timeline import log_quotation_timeline_activity
            log_quotation_timeline_activity(
                quotation,
                request.user if request.user.is_authenticated else None,
                event='approved',
            )
        except Exception:
            pass

    messages.success(request, 'Quotation approved!')
    return redirect('quotation_detail', pk=pk)

@login_required
def quotation_reject(request, pk):
    """
    Reject ERP quotation with required reason (modal POST). Clears approval flags.
    """
    if request.method != 'POST':
        return redirect('quotation_detail', pk=pk)

    from quotation.models import QuotationRejectionRecord
    from quotation.views import quotation_is_latest_in_family_for_request

    quotation = _crm_erp_quotation_or_404(request, pk)
    if not quotation_is_latest_in_family_for_request(request, quotation):
        messages.warning(request, 'You can only reject the latest quotation revision in this quote family.')
        return redirect('quotation_detail', pk=pk)

    reason = (request.POST.get('reject_reason') or '').strip()
    if not reason:
        messages.error(request, 'Please enter a rejection reason.')
        return redirect('quotation_detail', pk=pk)

    quotation.status = 'rejected'
    quotation.customer_approval = False
    quotation.internal_approval = False
    quotation.approved_by = None
    quotation.approved_date = None
    quotation.save()

    QuotationRejectionRecord.objects.create(
        quotation=quotation,
        reason=reason,
        rejected_by=request.user if request.user.is_authenticated else None,
    )
    if quotation.lead_id:
        try:
            from apps.leads.timeline import log_quotation_timeline_activity
            log_quotation_timeline_activity(
                quotation,
                request.user if request.user.is_authenticated else None,
                event='rejected',
            )
        except Exception:
            pass
    messages.info(request, 'Quotation rejected.')
    return redirect('quotation_detail', pk=pk)


@login_required
def quotation_mark_converted(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    from quotation.conversion_utils import finalize_quotation_conversion
    from quotation.views import quotation_is_latest_in_family_for_request

    quotation = _crm_erp_quotation_or_404(request, pk)
    if not quotation_is_latest_in_family_for_request(request, quotation):
        return JsonResponse(
            {'success': False, 'message': 'Only latest quotation revision can be converted.'},
            status=400,
        )
    if quotation.status not in ('approved', 'converted'):
        return JsonResponse(
            {'success': False, 'message': 'Only approved quotation can be converted to consumer.'},
            status=400,
        )

    finalize_quotation_conversion(
        quotation,
        converted_by=request.user if request.user.is_authenticated else None,
    )

    return JsonResponse({'success': True})


@login_required
def quotation_revise(request, pk):
    """
    Full revise flow under Lead CRM URL (/new-lead/quotations/<pk>/revise/).
    Delegates to quotation.views.revise_quotation (same logic as ERP; template uses CRM base).
    """
    _crm_erp_quotation_or_404(request, pk)
    from quotation.views import revise_quotation as erp_revise_quotation

    return erp_revise_quotation(request, pk)


@login_required
def add_quotation_item(request, pk):
    """
    Add item to quotation
    """
    if request.method == 'POST':
        quotation = get_object_or_404(Quotation, pk=pk)

        form = QuotationItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.quotation = quotation
            item.total_price = item.quantity * item.unit_price
            item.save()

            # Update quotation subtotal
            quotation.subtotal = quotation.items.aggregate(total=Sum('total_price'))['total'] or 0
            quotation.gst_amount = quotation.subtotal * (quotation.gst_percentage / 100)
            quotation.total_cost = quotation.subtotal + quotation.gst_amount
            quotation.net_cost = quotation.total_cost - quotation.subsidy_amount
            quotation.save()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)


@login_required
def add_negotiation_note(request, pk):
    """
    Add negotiation note to quotation
    """
    if request.method == 'POST':
        quotation = get_object_or_404(Quotation, pk=pk)
        note = request.POST.get('note')

        if note:
            if quotation.negotiation_notes:
                quotation.negotiation_notes += f"\n\n{timezone.now().strftime('%Y-%m-%d %H:%M')} - {request.user.get_full_name()}:\n{note}"
            else:
                quotation.negotiation_notes = f"{timezone.now().strftime('%Y-%m-%d %H:%M')} - {request.user.get_full_name()}:\n{note}"

            quotation.status = 'negotiating'
            quotation.save()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)

#
# def quotation_pdf(request, pk):
#     """
#     PDF generation - temporarily disabled
#     """
#     messages.info(request, 'PDF generation is currently being set up. Please check back later.')
#     return redirect('quotation_detail', pk=pk)


from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime


def _lead_quotation_pdf_buffer(quotation, variant='standard'):
    """
    variant: 'standard' (default) or 'company' — layout/branding only; same data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=16, spaceAfter=20))
    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT, fontSize=10))

    company = variant == 'company'
    accent = colors.HexColor('#2c5282') if company else colors.grey
    label_bg = colors.HexColor('#bee3f8') if company else colors.lightgrey
    row_bg = colors.HexColor('#ebf8ff') if company else colors.beige
    customer_name = quotation.get_customer_display_name()

    title = "COMPANY QUOTATION" if company else "SOLAR QUOTATION"
    elements.append(Paragraph(title, styles['Center']))
    if company:
        elements.append(Paragraph("<i>Company-branded proposal layout</i>", styles['Center']))
        elements.append(Spacer(1, 8))

    elements.append(Paragraph(f"Quote #: {quotation.quote_number}", styles['Normal']))
    elements.append(Paragraph(f"Date: {quotation.created.strftime('%d-%m-%Y')}", styles['Normal']))
    elements.append(Paragraph(f"Valid Until: {quotation.valid_until.strftime('%d-%m-%Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Customer Details", styles['Heading2']))
    elements.append(Paragraph(f"Name: {customer_name}", styles['Normal']))
    elements.append(Paragraph(f"Address: {quotation.lead.address}, {quotation.lead.city}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {quotation.lead.phone}", styles['Normal']))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("System Details", styles['Heading2']))
    data_system = [
        ["System Size", f"{quotation.system_size} kW"],
        ["Panel Type", quotation.panel_type],
        ["Panel Count", str(quotation.panel_count)],
        ["Inverter Type", quotation.inverter_type],
        ["Mounting Type", quotation.mounting_type],
        ["Warranty", f"{quotation.warranty_years} years"],
        ["Est. Generation", f"{quotation.estimated_generation} kWh/year"],
    ]
    table_system = Table(data_system, colWidths=[150, 200])
    table_system.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), label_bg),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table_system)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Cost Breakdown", styles['Heading2']))
    data_items = [["Description", "Qty", "Unit Price (₹)", "Total (₹)"]]
    for item in quotation.items.all():
        data_items.append([
            item.description,
            str(item.quantity),
            f"{item.unit_price:,.2f}",
            f"{item.total_price:,.2f}"
        ])
    data_items.append(["", "", "Subtotal:", f"{quotation.subtotal:,.2f}"])
    data_items.append(["", "", f"GST ({quotation.gst_percentage}%):", f"{quotation.gst_amount:,.2f}"])
    data_items.append(["", "", "Total:", f"{quotation.total_cost:,.2f}"])
    data_items.append(["", "", "Subsidy:", f"-{quotation.subsidy_amount:,.2f}"])
    data_items.append(["", "", "Net Cost:", f"{quotation.net_cost:,.2f}"])

    table_items = Table(data_items, colWidths=[200, 50, 100, 100])
    table_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), accent),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), row_bg),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    table_items.setStyle(TableStyle([
        ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table_items)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Financial Analysis", styles['Heading2']))
    emi = quotation.monthly_emi if quotation.monthly_emi is not None else 0
    data_finance = [
        ["ROI", f"{quotation.roi}%"],
        ["Payback Period", f"{quotation.payback_years} years"],
        ["Monthly EMI", f"₹{emi:,.2f}"],
        ["Monthly Savings", f"₹{quotation.monthly_savings:,.2f}"],
    ]
    table_finance = Table(data_finance, colWidths=[150, 200])
    table_finance.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), label_bg),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table_finance)
    elements.append(Spacer(1, 20))

    if quotation.terms_conditions:
        elements.append(Paragraph("Terms & Conditions", styles['Heading2']))
        elements.append(Paragraph(quotation.terms_conditions.replace('\n', '<br/>'), styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer


@login_required
def quotation_pdf(request, pk):
    """
    CRM URL /new-lead/quotations/<pk>/pdf/ — delegate to ERP PDF (same record as detail).
    """
    from quotation import views as erp_quotation_views

    return erp_quotation_views.quotation_pdf(request, pk)

#
# @login_required
# def quotation_pdf(request, pk):
#     """
#     Generate PDF for quotation
#     """
#     if not REPORTLAB_AVAILABLE:
#         messages.error(request, 'PDF generation is not available. Please install reportlab.')
#         return redirect('quotation_detail', pk=pk)
#
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     try:
#         # Create PDF
#         buffer = io.BytesIO()
#         p = canvas.Canvas(buffer, pagesize=letter)
#         width, height = letter
#
#         # Helper to safely format numbers
#         def safe_currency(value):
#             if value is None:
#                 return "₹0"
#             try:
#                 # Convert Decimal to float and format
#                 val = float(value)
#                 return f"₹{val:,.2f}"
#             except (TypeError, ValueError):
#                 return "₹0"
#
#         def safe_float(value, default=0):
#             if value is None:
#                 return default
#             try:
#                 return float(value)
#             except (TypeError, ValueError):
#                 return default
#
#         def safe_str(value):
#             return str(value) if value is not None else ""
#
#         # Header
#         p.setFont("Helvetica-Bold", 20)
#         p.drawString(50, height - 50, "SOLAR QUOTATION")
#
#         p.setFont("Helvetica", 12)
#         p.drawString(50, height - 80, f"Quote #: {quotation.quote_number}")
#         p.drawString(50, height - 95, f"Date: {quotation.created.strftime('%d-%m-%Y')}")
#         p.drawString(50, height - 110,
#                      f"Valid Until: {quotation.valid_until.strftime('%d-%m-%Y') if quotation.valid_until else 'N/A'}")
#
#         # Customer Details
#         p.setFont("Helvetica-Bold", 14)
#         p.drawString(50, height - 140, "Customer Details")
#
#         p.setFont("Helvetica", 12)
#         p.drawString(50, height - 160, f"Name: {quotation.lead.name}")
#         p.drawString(50, height - 175, f"Address: {quotation.lead.address}")
#         p.drawString(50, height - 190, f"Phone: {quotation.lead.phone}")
#
#         # System Details
#         p.setFont("Helvetica-Bold", 14)
#         p.drawString(50, height - 220, "System Details")
#
#         p.setFont("Helvetica", 12)
#         p.drawString(50, height - 240, f"System Size: {safe_float(quotation.system_size)} kW")
#         p.drawString(50, height - 255, f"Panel Type: {safe_str(quotation.panel_type)}")
#         p.drawString(50, height - 270, f"Panel Count: {quotation.panel_count or 0}")
#         p.drawString(50, height - 285, f"Inverter: {safe_str(quotation.inverter_type)}")
#
#         # Cost Breakdown
#         p.setFont("Helvetica-Bold", 14)
#         p.drawString(50, height - 315, "Cost Breakdown")
#
#         y = height - 335
#         p.setFont("Helvetica-Bold", 10)
#         p.drawString(50, y, "Description")
#         p.drawString(300, y, "Qty")
#         p.drawString(350, y, "Unit Price")
#         p.drawString(450, y, "Total")
#
#         y -= 15
#         p.setFont("Helvetica", 10)
#
#         for item in quotation.items.all():
#             p.drawString(50, y, safe_str(item.description)[:30])
#             p.drawString(300, y, str(item.quantity or 0))
#             p.drawString(350, y, safe_currency(item.unit_price))
#             p.drawString(450, y, safe_currency(item.total_price))
#             y -= 15
#
#             if y < 50:  # New page
#                 p.showPage()
#                 y = height - 50
#
#         # Totals
#         y -= 10
#         p.setFont("Helvetica-Bold", 12)
#         p.drawString(350, y, "Subtotal:")
#         p.drawString(450, y, safe_currency(quotation.subtotal))
#
#         y -= 15
#         gst_percent = safe_float(quotation.gst_percentage, 0)
#         p.drawString(350, y, f"GST ({gst_percent:.1f}%):")
#         p.drawString(450, y, safe_currency(quotation.gst_amount))
#
#         y -= 15
#         p.drawString(350, y, "Total:")
#         p.drawString(450, y, safe_currency(quotation.total_cost))
#
#         y -= 15
#         p.drawString(350, y, "Subsidy:")
#         p.drawString(450, y, f"-{safe_currency(quotation.subsidy_amount)}")
#
#         y -= 15
#         p.setFont("Helvetica-Bold", 14)
#         p.drawString(350, y, "Net Cost:")
#         p.drawString(450, y, safe_currency(quotation.net_cost))
#
#         # Financial Analysis
#         y -= 30
#         p.setFont("Helvetica-Bold", 14)
#         p.drawString(50, y, "Financial Analysis")
#
#         y -= 20
#         p.setFont("Helvetica", 12)
#         p.drawString(50, y, f"ROI: {safe_float(quotation.roi, 0):.1f}%")
#         p.drawString(200, y, f"Payback Period: {safe_float(quotation.payback_years, 0):.1f} years")
#
#         y -= 15
#         p.drawString(50, y, f"Monthly EMI: {safe_currency(quotation.monthly_emi)}")
#         p.drawString(200, y, f"Monthly Savings: {safe_currency(quotation.monthly_savings)}")
#
#         # Terms
#         y -= 30
#         p.setFont("Helvetica-Bold", 12)
#         p.drawString(50, y, "Terms & Conditions:")
#
#         y -= 15
#         p.setFont("Helvetica", 10)
#         terms = (quotation.terms_conditions or "").split('\n')
#         for line in terms:
#             p.drawString(50, y, line[:80])  # Truncate long lines
#             y -= 12
#             if y < 30:
#                 p.showPage()
#                 y = height - 30
#
#         p.save()
#         buffer.seek(0)
#         return FileResponse(buffer, as_attachment=True, filename=f"Quotation_{quotation.quote_number}.pdf")
#
#     except Exception as e:
#         logger.error(f"PDF generation error: {e}")
#         messages.error(request, f'Error generating PDF: {str(e)}')
#         return redirect('quotation_detail', pk=quotation.id)

@login_required
def quotation_export(request):
    """
    Export quotations to CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="quotations_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Quote #', 'Lead', 'System Size', 'Total Cost', 'Status', 'Created By', 'Created Date'])

    quotations = Quotation.objects.all().select_related('lead', 'created_by')
    for quote in quotations:
        writer.writerow([
            quote.quote_number,
            quote.lead.name,
            f"{quote.system_size} kW",
            quote.total_cost,
            quote.get_status_display(),
            quote.created_by.get_full_name() if quote.created_by else '',
            quote.created.strftime('%Y-%m-%d'),
        ])

    return response