from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.utils import timezone

from .models import Quotation, SolarPanelCompany, InverterCompany, Representative, PlantCapacity, TermsAndCondition
from .forms import QuotationForm
# views.py
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .models import OtherItem, Quotation, SolarPanelCompany, InverterCompany
from django.db import connection
from django.views.decorators.csrf import csrf_protect

from customer.staff_access import (
    quotation_queryset_for_request,
    is_associate_staff,
)


def get_quotation_or_404_for_request(request, pk):
    """Associates may only open quotations assigned to them."""
    qs = quotation_queryset_for_request(request.user)
    return get_object_or_404(qs, pk=pk)


def get_active_terms_conditions():
    """Helper function to get active terms and conditions, handling bit varying type issue"""
    # Use raw SQL to fetch all data and create model instances directly
    # This completely bypasses Django ORM to avoid bit varying boolean comparison errors
    try:
        with connection.cursor() as cursor:
            # Use CAST to text to avoid any boolean comparison issues
            cursor.execute("""
                SELECT 
                    id, 
                    content, 
                    CAST(has_yellow_background AS TEXT) as has_yellow_text,
                    CAST(is_active AS TEXT) as is_active_text,
                    created_at
                FROM quotation_termsandcondition
            """)
            rows = cursor.fetchall()

            # Create model instances directly from raw SQL results
            terms_list = []
            for row in rows:
                # Check if is_active is truthy by checking text value
                is_active_text = str(row[3]).lower() if row[3] else ''
                is_active_value = is_active_text in ('1', 't', 'true', 'y', 'yes')

                if is_active_value:
                    term = TermsAndCondition()
                    term.id = row[0]
                    term.content = row[1] if row[1] else ''
                    # Convert has_yellow_background from text
                    has_yellow_text = str(row[2]).lower() if row[2] else ''
                    term.has_yellow_background = has_yellow_text in ('1', 't', 'true', 'y', 'yes')
                    term.is_active = True  # We already filtered for active ones
                    term.created_at = row[4] if row[4] else None
                    # Mark as saved to avoid save() calls and prevent database queries
                    from django.db.models.base import ModelState
                    term._state = ModelState()
                    term._state.adding = False
                    term._state.db = 'default'
                    terms_list.append(term)

            return terms_list
    except Exception as e:
        # If that fails, return empty list and log the error
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching terms and conditions: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

# def quotation_list(request):
#     quotations = Quotation.objects.all().order_by('-date', '-created_at')
#     return render(request, 'quotation/quotation_list.html', {'quotations': quotations})

#
# def quotation_list(request):
#     quotations = Quotation.objects.all()
#
#     # Sort by quotation number in descending order
#     # Handle quotation numbers like "1000", "1000_1", "1000_2", "1001", etc.
#     def sort_key(q):
#         quotation_no = q.quotation_no or "0"
#         # Split into base number and revision
#         parts = quotation_no.split('_')
#         base_no = parts[0]
#         revision = int(parts[1]) if len(parts) > 1 else 0
#
#         try:
#             base_num = int(base_no)
#         except (ValueError, TypeError):
#             base_num = 0
#
#         # Return tuple for sorting: (base_num, revision) - negative for descending
#         # We'll sort in reverse, so return positive values
#         return (base_num, revision)
#
#     # Sort quotations by quotation number in descending order
#     quotations_list = list(quotations)
#     quotations_list.sort(key=sort_key, reverse=True)
#
#     # Determine which quotations are the latest revisions
#     quotation_groups = {}
#     for quotation in quotations_list:
#         base_quotation_no = quotation.quotation_no.split('_')[0]  # Get base number without revision
#         if base_quotation_no not in quotation_groups:
#             quotation_groups[base_quotation_no] = quotation.pk
#         else:
#             # If we already have this base number, keep the one with latest created_at
#             existing_quotation = Quotation.objects.get(pk=quotation_groups[base_quotation_no])
#             if quotation.created_at > existing_quotation.created_at:
#                 quotation_groups[base_quotation_no] = quotation.pk
#
#     # Mark latest revisions
#     for quotation in quotations_list:
#         quotation.is_latest_revision = (quotation.pk == quotation_groups.get(quotation.quotation_no.split('_')[0]))
#
#     return render(request, 'quotation/quotation_list.html', {'quotations': quotations_list})


#
# def quotation_list(request):
#     quotations = Quotation.objects.all()
#
#     def sort_key(q):
#         quotation_no = q.quotation_no or "0"
#         parts = quotation_no.split('_')
#         base_no = parts[0]
#         revision = int(parts[1]) if len(parts) > 1 else 0
#         try:
#             base_num = int(base_no)
#         except (ValueError, TypeError):
#             base_num = 0
#         return (base_num, revision)
#
#     quotations_list = list(quotations)
#     quotations_list.sort(key=sort_key, reverse=True)
#
#     quotation_groups = {}
#     for quotation in quotations_list:
#         base_no = quotation.quotation_no.split('_')[0]
#         if base_no not in quotation_groups:
#             quotation_groups[base_no] = quotation.pk
#         else:
#             existing = Quotation.objects.get(pk=quotation_groups[base_no])
#             if quotation.created_at and existing.created_at and quotation.created_at > existing.created_at:
#                 quotation_groups[base_no] = quotation.pk
#
#     for quotation in quotations_list:
#         quotation.is_latest_revision = (
#             quotation.pk == quotation_groups.get(quotation.quotation_no.split('_')[0])
#         )
#
#     return render(
#         request,
#         'quotation/quotation_list.html',
#         {'quotations': quotations_list}
#     )

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Quotation

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Quotation

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Quotation


# def quotation_list(request):
#     quotations = Quotation.objects.all()
#
#     def sort_key(q):
#         parts = q.quotation_no.split("_")
#         base = int(parts[0])
#         rev = int(parts[1]) if len(parts) > 1 else 0
#         return (base, rev)
#
#     quotations = sorted(list(quotations), key=sort_key, reverse=True)
#
#     latest_map = {}
#     for q in quotations:
#         q.base_no = q.quotation_no.split("_")[0]
#         if q.base_no not in latest_map:
#             latest_map[q.base_no] = q
#
#     for q in quotations:
#         latest = latest_map[q.base_no]
#         q.is_latest_revision = (q.id == latest.id)
#         q.latest_confirmed = latest.is_confirmed   # ✅ NEW FLAG
#
#         # Hide only old revisions when latest is confirmed
#         q.hide_row = (
#             q.latest_confirmed and not q.is_latest_revision
#         )
#
#     return render(
#         request,
#         "quotation/quotation_list.html",
#         {"quotations": quotations}
#     )

from collections import defaultdict
from collections import defaultdict

def quotation_list(request):
    mode = (request.GET.get("mode") or "latest").strip().lower()
    if mode not in {"latest", "all"}:
        mode = "latest"

    quotations = list(
        quotation_queryset_for_request(request.user).select_related(
            "assigned_associate", "plant_capacity_kw"
        )
    )

    def sort_key(q):
        parts = q.quotation_no.split("_")
        base = int(parts[0])
        rev = int(parts[1]) if len(parts) > 1 else 0
        return (base, rev)

    quotations = sorted(list(quotations), key=sort_key, reverse=True)

    latest_map = {}
    count_map = defaultdict(int)

    def _format_display_date(raw_value):
        if not raw_value:
            return "-"
        try:
            # Datetime/date objects
            if hasattr(raw_value, "strftime"):
                return raw_value.strftime("%d.%m.%Y")
            # String values from legacy rows
            raw_str = str(raw_value).strip()
            if not raw_str:
                return "-"
            for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    from datetime import datetime
                    return datetime.strptime(raw_str[:19], fmt).strftime("%d.%m.%Y")
                except Exception:
                    continue
            # Already in date-like text, try first 10 chars as YYYY-MM-DD
            if len(raw_str) >= 10:
                from datetime import datetime
                try:
                    return datetime.strptime(raw_str[:10], "%Y-%m-%d").strftime("%d.%m.%Y")
                except Exception:
                    pass
        except Exception:
            pass
        return "-"

    # Count records per quotation
    for q in quotations:
        q.base_no = q.quotation_no.split("_")[0]
        count_map[q.base_no] += 1

        if q.base_no not in latest_map:
            latest_map[q.base_no] = q

    for q in quotations:
        latest = latest_map[q.base_no]

        q.is_latest_revision = (q.id == latest.id)
        q.latest_confirmed = latest.is_confirmed
        q.display_date = _format_display_date(getattr(q, "date", None) or getattr(q, "created_at", None))

        q.has_multiple = count_map[q.base_no] > 1

        # ✅ number of previous quotations
        q.previous_count = count_map[q.base_no] - 1

        # Hide old revisions initially in "latest" mode only.
        q.hide_row = (mode == "latest") and q.has_multiple and not q.is_latest_revision

    return render(
        request,
        "quotation/quotation_list.html",
        {
            "quotations": quotations,
            "quotation_initial_mode": mode,
        }
    )

# def quotation_list(request):
#     quotations = Quotation.objects.all()
#
#     def sort_key(q):
#         parts = q.quotation_no.split("_")
#         base = int(parts[0])
#         rev = int(parts[1]) if len(parts) > 1 else 0
#         return (base, rev)
#
#     quotations = sorted(list(quotations), key=sort_key, reverse=True)
#
#     latest_map = {}
#     count_map = defaultdict(int)
#
#     # Count how many records per base quotation
#     for q in quotations:
#         q.base_no = q.quotation_no.split("_")[0]
#         count_map[q.base_no] += 1
#
#         if q.base_no not in latest_map:
#             latest_map[q.base_no] = q
#
#     for q in quotations:
#         latest = latest_map[q.base_no]
#
#         q.is_latest_revision = (q.id == latest.id)
#         q.latest_confirmed = latest.is_confirmed
#
#         # ✅ NEW FLAG
#         q.has_multiple = count_map[q.base_no] > 1
#
#         # Hide older revisions initially
#         q.hide_row = q.has_multiple and not q.is_latest_revision
#
#     return render(
#         request,
#         "quotation/quotation_list.html",
#         {"quotations": quotations}
#     )

@csrf_exempt
def confirm_quotation(request, pk):
    if request.method == "POST":
        q = get_quotation_or_404_for_request(request, pk)

        q.payment_type = request.POST.get("payment_type")
        q.payment_mode = request.POST.get("payment_mode")
        q.hybrid_mode = request.POST.get("hybrid_mode")
        q.po_order_no = request.POST.get("po_order_no")
        q.po_date = request.POST.get("po_date") or None
        q.is_confirmed = True
        q.save()

        return JsonResponse({"status": "success"})


# In your views.py (quotation app), add these missing views:

@csrf_exempt
def check_quotation_confirmed(request, pk):
    """Check if quotation is already confirmed"""
    try:
        quotation = quotation_queryset_for_request(request.user).get(pk=pk)
        return JsonResponse({
            'is_confirmed': quotation.is_confirmed,
            'consumer_type': quotation.consumer_type
        })
    except Quotation.DoesNotExist:
        return JsonResponse({'error': 'Quotation not found'}, status=404)


@csrf_exempt
# def get_quotation_details(request, pk):
#     """Get quotation details for conversion"""
#     try:
#         quotation = Quotation.objects.get(pk=pk)
#
#         # Split full name into first, middle, last
#         name_parts = quotation.consumer_name.split()
#         first_name = name_parts[0] if len(name_parts) > 0 else ""
#         last_name = name_parts[-1] if len(name_parts) > 1 else ""
#         middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
#
#         # If only two words, first becomes first name, second becomes last name
#         if len(name_parts) == 2:
#             first_name = name_parts[0]
#             last_name = name_parts[1]
#             middle_name = ""
#
#         # Get plant capacity - handle PlantCapacity object properly
#         plant_capacity = 0
#         if quotation.plant_capacity_kw:
#             # Check if plant_capacity_kw is a ForeignKey to PlantCapacity
#             if hasattr(quotation.plant_capacity_kw, '__str__'):
#                 # Try to extract numeric value from string representation
#                 import re
#                 capacity_str = str(quotation.plant_capacity_kw)
#                 match = re.search(r'(\d+(\.\d+)?)', capacity_str)
#                 if match:
#                     plant_capacity = float(match.group(1))
#
#         data = {
#             'consumer_type': quotation.consumer_type,
#             'project_type': quotation.project_type,
#             'plant_capacity': plant_capacity,
#             'phase': quotation.inv_phase,
#             'consumer_no': quotation.consumer_no,
#             'consumer_full_name': quotation.consumer_name,
#             'first_name': first_name,
#             'middle_name': middle_name,
#             'last_name': last_name,
#             'address': quotation.consumer_address1,
#             'city': quotation.consumer_address2,  # You might need to add city field to quotation model
#             'state': quotation.consumer_state,
#             'email': quotation.consumer_email,
#             'phone': quotation.consumer_mobile,
#             'po_order_no': quotation.po_order_no,
#             'po_date': quotation.po_date.strftime('%Y-%m-%d') if quotation.po_date else None,
#         }
#         return JsonResponse(data)
#     except Quotation.DoesNotExist:
#         return JsonResponse({'error': 'Quotation not found'}, status=404)
@csrf_exempt
def get_quotation_details(request, pk):
    """Get quotation details for conversion"""
    try:
        quotation = quotation_queryset_for_request(request.user).get(pk=pk)

        print(f"DEBUG: Getting quotation details for ID: {pk}")
        print(f"DEBUG: Consumer Name: {quotation.consumer_name}")
        print(f"DEBUG: Project Type: {quotation.project_type}")
        print(f"DEBUG: Phase: {quotation.inv_phase}")

        # Split full name into first, middle, last
        name_parts = quotation.consumer_name.split()
        print(f"DEBUG: Name parts: {name_parts}")

        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[-1] if len(name_parts) > 1 else ""
        middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""

        # If only two words, first becomes first name, second becomes last name
        if len(name_parts) == 2:
            first_name = name_parts[0]
            last_name = name_parts[1]
            middle_name = ""

        print(f"DEBUG: First: {first_name}, Middle: {middle_name}, Last: {last_name}")

        # Get plant capacity
        plant_capacity = 0
        if quotation.plant_capacity_kw:
            if hasattr(quotation.plant_capacity_kw, '__str__'):
                import re
                capacity_str = str(quotation.plant_capacity_kw)
                print(f"DEBUG: Capacity string: {capacity_str}")
                match = re.search(r'(\d+(\.\d+)?)', capacity_str)
                if match:
                    plant_capacity = float(match.group(1))

        print(f"DEBUG: Plant Capacity: {plant_capacity}")

        # Get city from consumer_address2 if available
        city = quotation.consumer_address2 if quotation.consumer_address2 else ''

        data = {
            'consumer_type': quotation.consumer_type,
            'project_type': quotation.project_type,
            'plant_capacity': plant_capacity,
            'phase': quotation.inv_phase,
            'consumer_no': quotation.consumer_no,
            'consumer_full_name': quotation.consumer_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'address': quotation.consumer_address1,
            'city': city,
            'state': quotation.consumer_state,
            'email': quotation.consumer_email,
            'phone': quotation.consumer_mobile,
            'po_order_no': quotation.po_order_no,
            'po_date': quotation.po_date.strftime('%Y-%m-%d') if quotation.po_date else None,
            'comp_name': quotation.consumer_name,
        }

        print(f"DEBUG: Final data being sent: {data}")

        return JsonResponse(data)
    except Quotation.DoesNotExist:
        print(f"DEBUG: Quotation {pk} not found")
        return JsonResponse({'error': 'Quotation not found'}, status=404)
    except Exception as e:
        print(f"DEBUG: Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def store_quotation_data(request):
    """Store quotation data in session for form pre-filling"""
    import json
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Store both the data and timestamp to avoid session conflicts
            request.session['quotation_data'] = {
                'data': data.get('data', {}),
                'timestamp': timezone.now().timestamp(),
                'quotation_id': data.get('quotation_id')
            }
            request.session.modified = True  # Mark session as modified
            return JsonResponse({'status': 'success', 'message': 'Data stored successfully'})
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON', 'details': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Server error', 'details': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

#
# def quotation_list(request):
#     quotations = Quotation.objects.all()
#
#     def sort_key(q):
#         quotation_no = q.quotation_no or "0"
#         parts = quotation_no.split('_')
#         base_no = parts[0]
#         revision = int(parts[1]) if len(parts) > 1 else 0
#         try:
#             base_num = int(base_no)
#         except:
#             base_num = 0
#         return (base_num, revision)
#
#     quotations_list = list(quotations)
#     quotations_list.sort(key=sort_key, reverse=True)
#
#     quotation_groups = {}
#     for q in quotations_list:
#         base_no = q.quotation_no.split('_')[0]
#         if base_no not in quotation_groups:
#             quotation_groups[base_no] = q.pk
#         else:
#             old = Quotation.objects.get(pk=quotation_groups[base_no])
#             if q.created_at > old.created_at:
#                 quotation_groups[base_no] = q.pk
#
#     for q in quotations_list:
#         q.is_latest_revision = (
#             q.pk == quotation_groups.get(q.quotation_no.split('_')[0])
#         )
#
#     return render(request, "quotation/quotation_list.html", {
#         "quotations": quotations_list
#     })
#
#
# @csrf_exempt
# def confirm_quotation(request, pk):
#     if request.method == "POST":
#         q = get_object_or_404(Quotation, pk=pk)
#
#         q.payment_type = request.POST.get("payment_type")
#         q.payment_mode = request.POST.get("payment_mode")
#         q.hybrid_mode = request.POST.get("hybrid_mode")
#         q.po_order_no = request.POST.get("po_order_no")
#         q.po_date = request.POST.get("po_date") or None
#         q.is_confirmed = True
#
#         q.save()
#         return JsonResponse({"status": "success"})



#
# def revise_quotation(request, pk):
#     original_quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (original_quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         form = QuotationForm(request.POST)
#
#         if form.is_valid():
#             # Create new quotation instance (don't save yet)
#             new_quotation = form.save(commit=False)
#
#             # Generate new quotation number with revision
#             base_quotation_no = original_quotation.quotation_no.split('_')[0]
#
#             # Find the highest revision number for this base quotation
#             existing_revisions = Quotation.objects.filter(
#                 quotation_no__startswith=base_quotation_no + '_'
#             )
#
#             if existing_revisions.exists():
#                 # Get the highest revision number
#                 max_revision = 0
#                 for rev in existing_revisions:
#                     try:
#                         rev_num = int(rev.quotation_no.split('_')[1])
#                         if rev_num > max_revision:
#                             max_revision = rev_num
#                     except (IndexError, ValueError):
#                         continue
#                 new_revision = max_revision + 1
#             else:
#                 # This is the first revision
#                 new_revision = 1
#
#             new_quotation.quotation_no = f"{base_quotation_no}_{new_revision}"
#             new_quotation.save()
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             new_quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             new_quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             new_quotation.inverter_companies.set(inverter_ids)
#
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inv_names.append(inv.name)
#                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                 inv_warranties.append(wt)
#
#             new_quotation.inverter_company_names = " / ".join(inv_names)
#             new_quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES
#             rep_ids = request.POST.getlist('representatives')
#             new_quotation.representatives.set(rep_ids)
#
#             # Store textual representation for PDF
#             rep_qs = Representative.objects.filter(id__in=rep_ids)
#             rep_texts = [f"{i + 1}. {r.name} - {r.contact}" for i, r in enumerate(rep_qs)]
#             new_quotation.representative_names = "\n".join(rep_texts)
#
#             # OTHER ITEMS
#             static_qs = form.cleaned_data.get("other_items") or []
#             static_names = list(static_qs.values_list("name", flat=True))
#             dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#
#             combined = []
#             for n in static_names + dynamic_inputs:
#                 if n and n not in combined:
#                     combined.append(n)
#
#             new_quotation.other_details = " / ".join(combined)
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 new_quotation.net_amount = net_input
#                 new_quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 new_quotation.final_amount = final_input
#                 new_quotation.calculate_from_final()
#
#             new_quotation.save()
#             return redirect("quotation:quotation_pdf", pk=new_quotation.pk)
#
#     else:
#         # GET - create form pre-filled with original quotation data
#         form = QuotationForm(initial={
#             'consumer_name': original_quotation.consumer_name,
#             'consumer_address1': original_quotation.consumer_address1,
#             'consumer_address2': original_quotation.consumer_address2,
#             'consumer_no': original_quotation.consumer_no,
#             'consumer_mobile': original_quotation.consumer_mobile,
#             'date': original_quotation.date,
#             'plant_capacity_kw': original_quotation.plant_capacity_kw,
#             'employee_name': original_quotation.employee_name,
#             'panel_type': original_quotation.panel_type,
#             'panel_capacity_watt': original_quotation.panel_capacity_watt,
#             'panel_qty': original_quotation.panel_qty,
#             'panel_manufacturing_warranty': original_quotation.panel_manufacturing_warranty,
#             'panel_performance_warranty': original_quotation.panel_performance_warranty,
#             'inv_phase': original_quotation.inv_phase,
#             'inv_capacity_kw': original_quotation.inv_capacity_kw,
#             'inverter_qty': original_quotation.inverter_qty,
#             'structure_type': original_quotation.structure_type,
#             'structure_back_height_ft': original_quotation.structure_back_height_ft,
#             'structure_front_height_ft': original_quotation.structure_front_height_ft,
#             'structure_warranty': original_quotation.structure_warranty,
#             'special_discount': original_quotation.special_discount,
#             'gst_5_percent': original_quotation.gst_5_percent,
#             'gst_18_percent': original_quotation.gst_18_percent,
#             'net_amount_input': original_quotation.net_amount,
#             'final_amount_input': original_quotation.final_amount,
#         })
#
#         # Pre-check static other_items checkboxes
#         static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#         if static_names_to_check:
#             checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#             form.fields["other_items"].initial = checked_qs
#
#     # Prepare warranty mapping
#     stored_names = [n.strip() for n in (original_quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (original_quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "original_quotation": original_quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/revise_quotation.html", context)

#
# def revise_quotation(request, pk):
#     original_quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#     terms_conditions = TermsAndCondition.objects.filter(is_active=True)  # ADD THIS
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (original_quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         form = QuotationForm(request.POST)
#
#         if form.is_valid():
#             # Create new quotation instance (don't save yet)
#             new_quotation = form.save(commit=False)
#
#             # Handle system_na checkbox - clear capacities if NA is checked
#             system_na = form.cleaned_data.get('system_na', False)
#             if system_na:
#                 new_quotation.dc_capacity = None
#                 new_quotation.ac_capacity = None
#             else:
#                 # Ensure capacities are saved if not NA
#                 new_quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
#                 new_quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
#
#             # Generate new quotation number with revision
#             base_quotation_no = original_quotation.quotation_no.split('_')[0]
#
#             # Find the highest revision number for this base quotation
#             existing_revisions = Quotation.objects.filter(
#                 quotation_no__startswith=base_quotation_no + '_'
#             )
#
#             if existing_revisions.exists():
#                 # Get the highest revision number
#                 max_revision = 0
#                 for rev in existing_revisions:
#                     try:
#                         rev_num = int(rev.quotation_no.split('_')[1])
#                         if rev_num > max_revision:
#                             max_revision = rev_num
#                     except (IndexError, ValueError):
#                         continue
#                 new_revision = max_revision + 1
#             else:
#                 # This is the first revision
#                 new_revision = 1
#
#             new_quotation.quotation_no = f"{base_quotation_no}_{new_revision}"
#             new_quotation.save()
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             new_quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             new_quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             new_quotation.inverter_companies.set(inverter_ids)
#
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inv_names.append(inv.name)
#                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                 inv_warranties.append(wt)
#
#             new_quotation.inverter_company_names = " / ".join(inv_names)
#             new_quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES
#             rep_ids = request.POST.getlist('representatives')
#             new_quotation.representatives.set(rep_ids)
#
#             # Store textual representation for PDF
#             rep_qs = Representative.objects.filter(id__in=rep_ids)
#             rep_texts = [f"{i + 1}. {r.name} - {r.contact}" for i, r in enumerate(rep_qs)]
#             new_quotation.representative_names = "\n".join(rep_texts)
#
#             # TERMS & CONDITIONS - ADD THIS SECTION
#             terms_ids = request.POST.getlist('terms_conditions')
#             new_quotation.terms_conditions.set(terms_ids)
#
#             # Store terms content for PDF (ordered by PK)
#             terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
#             terms_texts = []
#             for i, term in enumerate(terms_qs):
#                 terms_texts.append(f"{i + 1}. {term.content}")
#             new_quotation.terms_conditions_text = "\n".join(terms_texts)
#
#             # OTHER ITEMS
#             static_qs = form.cleaned_data.get("other_items") or []
#             static_names = list(static_qs.values_list("name", flat=True))
#             dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#
#             combined = []
#             for n in static_names + dynamic_inputs:
#                 if n and n not in combined:
#                     combined.append(n)
#
#             new_quotation.other_details = " / ".join(combined)
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 new_quotation.net_amount = net_input
#                 new_quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 new_quotation.final_amount = final_input
#                 new_quotation.calculate_from_final()
#
#             new_quotation.save()
#             return redirect("quotation:quotation_pdf", pk=new_quotation.pk)
#
#     else:
#         # GET - create form pre-filled with original quotation data
#         form = QuotationForm(initial={
#             'consumer_type': original_quotation.consumer_type,  # ADD CONSUMER TYPE
#             'consumer_no': original_quotation.consumer_no,  # ADD CONSUMER NO
#             'title': original_quotation.title,  # ADD TITLE
#             'consumer_name': original_quotation.consumer_name,
#             'consumer_address1': original_quotation.consumer_address1,
#             'consumer_address2': original_quotation.consumer_address2,
#             'consumer_no': original_quotation.consumer_no,
#             'consumer_mobile': original_quotation.consumer_mobile,
#             'date': original_quotation.date,
#             'plant_capacity_kw': original_quotation.plant_capacity_kw,
#             'employee_name': original_quotation.employee_name,
#             'panel_type': original_quotation.panel_type,
#             'panel_capacity_watt': original_quotation.panel_capacity_watt,
#             'panel_qty': original_quotation.panel_qty,
#             'panel_manufacturing_warranty': original_quotation.panel_manufacturing_warranty,
#             'panel_performance_warranty': original_quotation.panel_performance_warranty,
#             'inv_phase': original_quotation.inv_phase,
#             'inv_capacity_kw': original_quotation.inv_capacity_kw,
#             'inverter_qty': original_quotation.inverter_qty,
#             'structure_type': original_quotation.structure_type,
#             'structure_back_height_ft': original_quotation.structure_back_height_ft,
#             'structure_front_height_ft': original_quotation.structure_front_height_ft,
#             'structure_warranty': original_quotation.structure_warranty,
#             'special_discount': original_quotation.special_discount,
#             'gst_5_percent': original_quotation.gst_5_percent,
#             'gst_18_percent': original_quotation.gst_18_percent,
#             'net_amount_input': original_quotation.net_amount,
#             'final_amount_input': original_quotation.final_amount,
#             'dc_capacity': original_quotation.dc_capacity,  # ADD DC CAPACITY
#             'ac_capacity': original_quotation.ac_capacity,  # ADD AC CAPACITY
#             'system_na': original_quotation.system_na,  # ADD SYSTEM NA
#         })
#
#         # Pre-check static other_items checkboxes
#         static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#         if static_names_to_check:
#             checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#             form.fields["other_items"].initial = checked_qs
#
#     # Prepare warranty mapping
#     stored_names = [n.strip() for n in (original_quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (original_quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "original_quotation": original_quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,  # ADD THIS
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/revise_quotation.html", context)

#
# def revise_quotation(request, pk):
#     original_quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#     terms_conditions = get_active_terms_conditions()
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (original_quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         form = QuotationForm(request.POST)
#
#         # Set terms_conditions queryset before validation to avoid "not one of the available choices" error
#         # Use raw SQL to get active term IDs to avoid boolean comparison issues
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM quotation_termsandcondition
#                     WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
#                 """)
#                 active_term_ids = [row[0] for row in cursor.fetchall()]
#             # Set queryset to include only active terms (filtering by ID only, no boolean comparison)
#             if active_term_ids:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=active_term_ids)
#             else:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#         except Exception as e:
#             # If query fails, set to empty queryset
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not set terms_conditions queryset: {e}")
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         if form.is_valid():
#             # Create new quotation instance (don't save yet)
#             new_quotation = form.save(commit=False)
#
#             # Handle system_na checkbox - clear capacities if NA is checked
#             system_na = form.cleaned_data.get('system_na', False)
#             if system_na:
#                 new_quotation.dc_capacity = None
#                 new_quotation.ac_capacity = None
#             else:
#                 # Ensure capacities are saved if not NA
#                 new_quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
#                 new_quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
#
#             # Set system_na to False - we'll update it via raw SQL immediately after save
#             new_quotation.system_na = False
#
#             # Handle Other Details NA checkbox
#             na_other_checked = request.POST.get("na_other_checkbox") == "on"
#             if na_other_checked:
#                 # Clear other details if NA is checked
#                 new_quotation.other_details = ""
#             else:
#                 # Process other items only if NA is not checked
#                 static_qs = form.cleaned_data.get("other_items") or []
#                 static_names = []
#
#                 # Handle both QuerySet and list cases
#                 for item in static_qs:
#                     if hasattr(item, 'name'):
#                         static_names.append(item.name)
#
#                 dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#
#                 combined = []
#                 for n in static_names + dynamic_inputs:
#                     if n and n not in combined:
#                         combined.append(n)
#
#                 new_quotation.other_details = " / ".join(combined)
#
#             # Generate new quotation number with revision
#             base_quotation_no = original_quotation.quotation_no.split('_')[0]
#
#             # Find the highest revision number for this base quotation
#             existing_revisions = Quotation.objects.filter(
#                 quotation_no__startswith=base_quotation_no + '_'
#             )
#
#             if existing_revisions.exists():
#                 # Get the highest revision number
#                 max_revision = 0
#                 for rev in existing_revisions:
#                     try:
#                         rev_num = int(rev.quotation_no.split('_')[1])
#                         if rev_num > max_revision:
#                             max_revision = rev_num
#                     except (IndexError, ValueError):
#                         continue
#                 new_revision = max_revision + 1
#             else:
#                 # This is the first revision
#                 new_revision = 1
#
#             new_quotation.quotation_no = f"{base_quotation_no}_{new_revision}"
#             new_quotation.save()
#
#             # Update system_na using raw SQL to handle bit varying type
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s::bit varying
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', new_quotation.id])
#
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             new_quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             new_quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             new_quotation.inverter_companies.set(inverter_ids)
#
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inv_names.append(inv.name)
#                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                 inv_warranties.append(wt)
#
#             new_quotation.inverter_company_names = " / ".join(inv_names)
#             new_quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES - Use selection order if provided, otherwise preserve existing order
#             rep_ids = request.POST.getlist('representatives')
#             rep_order_str = request.POST.get('representatives_order', '').strip()
#
#             # If order is provided, use it
#             if rep_order_str:
#                 # Parse the order from comma-separated string
#                 ordered_rep_ids = [rid.strip() for rid in rep_order_str.split(',') if rid.strip() in rep_ids]
#                 # Add any remaining reps that weren't in the order (shouldn't happen, but safety)
#                 for rid in rep_ids:
#                     if rid not in ordered_rep_ids:
#                         ordered_rep_ids.append(rid)
#                 rep_ids = ordered_rep_ids
#             else:
#                 # No order provided - preserve existing order from original quotation
#                 # Parse representative_names to extract the order (most reliable source)
#                 if original_quotation.representative_names:
#                     # representative_names format: "1. Name - Contact\n2. Name - Contact\n..."
#                     # Create a mapping of all existing representatives
#                     all_reps = {str(r.id): r for r in Representative.objects.all()}
#                     existing_reps = {str(r.id): r for r in original_quotation.representatives.all()}
#
#                     # Parse lines from representative_names
#                     lines = original_quotation.representative_names.strip().split('\n')
#                     ordered_rep_ids = []
#
#                     for line in lines:
#                         line = line.strip()
#                         if not line or '.' not in line:
#                             continue
#
#                         # Extract name from line (format: "1. Name - Contact" or "1. Name")
#                         # Remove number prefix (e.g., "1. ")
#                         name_part = line.split('.', 1)[1].strip()
#                         # Remove contact part if exists (e.g., "Name - Contact" -> "Name")
#                         name = name_part.split(' - ', 1)[0].strip()
#
#                         # Find matching representative by name
#                         for rep_id, rep in existing_reps.items():
#                             if rep.name.strip() == name.strip() and rep_id in rep_ids:
#                                 if rep_id not in ordered_rep_ids:
#                                     ordered_rep_ids.append(rep_id)
#                                 break
#
#                     # Add any new reps that weren't in the original order
#                     for rid in rep_ids:
#                         if rid not in ordered_rep_ids:
#                             ordered_rep_ids.append(rid)
#
#                     rep_ids = ordered_rep_ids if ordered_rep_ids else rep_ids
#
#             new_quotation.representatives.set(rep_ids)
#
#             # Store textual representation for PDF in selection order
#             # Create a mapping of ID to Representative for quick lookup
#             rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
#             rep_texts = []
#             for i, rep_id in enumerate(rep_ids):
#                 if rep_id in rep_dict:
#                     r = rep_dict[rep_id]
#                     contact_str = f" - {r.contact}" if r.contact else ""
#                     rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
#             new_quotation.representative_names = "\n".join(rep_texts)
#
#             # TERMS & CONDITIONS
#             terms_ids = request.POST.getlist('terms_conditions')
#             new_quotation.terms_conditions.set(terms_ids)
#
#             # Store terms content for PDF (ordered by PK)
#             terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
#             terms_texts = []
#             for i, term in enumerate(terms_qs):
#                 terms_texts.append(f"{i + 1}. {term.content}")
#             new_quotation.terms_conditions_text = "\n".join(terms_texts)
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 new_quotation.net_amount = net_input
#                 new_quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 new_quotation.final_amount = final_input
#                 new_quotation.calculate_from_final()
#
#             new_quotation.save()
#
#             # Update system_na again after final save to ensure it's persisted
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s::bit varying
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', new_quotation.id])
#
#             return redirect("quotation:quotation_pdf", pk=new_quotation.pk)
#
#     else:
#         # GET - create form pre-filled with original quotation data
#         # Format date for HTML date input (YYYY-MM-DD format)
#         formatted_date = None
#         if original_quotation.date:
#             if hasattr(original_quotation.date, 'strftime'):
#                 # It's a datetime object
#                 formatted_date = original_quotation.date.strftime('%Y-%m-%d')
#             elif isinstance(original_quotation.date, str):
#                 # It's already a string, try to parse and reformat
#                 try:
#                     from datetime import datetime
#                     # Try common date formats
#                     for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S%z']:
#                         try:
#                             parsed_date = datetime.strptime(original_quotation.date, fmt)
#                             formatted_date = parsed_date.strftime('%Y-%m-%d')
#                             break
#                         except ValueError:
#                             continue
#                     # If parsing failed, use original string if it's already in YYYY-MM-DD format
#                     if not formatted_date and len(original_quotation.date) >= 10:
#                         formatted_date = original_quotation.date[:10]  # Take first 10 chars (YYYY-MM-DD)
#                 except Exception:
#                     formatted_date = original_quotation.date
#             else:
#                 formatted_date = str(original_quotation.date)
#
#         form = QuotationForm(initial={
#             'consumer_type': original_quotation.consumer_type,
#             'consumer_no': original_quotation.consumer_no,
#             'title': original_quotation.title,
#             'consumer_name': original_quotation.consumer_name,
#             'consumer_address1': original_quotation.consumer_address1,
#             'consumer_address2': original_quotation.consumer_address2,
#             'consumer_no': original_quotation.consumer_no,
#             'consumer_mobile': original_quotation.consumer_mobile,
#             'date': formatted_date,
#             'plant_capacity_kw': original_quotation.plant_capacity_kw,
#             'employee_name': original_quotation.employee_name,
#             'panel_type': original_quotation.panel_type,
#             'panel_capacity_watt': original_quotation.panel_capacity_watt,
#             'panel_qty': original_quotation.panel_qty,
#             'panel_manufacturing_warranty': original_quotation.panel_manufacturing_warranty,
#             'panel_performance_warranty': original_quotation.panel_performance_warranty,
#             'inv_phase': original_quotation.inv_phase,
#             'inv_capacity_kw': original_quotation.inv_capacity_kw,
#             'inverter_qty': original_quotation.inverter_qty,
#             'structure_type': original_quotation.structure_type,
#             'structure_back_height_ft': original_quotation.structure_back_height_ft,
#             'structure_front_height_ft': original_quotation.structure_front_height_ft,
#             'structure_warranty': original_quotation.structure_warranty,
#             'special_discount': original_quotation.special_discount,
#             'gst_5_percent': original_quotation.gst_5_percent,
#             'gst_18_percent': original_quotation.gst_18_percent,
#             'net_amount_input': original_quotation.net_amount,
#             'final_amount_input': original_quotation.final_amount,
#             'dc_capacity': original_quotation.dc_capacity,
#             'ac_capacity': original_quotation.ac_capacity,
#             'system_na': original_quotation.system_na,
#         })
#
#         # CRITICAL: Set initial terms_conditions from the original quotation instance
#         # This ensures the checkboxes are pre-checked with existing terms
#         existing_term_ids = list(original_quotation.terms_conditions.values_list('id', flat=True))
#         if existing_term_ids:
#             form.initial['terms_conditions'] = existing_term_ids
#             # Also set on the field itself
#             form.fields['terms_conditions'].initial = existing_term_ids
#
#         # Pre-check static other_items checkboxes only if other_details exists
#         if original_quotation.other_details:
#             static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#             if static_names_to_check:
#                 checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#                 form.fields["other_items"].initial = checked_qs
#
#     # Prepare warranty mapping
#     stored_names = [n.strip() for n in (original_quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (original_quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "original_quotation": original_quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/revise_quotation.html", context)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db import connection
from .models import Quotation, SolarPanelCompany, InverterCompany, TermsAndCondition, OtherItem, Representative, \
    PlantCapacity
from .forms import QuotationForm
import logging

logger = logging.getLogger(__name__)

#
# def get_active_terms_conditions():
#     """Helper function to get active terms and conditions, handling bit varying type issue"""
#     # Use raw SQL to fetch all data and create model instances directly
#     # This completely bypasses Django ORM to avoid bit varying boolean comparison errors
#     try:
#         with connection.cursor() as cursor:
#             # Use CAST to text to avoid any boolean comparison issues
#             cursor.execute("""
#                 SELECT
#                     id,
#                     content,
#                     CAST(has_yellow_background AS TEXT) as has_yellow_text,
#                     CAST(is_active AS TEXT) as is_active_text,
#                     created_at
#                 FROM quotation_termsandcondition
#             """)
#             rows = cursor.fetchall()
#
#             # Create model instances directly from raw SQL results
#             terms_list = []
#             for row in rows:
#                 # Check if is_active is truthy by checking text value
#                 is_active_text = str(row[3]).lower() if row[3] else ''
#                 is_active_value = is_active_text in ('1', 't', 'true', 'y', 'yes')
#
#                 if is_active_value:
#                     term = TermsAndCondition()
#                     term.id = row[0]
#                     term.content = row[1] if row[1] else ''
#                     # Convert has_yellow_background from text
#                     has_yellow_text = str(row[2]).lower() if row[2] else ''
#                     term.has_yellow_background = has_yellow_text in ('1', 't', 'true', 'y', 'yes')
#                     term.is_active = True  # We already filtered for active ones
#                     term.created_at = row[4] if row[4] else None
#                     # Mark as saved to avoid save() calls and prevent database queries
#                     from django.db.models.base import ModelState
#                     term._state = ModelState()
#                     term._state.adding = False
#                     term._state.db = 'default'
#                     terms_list.append(term)
#
#             return terms_list
#     except Exception as e:
#         # If that fails, return empty list and log the error
#         logger.error(f"Error fetching terms and conditions: {e}")
#         return []

#
# def revise_quotation(request, pk):
#     original_quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#     terms_conditions = get_active_terms_conditions()
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (original_quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     # Store the new quotation ID between AJAX save and PDF generation
#     new_quotation_id = None
#
#     if request.method == "POST":
#         # Check if this is an AJAX save request or final PDF generation
#         is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('save_only')
#
#         # Check if we already have a saved quotation (for PDF generation phase)
#         saved_quotation_id = request.POST.get('saved_quotation_id')
#         if saved_quotation_id and not is_ajax:
#             try:
#                 # We already saved the quotation, just redirect to PDF
#                 new_quotation = Quotation.objects.get(pk=saved_quotation_id)
#                 pdf_template = request.POST.get('pdf_template', 'quotation')
#                 if pdf_template == 'industrial':
#                     return redirect("quotation:industrial_quotation_pdf", pk=new_quotation.pk)
#                 else:
#                     return redirect("quotation:quotation_pdf", pk=new_quotation.pk)
#             except Quotation.DoesNotExist:
#                 pass  # Continue with normal save process
#
#         form = QuotationForm(request.POST)
#
#         # Get active term IDs for validation
#         active_term_ids = [term.id for term in terms_conditions]
#
#         # Set terms_conditions queryset before validation
#         if active_term_ids:
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=active_term_ids)
#         else:
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         if form.is_valid():
#             # Create new quotation instance (don't save yet)
#             new_quotation = form.save(commit=False)
#
#             # Handle system_na checkbox - clear capacities if NA is checked
#             system_na = form.cleaned_data.get('system_na', False)
#             if system_na:
#                 new_quotation.dc_capacity = None
#                 new_quotation.ac_capacity = None
#             else:
#                 # Ensure capacities are saved if not NA
#                 new_quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
#                 new_quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
#
#             # Set system_na to False initially
#             new_quotation.system_na = False
#
#             # Handle Other Details NA checkbox
#             na_other_checked = request.POST.get("na_other_checkbox") == "on"
#             if na_other_checked:
#                 new_quotation.other_details = ""
#             else:
#                 # Process other items only if NA is not checked
#                 static_qs = form.cleaned_data.get("other_items") or []
#                 static_names = []
#                 for item in static_qs:
#                     if hasattr(item, 'name'):
#                         static_names.append(item.name)
#
#                 dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#
#                 combined = []
#                 for n in static_names + dynamic_inputs:
#                     if n and n not in combined:
#                         combined.append(n)
#
#                 new_quotation.other_details = " / ".join(combined)
#
#             # Only generate new quotation number if this is the first save
#             if not saved_quotation_id:
#                 # Generate new quotation number with revision
#                 base_quotation_no = original_quotation.quotation_no.split('_')[0]
#
#                 # Find the highest revision number for this base quotation
#                 existing_revisions = Quotation.objects.filter(
#                     quotation_no__startswith=base_quotation_no + '_'
#                 )
#
#                 if existing_revisions.exists():
#                     # Get the highest revision number
#                     max_revision = 0
#                     for rev in existing_revisions:
#                         try:
#                             rev_num = int(rev.quotation_no.split('_')[1])
#                             if rev_num > max_revision:
#                                 max_revision = rev_num
#                         except (IndexError, ValueError):
#                             continue
#                     new_revision = max_revision + 1
#                 else:
#                     # This is the first revision
#                     new_revision = 1
#
#                 new_quotation.quotation_no = f"{base_quotation_no}_{new_revision}"
#             else:
#                 # We're updating an existing revision, keep the same number
#                 try:
#                     existing_quotation = Quotation.objects.get(pk=saved_quotation_id)
#                     new_quotation.quotation_no = existing_quotation.quotation_no
#                 except Quotation.DoesNotExist:
#                     # Fallback to generating new number
#                     base_quotation_no = original_quotation.quotation_no.split('_')[0]
#                     new_quotation.quotation_no = f"{base_quotation_no}_1"
#
#             # Save the quotation
#             new_quotation.save()
#
#             # Store the new quotation ID
#             new_quotation_id = new_quotation.pk
#
#             # Update system_na using raw SQL to handle bit varying type
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', new_quotation.id])
#
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             new_quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             new_quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             new_quotation.inverter_companies.set(inverter_ids)
#
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 try:
#                     inv = InverterCompany.objects.get(id=inv_id)
#                     inv_names.append(inv.name)
#                     wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                     inv_warranties.append(wt)
#                 except InverterCompany.DoesNotExist:
#                     continue
#
#             new_quotation.inverter_company_names = " / ".join(inv_names)
#             new_quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES
#             rep_ids = request.POST.getlist('representatives')
#             new_quotation.representatives.set(rep_ids)
#
#             # Store textual representation for PDF
#             rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
#             rep_texts = []
#             for i, rep_id in enumerate(rep_ids):
#                 if rep_id in rep_dict:
#                     r = rep_dict[rep_id]
#                     contact_str = f" - {r.contact}" if r.contact else ""
#                     rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
#             new_quotation.representative_names = "\n".join(rep_texts)
#
#             # TERMS & CONDITIONS
#             terms_ids = request.POST.getlist('terms_conditions')
#             new_quotation.terms_conditions.set(terms_ids)
#
#             # Store terms content for PDF
#             terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
#             terms_texts = []
#             for i, term in enumerate(terms_qs):
#                 terms_texts.append(f"{i + 1}. {term.content}")
#             new_quotation.terms_conditions_text = "\n".join(terms_texts)
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 new_quotation.net_amount = net_input
#                 new_quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 new_quotation.final_amount = final_input
#                 new_quotation.calculate_from_final()
#
#             new_quotation.save()
#
#             # Update system_na again after final save
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', new_quotation.id])
#
#             # If this is an AJAX save request (save_only), return JSON success with quotation ID
#             if is_ajax:
#                 return JsonResponse({
#                     'success': True,
#                     'quotation_id': new_quotation.pk,
#                     'quotation_no': new_quotation.quotation_no,
#                     'message': 'Quotation revised successfully'
#                 })
#
#             # If this is a normal POST with pdf_template selected, redirect to PDF
#             pdf_template = request.POST.get('pdf_template', 'quotation')
#             if pdf_template == 'industrial':
#                 return redirect("quotation:industrial_quotation_pdf", pk=new_quotation.pk)
#             else:
#                 return redirect("quotation:quotation_pdf", pk=new_quotation.pk)
#
#         else:
#             # Form has errors
#             logger.error(f"Form errors: {form.errors}")
#
#             # If AJAX request, return errors as JSON
#             if is_ajax:
#                 return JsonResponse({
#                     'success': False,
#                     'errors': dict(form.errors)
#                 }, status=400)
#
#     else:
#         # GET - create form pre-filled with original quotation data
#         formatted_date = None
#         if original_quotation.date:
#             if hasattr(original_quotation.date, 'strftime'):
#                 formatted_date = original_quotation.date.strftime('%Y-%m-%d')
#             elif isinstance(original_quotation.date, str):
#                 try:
#                     from datetime import datetime
#                     for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S%z']:
#                         try:
#                             parsed_date = datetime.strptime(original_quotation.date, fmt)
#                             formatted_date = parsed_date.strftime('%Y-%m-%d')
#                             break
#                         except ValueError:
#                             continue
#                     if not formatted_date and len(original_quotation.date) >= 10:
#                         formatted_date = original_quotation.date[:10]
#                 except Exception:
#                     formatted_date = original_quotation.date
#             else:
#                 formatted_date = str(original_quotation.date)
#
#         form = QuotationForm(initial={
#             'consumer_type': original_quotation.consumer_type,
#             'consumer_no': original_quotation.consumer_no,
#             'title': original_quotation.title,
#             'consumer_name': original_quotation.consumer_name,
#             'consumer_address1': original_quotation.consumer_address1,
#             'consumer_address2': original_quotation.consumer_address2,
#             'consumer_no': original_quotation.consumer_no,
#             'consumer_mobile': original_quotation.consumer_mobile,
#             'date': formatted_date,
#             'plant_capacity_kw': original_quotation.plant_capacity_kw,
#             'employee_name': original_quotation.employee_name,
#             'panel_type': original_quotation.panel_type,
#             'panel_capacity_watt': original_quotation.panel_capacity_watt,
#             'panel_qty': original_quotation.panel_qty,
#             'panel_manufacturing_warranty': original_quotation.panel_manufacturing_warranty,
#             'panel_performance_warranty': original_quotation.panel_performance_warranty,
#             'inv_phase': original_quotation.inv_phase,
#             'inv_capacity_kw': original_quotation.inv_capacity_kw,
#             'inverter_qty': original_quotation.inverter_qty,
#             'structure_type': original_quotation.structure_type,
#             'structure_back_height_ft': original_quotation.structure_back_height_ft,
#             'structure_front_height_ft': original_quotation.structure_front_height_ft,
#             'structure_warranty': original_quotation.structure_warranty,
#             'special_discount': original_quotation.special_discount,
#             'gst_5_percent': original_quotation.gst_5_percent,
#             'gst_18_percent': original_quotation.gst_18_percent,
#             'net_amount_input': original_quotation.net_amount,
#             'final_amount_input': original_quotation.final_amount,
#             'dc_capacity': original_quotation.dc_capacity,
#             'ac_capacity': original_quotation.ac_capacity,
#             'system_na': original_quotation.system_na,
#             'electricity_unit_rate': original_quotation.electricity_unit_rate or 11.00,
#         })
#
#         # Set initial terms_conditions from the original quotation
#         existing_term_ids = list(original_quotation.terms_conditions.values_list('id', flat=True))
#         if existing_term_ids:
#             form.initial['terms_conditions'] = existing_term_ids
#             form.fields['terms_conditions'].initial = existing_term_ids
#
#         # Set terms_conditions queryset for GET request
#         active_term_ids = [term.id for term in terms_conditions]
#         if active_term_ids:
#             all_term_ids = list(set(active_term_ids + existing_term_ids))
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
#         else:
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         # Pre-check static other_items checkboxes
#         if original_quotation.other_details:
#             static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#             if static_names_to_check:
#                 checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#                 form.fields["other_items"].initial = checked_qs
#
#     # Prepare warranty mapping
#     stored_names = [n.strip() for n in (original_quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (original_quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "original_quotation": original_quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/revise_quotation.html", context)

def revise_quotation(request, pk):
    original_quotation = get_quotation_or_404_for_request(request, pk)

    panel_companies = list(SolarPanelCompany.objects.all())
    inverter_companies = list(InverterCompany.objects.all())
    terms_conditions = get_active_terms_conditions()

    # Build other_dynamic_list from stored other_details
    other_dynamic_list = [x.strip() for x in (original_quotation.other_details or "").split(" / ") if x.strip()]

    # Set of names existing in OtherItem table
    static_item_names = set(OtherItem.objects.values_list("name", flat=True))

    # Store the new quotation ID between AJAX save and PDF generation
    new_quotation_id = None

    if request.method == "POST":
        # Check if this is an AJAX save request or final PDF generation
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('save_only')

        # Check if we already have a saved quotation (for PDF generation phase)
        saved_quotation_id = request.POST.get('saved_quotation_id')
        if saved_quotation_id and not is_ajax:
            try:
                # We already saved the quotation, just redirect to PDF
                new_quotation = get_quotation_or_404_for_request(request, int(saved_quotation_id))
                pdf_template = request.POST.get('pdf_template', 'quotation')
                if pdf_template == 'industrial':
                    return redirect("quotation:industrial_quotation_pdf", pk=new_quotation.pk)
                else:
                    return redirect("quotation:quotation_pdf", pk=new_quotation.pk)
            except Quotation.DoesNotExist:
                pass  # Continue with normal save process

        form = QuotationForm(request.POST, form_user=request.user)

        # Get active term IDs for validation
        active_term_ids = [term.id for term in terms_conditions]

        # Set terms_conditions queryset before validation
        if active_term_ids:
            form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=active_term_ids)
        else:
            form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()

        if form.is_valid():
            # Create new quotation instance (don't save yet)
            new_quotation = form.save(commit=False)

            # Handle system_na checkbox - clear capacities if NA is checked
            system_na = form.cleaned_data.get('system_na', False)
            if system_na:
                new_quotation.dc_capacity = None
                new_quotation.ac_capacity = None
            else:
                # Ensure capacities are saved if not NA
                new_quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
                new_quotation.ac_capacity = form.cleaned_data.get('ac_capacity')

            # Set system_na to False initially
            new_quotation.system_na = False

            # Handle new fields from form
            new_quotation.consumer_state = form.cleaned_data.get('consumer_state', '')
            new_quotation.consumer_email = form.cleaned_data.get('consumer_email', '')
            new_quotation.project_type = form.cleaned_data.get('project_type', '')

            # Handle Other Details NA checkbox
            na_other_checked = request.POST.get("na_other_checkbox") == "on"
            if na_other_checked:
                new_quotation.other_details = ""
            else:
                # Process other items only if NA is not checked
                static_qs = form.cleaned_data.get("other_items") or []
                static_names = []
                for item in static_qs:
                    if hasattr(item, 'name'):
                        static_names.append(item.name)

                dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]

                combined = []
                for n in static_names + dynamic_inputs:
                    if n and n not in combined:
                        combined.append(n)

                new_quotation.other_details = " / ".join(combined)

            # Only generate new quotation number if this is the first save
            if not saved_quotation_id:
                # Generate new quotation number with revision
                base_quotation_no = original_quotation.quotation_no.split('_')[0]

                # Find the highest revision number for this base quotation
                existing_revisions = Quotation.objects.filter(
                    quotation_no__startswith=base_quotation_no + '_'
                )

                if existing_revisions.exists():
                    # Get the highest revision number
                    max_revision = 0
                    for rev in existing_revisions:
                        try:
                            rev_num = int(rev.quotation_no.split('_')[1])
                            if rev_num > max_revision:
                                max_revision = rev_num
                        except (IndexError, ValueError):
                            continue
                    new_revision = max_revision + 1
                else:
                    # This is the first revision
                    new_revision = 1

                new_quotation.quotation_no = f"{base_quotation_no}_{new_revision}"
            else:
                # We're updating an existing revision, keep the same number
                try:
                    existing_quotation = quotation_queryset_for_request(request.user).get(
                        pk=int(saved_quotation_id)
                    )
                    new_quotation.quotation_no = existing_quotation.quotation_no
                except Quotation.DoesNotExist:
                    # Fallback to generating new number
                    base_quotation_no = original_quotation.quotation_no.split('_')[0]
                    new_quotation.quotation_no = f"{base_quotation_no}_1"

            # Save the quotation
            new_quotation.save()

            # Store the new quotation ID
            new_quotation_id = new_quotation.pk

            # Update system_na using raw SQL to handle bit varying type
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE quotation_quotation 
                    SET system_na = %s 
                    WHERE id = %s
                """, ['1' if system_na else '0', new_quotation.id])

            form.save_m2m()

            # PANEL COMPANIES
            panel_ids = request.POST.getlist("panel_companies")
            new_quotation.panel_companies.set(panel_ids)
            panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
            new_quotation.panel_company_names = " / ".join(panel_names)

            # INVERTER COMPANIES + warranty
            inverter_ids = request.POST.getlist("inverter_companies")
            new_quotation.inverter_companies.set(inverter_ids)

            inv_names = []
            inv_warranties = []
            for inv_id in inverter_ids:
                try:
                    inv = InverterCompany.objects.get(id=inv_id)
                    inv_names.append(inv.name)
                    wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
                    inv_warranties.append(wt)
                except InverterCompany.DoesNotExist:
                    continue

            new_quotation.inverter_company_names = " / ".join(inv_names)
            new_quotation.inverter_warranty = " / ".join(inv_warranties)

            # REPRESENTATIVES
            rep_ids = request.POST.getlist('representatives')
            new_quotation.representatives.set(rep_ids)

            # Store textual representation for PDF
            rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
            rep_texts = []
            for i, rep_id in enumerate(rep_ids):
                if rep_id in rep_dict:
                    r = rep_dict[rep_id]
                    contact_str = f" - {r.contact}" if r.contact else ""
                    rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
            new_quotation.representative_names = "\n".join(rep_texts)

            # TERMS & CONDITIONS
            terms_ids = request.POST.getlist('terms_conditions')
            new_quotation.terms_conditions.set(terms_ids)

            # Store terms content for PDF
            terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
            terms_texts = []
            for i, term in enumerate(terms_qs):
                terms_texts.append(f"{i + 1}. {term.content}")
            new_quotation.terms_conditions_text = "\n".join(terms_texts)

            # PRICING
            pricing_mode = form.cleaned_data.get("pricing_mode")
            net_input = form.cleaned_data.get("net_amount_input")
            final_input = form.cleaned_data.get("final_amount_input")

            if pricing_mode == "net" and net_input is not None:
                new_quotation.net_amount = net_input
                new_quotation.calculate_from_net()
            elif pricing_mode == "final" and final_input is not None:
                new_quotation.final_amount = final_input
                new_quotation.calculate_from_final()

            new_quotation.save()

            # Update system_na again after final save
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE quotation_quotation 
                    SET system_na = %s 
                    WHERE id = %s
                """, ['1' if system_na else '0', new_quotation.id])

            # If this is an AJAX save request (save_only), return JSON success with quotation ID
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'quotation_id': new_quotation.pk,
                    'quotation_no': new_quotation.quotation_no,
                    'message': 'Quotation revised successfully'
                })

            # If this is a normal POST with pdf_template selected, redirect to PDF
            pdf_template = request.POST.get('pdf_template', 'quotation')
            if pdf_template == 'industrial':
                return redirect("quotation:industrial_quotation_pdf", pk=new_quotation.pk)
            else:
                return redirect("quotation:quotation_pdf", pk=new_quotation.pk)

        else:
            # Form has errors
            logger.error(f"Form errors: {form.errors}")

            # If AJAX request, return errors as JSON
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors)
                }, status=400)

    else:
        # GET - create form pre-filled with original quotation data
        formatted_date = None
        if original_quotation.date:
            if hasattr(original_quotation.date, 'strftime'):
                formatted_date = original_quotation.date.strftime('%Y-%m-%d')
            elif isinstance(original_quotation.date, str):
                try:
                    from datetime import datetime
                    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S%z']:
                        try:
                            parsed_date = datetime.strptime(original_quotation.date, fmt)
                            formatted_date = parsed_date.strftime('%Y-%m-%d')
                            break
                        except ValueError:
                            continue
                    if not formatted_date and len(original_quotation.date) >= 10:
                        formatted_date = original_quotation.date[:10]
                except Exception:
                    formatted_date = original_quotation.date
            else:
                formatted_date = str(original_quotation.date)

        form = QuotationForm(initial={
            'consumer_type': original_quotation.consumer_type,
            'consumer_no': original_quotation.consumer_no,
            'title': original_quotation.title,
            'consumer_name': original_quotation.consumer_name,
            'consumer_address1': original_quotation.consumer_address1,
            'consumer_address2': original_quotation.consumer_address2,
            'consumer_no': original_quotation.consumer_no,
            'consumer_mobile': original_quotation.consumer_mobile,
            'consumer_state': original_quotation.consumer_state,  # NEW FIELD
            'consumer_email': original_quotation.consumer_email,   # NEW FIELD
            'project_type': original_quotation.project_type,       # NEW FIELD
            'date': formatted_date,
            'plant_capacity_kw': original_quotation.plant_capacity_kw,
            'employee_name': original_quotation.employee_name,
            'panel_type': original_quotation.panel_type,
            'panel_capacity_watt': original_quotation.panel_capacity_watt,
            'panel_qty': original_quotation.panel_qty,
            'panel_manufacturing_warranty': original_quotation.panel_manufacturing_warranty,
            'panel_performance_warranty': original_quotation.panel_performance_warranty,
            'inv_phase': original_quotation.inv_phase,
            'inv_capacity_kw': original_quotation.inv_capacity_kw,
            'inverter_qty': original_quotation.inverter_qty,
            'structure_type': original_quotation.structure_type,
            'structure_back_height_ft': original_quotation.structure_back_height_ft,
            'structure_front_height_ft': original_quotation.structure_front_height_ft,
            'structure_warranty': original_quotation.structure_warranty,
            'special_discount': original_quotation.special_discount,
            'gst_5_percent': original_quotation.gst_5_percent,
            'gst_18_percent': original_quotation.gst_18_percent,
            'net_amount_input': original_quotation.net_amount,
            'final_amount_input': original_quotation.final_amount,
            'dc_capacity': original_quotation.dc_capacity,
            'ac_capacity': original_quotation.ac_capacity,
            'system_na': original_quotation.system_na,
            'electricity_unit_rate': original_quotation.electricity_unit_rate or 11.00,
            'assigned_associate': original_quotation.assigned_associate_id,
        }, form_user=request.user)

        # Set initial terms_conditions from the original quotation
        existing_term_ids = list(original_quotation.terms_conditions.values_list('id', flat=True))
        if existing_term_ids:
            form.initial['terms_conditions'] = existing_term_ids
            form.fields['terms_conditions'].initial = existing_term_ids

        # Set terms_conditions queryset for GET request
        active_term_ids = [term.id for term in terms_conditions]
        if active_term_ids:
            all_term_ids = list(set(active_term_ids + existing_term_ids))
            form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
        else:
            form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()

        # Pre-check static other_items checkboxes
        if original_quotation.other_details:
            static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
            if static_names_to_check:
                checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
                form.fields["other_items"].initial = checked_qs

    # Prepare warranty mapping
    stored_names = [n.strip() for n in (original_quotation.inverter_company_names or "").split(" / ") if n.strip()]
    stored_wts = [w.strip() for w in (original_quotation.inverter_warranty or "").split(" / ") if w.strip()]

    name_to_wt = {}
    for i, name in enumerate(stored_names):
        name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""

    for comp in inverter_companies:
        comp.warranty = name_to_wt.get(comp.name, "")

    context = {
        "form": form,
        "original_quotation": original_quotation,
        "panel_companies": panel_companies,
        "inverter_companies": inverter_companies,
        "terms_conditions": terms_conditions,
        "other_dynamic_list": other_dynamic_list,
        "static_item_names": static_item_names,
        "representatives": Representative.objects.all().order_by('name'),
    }
    return render(request, "quotation/revise_quotation.html", context)

#
# def edit_quotation(request, pk):
#     """
#     Edit an existing quotation (not create a revision).
#     Similar to revise_quotation but updates the same quotation instead of creating a new one.
#     """
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#     terms_conditions = get_active_terms_conditions()
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         # TODO: Uncomment POST section when ready
#         pass
# #         # Get existing term IDs from the quotation BEFORE creating the form
# #         # This ensures we can include them in the queryset
# #         existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
# #
# #         # Get submitted term IDs from POST data
# #         submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
# #
# #         # IMPORTANT: When editing, we need to include ALL existing terms (even if inactive)
# #         # because Django validates them when instance is provided
# #         # Get active term IDs using raw SQL
# #         try:
# #             with connection.cursor() as cursor:
# #                 cursor.execute("""
# #                     SELECT id FROM quotation_termsandcondition
# #                     WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
# #                 """)
# #                 active_term_ids = [row[0] for row in cursor.fetchall()]
# #
# #             # Combine: active + existing + submitted
# #             # CRITICAL: existing_term_ids MUST be included to pass validation
# #             all_term_ids = list(set(active_term_ids + existing_term_ids + submitted_term_ids))
# #
# #         except Exception as e:
# #             import logging
# #             logger = logging.getLogger(__name__)
# #             logger.warning(f"Could not get active term IDs: {e}")
# #             # Fallback: use existing + submitted terms
# #             all_term_ids = list(set(existing_term_ids + submitted_term_ids))
# #
# #         # For editing, we MUST include ALL existing terms to pass validation
# #         # Get ALL term IDs from database to ensure any existing term can be validated
# #         # This is necessary because existing terms might not be active anymore
# #         try:
# #             with connection.cursor() as cursor:
# #                 cursor.execute("SELECT id FROM quotation_termsandcondition")
# #                 all_db_term_ids = [int(row[0]) for row in cursor.fetchall()]  # Ensure integers
# #         except Exception as e:
# #             import logging
# #             logger = logging.getLogger(__name__)
# #             logger.warning(f"Could not get all term IDs: {e}")
# #             all_db_term_ids = []
# #
# #         # Ensure existing_term_ids are also integers
# #         existing_term_ids = [int(id) for id in existing_term_ids if id is not None]
# #
# #         # Combine: all database terms (to validate existing) + submitted terms
# #         # CRITICAL: Make sure ALL existing terms are included
# #         final_term_ids = list(set(all_db_term_ids + existing_term_ids + submitted_term_ids))
# #
# #         # Debug: Verify all existing terms are in final list
# #         import logging
# #         logger = logging.getLogger(__name__)
# #         missing_terms = set(existing_term_ids) - set(final_term_ids)
# #         if missing_terms:
# #             logger.error(f"CRITICAL: Existing terms {missing_terms} are missing from final_term_ids!")
# #             # Force include them
# #             final_term_ids = list(set(final_term_ids + list(missing_terms)))
# #
# #         # Debug logging
# #         import logging
# #         logger = logging.getLogger(__name__)
# #         logger.info(f"Edit quotation - Existing term IDs: {existing_term_ids}")
# #         logger.info(f"Edit quotation - Submitted term IDs: {submitted_term_ids}")
# #         logger.info(f"Edit quotation - All DB term IDs: {all_db_term_ids}")
# #         logger.info(f"Edit quotation - Final term IDs: {final_term_ids}")
# #
# #         # Create queryset with ALL terms from database
# #         # This ensures existing terms (even if inactive) will validate
# #         if final_term_ids:
# #             terms_queryset = TermsAndCondition.objects.filter(id__in=final_term_ids)
# #         else:
# #             terms_queryset = TermsAndCondition.objects.none()
# #
# #         # Create form with instance AND pass terms_conditions_queryset parameter
# #         # The form's __init__ will set the queryset on base_fields BEFORE super().__init__()
# #         # This ensures Django uses the correct queryset during validation
# #         form = QuotationForm(request.POST, instance=quotation, terms_conditions_queryset=terms_queryset)
# #
# #         # Double-check queryset is set correctly
# #         form.fields['terms_conditions'].queryset = terms_queryset
# #
# #         # Validate the form
# #         is_valid = form.is_valid()
# #
# #         # CRITICAL: Clear terms_conditions validation errors if they're about invalid choices
# #         # We know all terms exist because we got them from the database
# #         if not is_valid and 'terms_conditions' in form.errors:
# #             terms_errors = form.errors.get('terms_conditions', [])
# #             # Check if any error is about invalid choices
# #             has_invalid_choice_error = any('not one of the available choices' in str(e) for e in terms_errors)
# #             if has_invalid_choice_error:
# #                 # Clear the error - we verified these terms exist in the database
# #                 form._errors.pop('terms_conditions', None)
# #                 # Initialize cleaned_data if it doesn't exist
# #                 if not hasattr(form, 'cleaned_data'):
# #                     form.cleaned_data = {}
# #                 # Manually set cleaned_data for terms_conditions to bypass validation
# #                 submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
# #                 if submitted_term_ids:
# #                     form.cleaned_data['terms_conditions'] = list(TermsAndCondition.objects.filter(id__in=submitted_term_ids))
# #                 # Re-check if form is now valid (no errors left)
# #                 remaining_errors = {k: v for k, v in form.errors.items() if k != 'terms_conditions'}
# #                 if len(remaining_errors) == 0:
# #                     is_valid = True
# #
# #         if is_valid:
# #             quotation = form.save(commit=False)
# #
# #             # Handle system_na checkbox - clear capacities if NA is checked
# #             system_na = form.cleaned_data.get('system_na', False)
# #             if system_na:
# #                 quotation.dc_capacity = None
# #                 quotation.ac_capacity = None
# #             else:
# #                 # Ensure capacities are saved if not NA
# #                 quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
# #                 quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
# #
# #             # Set system_na to False - we'll update it via raw SQL immediately after save
# #             quotation.system_na = False
# #
# #             # Handle Other Details NA checkbox
# #             na_other_checked = request.POST.get("na_other_checkbox") == "on"
# #             if na_other_checked:
# #                 quotation.other_details = ""
# #             else:
# #                 # Process other items only if NA is not checked
# #                 static_qs = form.cleaned_data.get("other_items") or []
# #                 static_names = []
# #                 for item in static_qs:
# #                     if hasattr(item, 'name'):
# #                         static_names.append(item.name)
# #                 dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
# #                 combined = []
# #                 for n in static_names + dynamic_inputs:
# #                     if n and n not in combined:
# #                         combined.append(n)
# #                 quotation.other_details = " / ".join(combined)
# #
# #             quotation.save()
# #
# #             # Update system_na using raw SQL to handle bit varying type
# #             with connection.cursor() as cursor:
# #                 cursor.execute("""
# #                     UPDATE quotation_quotation
# #                     SET system_na = %s::bit varying
# #                     WHERE id = %s
# #                 """, ['1' if system_na else '0', quotation.id])
# #
# #             form.save_m2m()
# #
# #             # PANEL COMPANIES
# #             panel_ids = request.POST.getlist("panel_companies")
# #             quotation.panel_companies.set(panel_ids)
# #             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
# #             quotation.panel_company_names = " / ".join(panel_names)
# #
# #             # INVERTER COMPANIES + warranty
# #             inverter_ids = request.POST.getlist("inverter_companies")
# #             quotation.inverter_companies.set(inverter_ids)
# #             inv_names = []
# #             inv_warranties = []
# #             for inv_id in inverter_ids:
# #                 inv = InverterCompany.objects.get(id=inv_id)
# #                 inv_names.append(inv.name)
# #                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
# #                 inv_warranties.append(wt)
# #             quotation.inverter_company_names = " / ".join(inv_names)
# #             quotation.inverter_warranty = " / ".join(inv_warranties)
# #
# #             # REPRESENTATIVES
# #             rep_ids = request.POST.getlist('representatives')
# #             quotation.representatives.set(rep_ids)
# #             rep_qs = Representative.objects.filter(id__in=rep_ids)
# #             rep_texts = [f"{i + 1}. {r.name} - {r.contact}" for i, r in enumerate(rep_qs)]
# #             quotation.representative_names = "\n".join(rep_texts)
# #
# #             # TERMS & CONDITIONS
# #             terms_ids = request.POST.getlist('terms_conditions')
# #             if terms_ids:
# #                 quotation.terms_conditions.set(terms_ids)
# #                 terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
# #                 terms_texts = []
# #                 for i, term in enumerate(terms_qs, 1):
# #                     terms_texts.append(f"{i}. {term.content}")
# #                 quotation.terms_conditions_text = "\n".join(terms_texts)
# #             else:
# #                 # Clear terms if none selected
# #                 quotation.terms_conditions.clear()
# #                 quotation.terms_conditions_text = ""
# #
# #             # PRICING
# #             pricing_mode = form.cleaned_data.get("pricing_mode")
# #             net_input = form.cleaned_data.get("net_amount_input")
# #             final_input = form.cleaned_data.get("final_amount_input")
# #
# #             if pricing_mode == "net" and net_input is not None:
# #                 quotation.net_amount = net_input
# #                 quotation.calculate_from_net()
# #             elif pricing_mode == "final" and final_input is not None:
# #                 quotation.final_amount = final_input
# #                 quotation.calculate_from_final()
# #
# #             quotation.save()
# #
# #             # Update system_na again after final save
# #             with connection.cursor() as cursor:
# #                 cursor.execute("""
# #                     UPDATE quotation_quotation
# #                     SET system_na = %s::bit varying
# #                     WHERE id = %s
# #                 """, ['1' if system_na else '0', quotation.id])
# #
# #             return redirect("quotation:quotation_pdf", pk=quotation.pk)
#     else:
#         # GET - create form pre-filled with existing quotation data
#         # CRITICAL: Format date BEFORE creating form to ensure it's in the correct format
#         # Format date for HTML date input (YYYY-MM-DD format)
#         formatted_date = None
#         if quotation.date:
#             if hasattr(quotation.date, 'strftime'):
#                 # It's a datetime object
#                 formatted_date = quotation.date.strftime('%Y-%m-%d')
#             elif isinstance(quotation.date, str):
#                 # It's already a string, try to parse and reformat
#                 try:
#                     from datetime import datetime
#                     # Try common date formats
#                     for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S%z']:
#                         try:
#                             parsed_date = datetime.strptime(quotation.date, fmt)
#                             formatted_date = parsed_date.strftime('%Y-%m-%d')
#                             break
#                         except ValueError:
#                             continue
#                     # If parsing failed, use original string if it's already in YYYY-MM-DD format
#                     if not formatted_date and len(quotation.date) >= 10:
#                         formatted_date = quotation.date[:10]  # Take first 10 chars (YYYY-MM-DD)
#                 except Exception:
#                     formatted_date = quotation.date
#             else:
#                 formatted_date = str(quotation.date)
#
#         # Create form with instance AND initial data for date
#         # Using initial parameter ensures the formatted date is used
#         initial_data = {}
#         if formatted_date:
#             initial_data['date'] = formatted_date
#
#         # Create form with instance AND initial data
#         # Pass initial data to ensure formatted date is used (same approach as revise_quotation)
#         form = QuotationForm(instance=quotation, initial=initial_data)
#
#         # CRITICAL: Also explicitly set it after form creation to ensure it's used
#         # When using instance=quotation, Django may populate from instance first
#         # So we need to explicitly override the date field
#         if formatted_date:
#             # Set in initial data dictionary - this should override instance value
#             form.initial['date'] = formatted_date
#
#             # Also set on the field itself
#             if 'date' in form.fields:
#                 form.fields['date'].initial = formatted_date
#
#                 # For HTML5 date inputs (type='date'), ensure widget has the value
#                 try:
#                     if not hasattr(form.fields['date'].widget, 'attrs'):
#                         form.fields['date'].widget.attrs = {}
#                     form.fields['date'].widget.attrs['value'] = formatted_date
#                 except Exception as e:
#                     import logging
#                     logger = logging.getLogger(__name__)
#                     logger.warning(f"Could not set date widget value: {e}")
#
#                 # Clear bound field cache so it rebuilds with formatted value
#                 if hasattr(form, '_bound_fields_cache'):
#                     form._bound_fields_cache.pop('date', None)
#
#         # Set terms_conditions queryset to include:
#         # 1. All active terms (for new selections)
#         # 2. Existing terms from this quotation (so validation passes)
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM quotation_termsandcondition
#                     WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
#                 """)
#                 active_term_ids = [row[0] for row in cursor.fetchall()]
#
#             # Get existing term IDs from the quotation
#             existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#
#             # Combine both lists (active + existing) to ensure validation passes
#             all_term_ids = list(set(active_term_ids + existing_term_ids))
#
#             if all_term_ids:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
#             else:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not set terms_conditions queryset: {e}")
#             # Fallback: include at least the existing terms
#             try:
#                 existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#                 if existing_term_ids:
#                     form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=existing_term_ids)
#                 else:
#                     form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#             except:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         # Pre-check static other_items checkboxes
#         if quotation.other_details:
#             static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#             if static_names_to_check:
#                 checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#                 form.fields["other_items"].initial = checked_qs
#
#     # Prepare warranty mapping
#     stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "quotation": quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/edit_quotation.html", context)

#
# def create_panel_company(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         if name:
#             SolarPanelCompany.objects.create(name=name)
#             return redirect('quotation:create_quotation')
#     return render(request, 'quotation/create_panel_company.html')
#
#
# def create_inverter_company(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         if name:
#             InverterCompany.objects.create(name=name)
#             return redirect('quotation:create_quotation')
#     return render(request, 'quotation/create_inverter_company.html')

#
# def create_quotation(request):
#     panel_companies = SolarPanelCompany.objects.all()
#     inverter_companies = InverterCompany.objects.all()
#
#     if request.method == 'POST':
#         form = QuotationForm(request.POST)
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#
#             # Extract pricing values
#             pricing_mode = form.cleaned_data.get('pricing_mode')
#             net_input = form.cleaned_data.get('net_amount_input')
#             final_input = form.cleaned_data.get('final_amount_input')
#
#             quotation.save()
#             form.save_m2m()  # for many-to-many
#
#             # -----------------------------
#             # SAVE PANEL COMPANIES
#             # -----------------------------
#             panel_ids = request.POST.getlist('panel_companies')
#             quotation.panel_companies.set(panel_ids)
#
#             panel_names = SolarPanelCompany.objects.filter(
#                 id__in=panel_ids
#             ).values_list('name', flat=True)
#
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # -----------------------------
#             # SAVE INVERTER COMPANIES
#             # -----------------------------
#             inverter_ids = request.POST.getlist('inverter_companies')
#             quotation.inverter_companies.set(inverter_ids)
#
#             inverter_names = InverterCompany.objects.filter(
#                 id__in=inverter_ids
#             ).values_list('name', flat=True)
#
#             quotation.inverter_company_names = " / ".join(inverter_names)
#
#             quotation.save()
#
#
#             # # SAVE STATIC FIELDS
#             # quotation.walkway = form.cleaned_data.get('walkway')
#             # quotation.staircase = form.cleaned_data.get('staircase')
#             # quotation.plumbing = form.cleaned_data.get('plumbing')
#             # quotation.safety_railing = form.cleaned_data.get('safety_railing')
#             # quotation.gi_tray = form.cleaned_data.get('gi_tray')
#             #
#             # # SAVE DYNAMIC FIELDS
#             # other_names = request.POST.getlist('other_field_name[]')
#             # other_values = request.POST.getlist('other_field_value[]')
#             #
#             # other_dict = {}
#             #
#             # for name, value in zip(other_names, other_values):
#             #     if name.strip():
#             #         other_dict[name] = value
#             #
#             # quotation.other_details = other_dict
#             #
#             # quotation.save()
#
#             # STATIC CHECKBOXES
#             static_items = form.cleaned_data.get("other_items", [])
#
#             # DYNAMIC CHECKBOXES FROM MODAL
#             dynamic_items = request.POST.getlist("dynamic_other_items[]")
#
#             combined = static_items + dynamic_items
#
#             # store as: Walkway / GI Tray / Safety Railing
#             quotation.other_details = " / ".join(combined)
#
#             quotation.save()
#
#             # -----------------------------
#             # APPLY PRICING LOGIC
#             # -----------------------------
#             if pricing_mode == 'net' and net_input:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#                 quotation.save()
#             elif pricing_mode == 'final' and final_input:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#                 quotation.save()
#             quotation.save()
#
#             return redirect('quotation:quotation_pdf', pk=quotation.pk)
#
#     else:
#         form = QuotationForm()
#
#     context = {
#         'form': form,
#         'panel_companies': panel_companies,
#         'inverter_companies': inverter_companies,
#         # REMOVE formset
#     }
#     return render(request, 'quotation/create_quotation.html', context)
#
# @require_POST
# def add_terms_condition_api(request):
#     content = request.POST.get('content', '').strip()
#     if not content:
#         return JsonResponse({'success': False, 'error': 'Content required'}, status=400)
#
#     obj = TermsAndCondition.objects.create(content=content)
#     return JsonResponse({
#         'success': True,
#         'id': obj.id,
#         'content': obj.content
#     })
# def edit_quotation(request, pk):
#     """
#     Edit an existing quotation (not create a revision).
#     Similar to revise_quotation but updates the same quotation instead of creating a new one.
#     """
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#     terms_conditions = get_active_terms_conditions()
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         # Get existing term IDs from the quotation BEFORE creating the form
#         # This ensures we can include them in the queryset
#         existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#
#         # Get submitted term IDs from POST data
#         submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
#
#         # IMPORTANT: When editing, we need to include ALL existing terms (even if inactive)
#         # because Django validates them when instance is provided
#         # Get active term IDs using raw SQL
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM quotation_termsandcondition
#                     WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
#                 """)
#                 active_term_ids = [row[0] for row in cursor.fetchall()]
#
#             # Combine: active + existing + submitted
#             # CRITICAL: existing_term_ids MUST be included to pass validation
#             all_term_ids = list(set(active_term_ids + existing_term_ids + submitted_term_ids))
#
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not get active term IDs: {e}")
#             # Fallback: use existing + submitted terms
#             all_term_ids = list(set(existing_term_ids + submitted_term_ids))
#
#         # For editing, we MUST include ALL existing terms to pass validation
#         # Get ALL term IDs from database to ensure any existing term can be validated
#         # This is necessary because existing terms might not be active anymore
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT id FROM quotation_termsandcondition")
#                 all_db_term_ids = [int(row[0]) for row in cursor.fetchall()]  # Ensure integers
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not get all term IDs: {e}")
#             all_db_term_ids = []
#
#         # Ensure existing_term_ids are also integers
#         existing_term_ids = [int(id) for id in existing_term_ids if id is not None]
#
#         # Combine: all database terms (to validate existing) + submitted terms
#         # CRITICAL: Make sure ALL existing terms are included
#         final_term_ids = list(set(all_db_term_ids + existing_term_ids + submitted_term_ids))
#
#         # Debug: Verify all existing terms are in final list
#         import logging
#         logger = logging.getLogger(__name__)
#         missing_terms = set(existing_term_ids) - set(final_term_ids)
#         if missing_terms:
#             logger.error(f"CRITICAL: Existing terms {missing_terms} are missing from final_term_ids!")
#             # Force include them
#             final_term_ids = list(set(final_term_ids + list(missing_terms)))
#
#         # Debug logging
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.info(f"Edit quotation - Existing term IDs: {existing_term_ids}")
#         logger.info(f"Edit quotation - Submitted term IDs: {submitted_term_ids}")
#         logger.info(f"Edit quotation - All DB term IDs: {all_db_term_ids}")
#         logger.info(f"Edit quotation - Final term IDs: {final_term_ids}")
#
#         # Create queryset with ALL terms from database
#         # This ensures existing terms (even if inactive) will validate
#         if final_term_ids:
#             terms_queryset = TermsAndCondition.objects.filter(id__in=final_term_ids)
#         else:
#             terms_queryset = TermsAndCondition.objects.none()
#
#         # Create form with instance AND pass terms_conditions_queryset parameter
#         # The form's __init__ will set the queryset on base_fields BEFORE super().__init__()
#         # This ensures Django uses the correct queryset during validation
#         form = QuotationForm(request.POST, instance=quotation, terms_conditions_queryset=terms_queryset)
#
#         # Double-check queryset is set correctly
#         form.fields['terms_conditions'].queryset = terms_queryset
#
#         # Validate the form
#         is_valid = form.is_valid()
#
#         # CRITICAL: Clear terms_conditions validation errors if they're about invalid choices
#         # We know all terms exist because we got them from the database
#         if not is_valid and 'terms_conditions' in form.errors:
#             terms_errors = form.errors.get('terms_conditions', [])
#             # Check if any error is about invalid choices
#             has_invalid_choice_error = any('not one of the available choices' in str(e) for e in terms_errors)
#             if has_invalid_choice_error:
#                 # Clear the error - we verified these terms exist in the database
#                 form._errors.pop('terms_conditions', None)
#                 # Initialize cleaned_data if it doesn't exist
#                 if not hasattr(form, 'cleaned_data'):
#                     form.cleaned_data = {}
#                 # Manually set cleaned_data for terms_conditions to bypass validation
#                 submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
#                 if submitted_term_ids:
#                     form.cleaned_data['terms_conditions'] = list(
#                         TermsAndCondition.objects.filter(id__in=submitted_term_ids))
#                 # Re-check if form is now valid (no errors left)
#                 remaining_errors = {k: v for k, v in form.errors.items() if k != 'terms_conditions'}
#                 if len(remaining_errors) == 0:
#                     is_valid = True
#
#         if is_valid:
#             quotation = form.save(commit=False)
#
#             # Handle system_na checkbox - clear capacities if NA is checked
#             system_na = form.cleaned_data.get('system_na', False)
#             if system_na:
#                 quotation.dc_capacity = None
#                 quotation.ac_capacity = None
#             else:
#                 # Ensure capacities are saved if not NA
#                 quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
#                 quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
#
#             # Set system_na to False - we'll update it via raw SQL immediately after save
#             quotation.system_na = False
#
#             # Handle Other Details NA checkbox
#             na_other_checked = request.POST.get("na_other_checkbox") == "on"
#             if na_other_checked:
#                 quotation.other_details = ""
#             else:
#                 # Process other items only if NA is not checked
#                 static_qs = form.cleaned_data.get("other_items") or []
#                 static_names = []
#                 for item in static_qs:
#                     if hasattr(item, 'name'):
#                         static_names.append(item.name)
#                 dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#                 combined = []
#                 for n in static_names + dynamic_inputs:
#                     if n and n not in combined:
#                         combined.append(n)
#                 quotation.other_details = " / ".join(combined)
#
#             quotation.save()
#
#             # Update system_na using raw SQL to handle bit varying type
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s::bit varying
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', quotation.id])
#
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             quotation.inverter_companies.set(inverter_ids)
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inv_names.append(inv.name)
#                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                 inv_warranties.append(wt)
#             quotation.inverter_company_names = " / ".join(inv_names)
#             quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES
#             rep_ids = request.POST.getlist('representatives')
#             quotation.representatives.set(rep_ids)
#             rep_qs = Representative.objects.filter(id__in=rep_ids)
#             rep_texts = [f"{i + 1}. {r.name} - {r.contact}" for i, r in enumerate(rep_qs)]
#             quotation.representative_names = "\n".join(rep_texts)
#
#             # TERMS & CONDITIONS
#             terms_ids = request.POST.getlist('terms_conditions')
#             if terms_ids:
#                 quotation.terms_conditions.set(terms_ids)
#                 terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
#                 terms_texts = []
#                 for i, term in enumerate(terms_qs, 1):
#                     terms_texts.append(f"{i}. {term.content}")
#                 quotation.terms_conditions_text = "\n".join(terms_texts)
#             else:
#                 # Clear terms if none selected
#                 quotation.terms_conditions.clear()
#                 quotation.terms_conditions_text = ""
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             quotation.save()
#
#             # Update system_na again after final save
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s::bit varying
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', quotation.id])
#
#             return redirect("quotation:quotation_pdf", pk=quotation.pk)
#     else:
#         # GET - create form pre-filled with existing quotation data
#         form = QuotationForm(instance=quotation)
#
#         # Set terms_conditions queryset to include:
#         # 1. All active terms (for new selections)
#         # 2. Existing terms from this quotation (so validation passes)
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM quotation_termsandcondition
#                     WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
#                 """)
#                 active_term_ids = [row[0] for row in cursor.fetchall()]
#
#             # Get existing term IDs from the quotation
#             existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#
#             # Combine both lists (active + existing) to ensure validation passes
#             all_term_ids = list(set(active_term_ids + existing_term_ids))
#
#             if all_term_ids:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
#             else:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not set terms_conditions queryset: {e}")
#             # Fallback: include at least the existing terms
#             try:
#                 existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#                 if existing_term_ids:
#                     form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(
#                         id__in=existing_term_ids)
#                 else:
#                     form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#             except:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         # Pre-check static other_items checkboxes
#         if quotation.other_details:
#             static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#             if static_names_to_check:
#                 checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#                 form.fields["other_items"].initial = checked_qs
#
#     # Prepare warranty mapping
#     stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "quotation": quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/edit_quotation.html", context)
#
#
# # ---- AJAX: Add Panel Company ----
# @require_POST
# def add_panel_company_api(request):
#     name = request.POST.get('name', '').strip()
#     if not name:
#         return JsonResponse({'success': False, 'error': 'Name required'}, status=400)
#
#     obj, created = SolarPanelCompany.objects.get_or_create(name=name)
#     return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name})
#
#
# # ---- AJAX: Add Inverter Company ----
# @require_POST
# def add_inverter_company_api(request):
#     name = request.POST.get('name', '').strip()
#     if not name:
#         return JsonResponse({'success': False, 'error': 'Name required'}, status=400)
#
#     obj, created = InverterCompany.objects.get_or_create(name=name)
#     return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name})
#
#
#
# # def create_panel_company(request):
# #     if request.method == 'POST':
# #         name = request.POST.get('name')
# #         if name:
# #             obj, created = SolarPanelCompany.objects.get_or_create(name=name)
# #             return JsonResponse({"success": True, "id": obj.id, "name": obj.name})
# #     return JsonResponse({"success": False})
# #
# # def create_inverter_company(request):
# #     if request.method == 'POST':
# #         name = request.POST.get('name')
# #         if name:
# #             obj, created = InverterCompany.objects.get_or_create(name=name)
# #             return JsonResponse({"success": True, "id": obj.id, "name": obj.name})
# #     return JsonResponse({"success": False})
#
#
#
# #
# # def edit_quotation(request, pk):
# #     quotation = get_object_or_404(Quotation, pk=pk)
# #     # ItemFormSet = modelformset_factory(QuotationItem, form=QuotationItemForm, extra=0, can_delete=True)
# #     panel_companies = SolarPanelCompany.objects.all()
# #     inverter_companies = InverterCompany.objects.all()
# #
# #     if request.method == 'POST':
# #         form = QuotationForm(request.POST, instance=quotation)
# #         # formset = ItemFormSet(request.POST, queryset=quotation.items.all())
# #
# #         # if form.is_valid() and formset.is_valid():
# #             q = form.save()
# #             q.panel_companies.set(request.POST.getlist('panel_companies'))
# #             q.inverter_companies.set(request.POST.getlist('inverter_companies'))
# #
# #             # for item_form in formset:
# #                 if item_form.cleaned_data:
# #                     if item_form.cleaned_data.get('DELETE'):
# #                         if item_form.instance.pk:
# #                             item_form.instance.delete()
# #                     else:
# #                         item = item_form.save(commit=False)
# #                         item.quotation = q
# #                         item.save()
# #
# #             q.calculate_totals()
# #             return redirect('quotation:quotation_pdf', pk=q.pk)
# #         else:
# #             print("Edit form errors:", form.errors)
# #             print("Edit formset errors:", formset.errors)
# #     else:
# #         form = QuotationForm(instance=quotation)
# #         formset = ItemFormSet(queryset=quotation.items.all())
# #
# #     context = {
# #         'form': form,
# #         'formset': formset,
# #         'quotation': quotation,
# #         'panel_companies': panel_companies,
# #         'inverter_companies': inverter_companies,
# #     }
# #     return render(request, 'quotation/edit_quotation.html', context)
#
#
#
# # def create_quotation(request):
# #     # ItemFormSet = modelformset_factory(QuotationItem, form=QuotationItemForm, extra=1, can_delete=True)
# #     panel_companies = SolarPanelCompany.objects.all()
# #     inverter_companies = InverterCompany.objects.all()
# #
# #     if request.method == 'POST':
# #         form = QuotationForm(request.POST)
# #         # formset = ItemFormSet(request.POST, queryset=QuotationItem.objects.none())
# #
# #         if form.is_valid() and formset.is_valid():
# #             quotation = form.save(commit=False)
# #             pricing_mode = form.cleaned_data.get('pricing_mode')
# #             net_input = form.cleaned_data.get('net_amount_input')
# #             final_input = form.cleaned_data.get('final_amount_input')
# #
# #             quotation.save()
# #             form.save_m2m()  # REQUIRED for many-to-many
# #
# #             panel_ids = request.POST.getlist('panel_companies')
# #             quotation.panel_companies.set(panel_ids)
# #
# #             quotation.panel_company_names = "/".join(
# #                 SolarPanelCompany.objects.filter(id__in=panel_ids).values_list('name', flat=True)
# #             )
# #
# #             inverter_ids = request.POST.getlist('inverter_companies')
# #             quotation.inverter_companies.set(inverter_ids)
# #
# #             quotation.inverter_company_names = "/".join(
# #                 InverterCompany.objects.filter(id__in=inverter_ids).values_list('name', flat=True)
# #             )
# #
# #             quotation.save()
# #
# #             # quotation.save()
# #             # quotation.panel_companies.set(request.POST.getlist('panel_companies'))
# #             # quotation.inverter_companies.set(request.POST.getlist('inverter_companies'))
# #
# #             # # Save all item rows
# #             # for item_form in formset:
# #             #     if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
# #             #         item = item_form.save(commit=False)
# #             #         item.quotation = quotation
# #             #         item.save()
# #
# #             # Apply pricing logic
# #             if pricing_mode == 'net' and net_input:
# #                 quotation.net_amount = net_input
# #                 quotation.calculate_from_net()
# #             elif pricing_mode == 'final' and final_input:
# #                 quotation.final_amount = final_input
# #                 quotation.calculate_from_final()
# #
# #             return redirect('quotation:quotation_pdf', pk=quotation.pk)
# #     else:
# #         form = QuotationForm()
# #         # formset = ItemFormSet(queryset=QuotationItem.objects.none())
# #
# #     context = {
# #         'form': form,
# #         'formset': formset,
# #         'panel_companies': panel_companies,
# #         'inverter_companies': inverter_companies,
# #     }
# #     return render(request, 'quotation/create_quotation.html', context)
#
#
#
#
# @require_POST
# def add_other_item_api(request):
#     """
#     AJAX endpoint to create a new OtherItem.
#     Expects: POST 'name'
#     Returns: JSON { success: True, id: ..., name: ... } or error
#     """
#     name = request.POST.get('name', '').strip()
#     if not name:
#         return JsonResponse({'success': False, 'error': 'Name required'}, status=400)
#
#     # create or get existing
#     obj, created = OtherItem.objects.get_or_create(name=name)
#     return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name, 'created': created})
#
# @require_POST
# def add_terms_condition_api(request):
#     content = request.POST.get('content', '').strip()
#     # Handle both 'true'/'false' strings and boolean values
#     has_yellow_background_str = request.POST.get('has_yellow_background', 'false')
#     has_yellow_background = has_yellow_background_str in ('true', 'True', '1', 1, True)
#
#     if not content:
#         return JsonResponse({'success': False, 'error': 'Content required'}, status=400)
#
#     # Handle bit varying columns using raw SQL to avoid type mismatch errors
#     try:
#         with connection.cursor() as cursor:
#             # Insert using raw SQL with proper bit varying casting
#             cursor.execute("""
#                 INSERT INTO quotation_termsandcondition (content, has_yellow_background, is_active, created_at)
#                 VALUES (%s, (%s)::bit(1)::bit varying, B'1'::bit varying, now())
#                 RETURNING id
#             """, [content, 1 if has_yellow_background else 0])
#             new_id = cursor.fetchone()[0]
#
#         # Fetch the created object to return
#         obj = TermsAndCondition.objects.get(id=new_id)
#         # Convert bit varying to boolean for JSON response
#         # The BitVaryingBooleanField should handle this, but ensure we return boolean
#         has_yellow_value = bool(obj.has_yellow_background) if hasattr(obj, 'has_yellow_background') else has_yellow_background
#
#         return JsonResponse({
#             'success': True,
#             'id': obj.id,
#             'content': obj.content,
#             'has_yellow_background': has_yellow_value
#         })
#     except Exception as e:
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.error(f"Error creating term and condition: {e}")
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)
#
#
# # Alias for add_terms_api URL
# add_terms_api = add_terms_condition_api


#
# def create_quotation(request):
#         panel_companies = SolarPanelCompany.objects.all()
#         inverter_companies = InverterCompany.objects.all()
#         representatives = Representative.objects.all()
#         terms_conditions = TermsAndCondition.objects.filter(is_active=True)
#
#         if request.method == 'POST':
#             form = QuotationForm(request.POST)
#
#             if form.is_valid():
#                 quotation = form.save(commit=False)
#
#                 # pricing logic (as you already have)
#                 pricing_mode = form.cleaned_data.get('pricing_mode')
#                 net_input = form.cleaned_data.get('net_amount_input')
#                 final_input = form.cleaned_data.get('final_amount_input')
#                 # Handle plant capacity (it's now a ForeignKey)
#                 plant_capacity = form.cleaned_data.get('plant_capacity_kw')
#                 terms_ids = request.POST.getlist('terms_conditions')
#                 quotation.terms_conditions.set(terms_ids)
#
#                 # Build textual representation for PDF
#                 terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids)
#                 terms_texts = [f"{i + 1}. {t.content}" for i, t in enumerate(terms_qs)]
#                 quotation.terms_conditions_text = "\n".join(terms_texts)
#
#                 if plant_capacity:
#                     quotation.plant_capacity_kw = plant_capacity
#
#                 # Save M2M fields after commit
#                 quotation.save()
#                 form.save_m2m()
#
#                 # Save representatives M2M
#                 rep_ids = request.POST.getlist('representatives')
#                 quotation.representatives.set(rep_ids)
#
#                 # Build a textual representation for quick PDF rendering (optional)
#                 rep_qs = Representative.objects.filter(id__in=rep_ids)
#                 rep_texts = [f"{i + 1}. {r.name} - {r.contact}" for i, r in enumerate(rep_qs)]
#                 quotation.representative_names = "\n".join(rep_texts)
#                 quotation.save()
#
#                 # collect other_items selection (ModelMultipleChoiceField returns QuerySet)
#                 other_qs = form.cleaned_data.get('other_items')  # QuerySet of OtherItem
#                 other_names = []
#                 if other_qs:
#                     other_names = list(other_qs.values_list('name', flat=True))
#
#                 # if you also allowed dynamic checkboxes posted manually (not necessary since form has them),
#                 # you can merge request.POST.getlist('dynamic_other_items[]') as well:
#                 dynamic_items = request.POST.getlist('dynamic_other_items[]')
#                 # combine and dedupe while preserving order
#                 combined = []
#                 for n in other_names + dynamic_items:
#                     n = n.strip()
#                     if n and n not in combined:
#                         combined.append(n)
#
#                 quotation.other_details = " / ".join(combined)
#                 # -----------------------------
#                 # SAVE PANEL COMPANIES
#                 # -----------------------------
#                 panel_ids = request.POST.getlist('panel_companies')
#                 quotation.panel_companies.set(panel_ids)
#
#                 panel_names = SolarPanelCompany.objects.filter(
#                     id__in=panel_ids
#                 ).values_list('name', flat=True)
#
#                 quotation.panel_company_names = " / ".join(panel_names)
#
#                 # # -----------------------------
#                 # # SAVE INVERTER COMPANIES
#                 # # -----------------------------
#                 # inverter_ids = request.POST.getlist('inverter_companies')
#                 # quotation.inverter_companies.set(inverter_ids)
#                 #
#                 # inverter_names = InverterCompany.objects.filter(
#                 #     id__in=inverter_ids
#                 # ).values_list('name', flat=True)
#                 #
#                 # quotation.inverter_company_names = " / ".join(inverter_names)
#                 #
#                 # quotation.save()
#                 # -----------------------------
#                 # SAVE INVERTER COMPANIES + WARRANTY
#                 # -----------------------------
#                 inverter_ids = request.POST.getlist('inverter_companies')
#                 quotation.inverter_companies.set(inverter_ids)
#
#                 inverter_names = []
#                 warranty_values = []
#
#                 for inv_id in inverter_ids:
#                     # Fetch inverter company name
#                     name = InverterCompany.objects.get(id=inv_id).name
#                     inverter_names.append(name)
#
#                     # Collect warranty from dynamically shown textbox
#                     wt = request.POST.get(f'inverter_warranty_{inv_id}', '').strip()
#                     if wt:
#                         warranty_values.append(wt)
#
#                 quotation.inverter_company_names = " / ".join(inverter_names)
#                 quotation.inverter_warranty = " / ".join(warranty_values)
#
#                 # -----------------------------
#                 # APPLY PRICING LOGIC
#                 # -----------------------------
#
#                 if pricing_mode == 'net' and net_input:
#                     quotation.net_amount = net_input
#                     quotation.calculate_from_net()
#
#                 elif pricing_mode == 'final' and final_input:
#                     quotation.final_amount = final_input
#                     quotation.calculate_from_final()
#
#                 quotation.save()
#
#                 return redirect('quotation:quotation_pdf', pk=quotation.pk)
#         else:
#             form = QuotationForm()
#
#         context = {
#             'form': form,
#             'panel_companies': panel_companies,
#             'inverter_companies': inverter_companies,
#             'representatives': representatives,
#             'terms_conditions': terms_conditions,
#
#         }
#         return render(request, 'quotation/create_quotation.html', context)
# def check_consumer(request):
#     if request.method == 'POST':
#         consumer_type = request.POST.get('consumer_type')
#         consumer_no = request.POST.get('consumer_no')
#
#         try:
#             # Check if consumer no already exists in quotation table
#             quotation = Quotation.objects.get(consumer_no=consumer_no)
#
#             return JsonResponse({
#                 'exists': True,
#                 'consumer_name': quotation.consumer_name,
#                 'quotation_no': quotation.quotation_no,
#                 'final_amount': quotation.final_amount,   # <-- ADD THIS
#                 'date': quotation.date.strftime('%Y-%m-%d %H:%M:%S')
#             })
#         except Quotation.DoesNotExist:
#             return JsonResponse({'exists': False})
#
#     return JsonResponse({'error': 'Invalid request'})


def check_consumer(request):
    if request.method == 'POST':
        consumer_type = request.POST.get('consumer_type')
        consumer_no = request.POST.get('consumer_no')

        try:
            # Check if consumer no already exists in quotation table WITH THE SAME CONSUMER TYPE
            quotation = Quotation.objects.get(consumer_no=consumer_no, consumer_type=consumer_type)

            return JsonResponse({
                'exists': True,
                'consumer_name': quotation.consumer_name,
                'quotation_no': quotation.quotation_no,
                'final_amount': quotation.final_amount,  # Added this field
                'date': quotation.date.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Quotation.DoesNotExist:
            return JsonResponse({'exists': False})
        except Quotation.MultipleObjectsReturned:
            # Handle case where multiple quotations exist for same consumer_no and type
            quotations = Quotation.objects.filter(consumer_no=consumer_no, consumer_type=consumer_type)
            latest_quotation = quotations.latest('date')  # Get the most recent one

            return JsonResponse({
                'exists': True,
                'consumer_name': latest_quotation.consumer_name,
                'quotation_no': latest_quotation.quotation_no,
                'final_amount': latest_quotation.final_amount,
                'date': latest_quotation.date.strftime('%Y-%m-%d %H:%M:%S')
            })

    return JsonResponse({'error': 'Invalid request'})
#
# def create_quotation(request):
#     panel_companies = SolarPanelCompany.objects.all()
#     inverter_companies = InverterCompany.objects.all()
#     representatives = Representative.objects.all()
#
#     # Get terms_conditions using helper function - returns a list, not queryset
#     # This prevents any queryset evaluation errors
#     terms_conditions = get_active_terms_conditions()
#
#     # Get consumer_type and consumer_no from URL parameters
#     consumer_type = request.GET.get('consumer_type', 'Residential')
#     consumer_no = request.GET.get('consumer_no', '')
#
#     if request.method == 'POST':
#         form = QuotationForm(request.POST)
#
#         # Set terms_conditions queryset before validation to avoid "not one of the available choices" error
#         # Use raw SQL to get active term IDs to avoid boolean comparison issues
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM quotation_termsandcondition
#                     WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
#                 """)
#                 active_term_ids = [row[0] for row in cursor.fetchall()]
#             # Set queryset to include only active terms (filtering by ID only, no boolean comparison)
#             if active_term_ids:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=active_term_ids)
#             else:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#         except Exception as e:
#             # If query fails, set to empty queryset (form will still validate, but terms won't be saved)
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not set terms_conditions queryset: {e}")
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#
#             # Handle plant capacity (it's now a ForeignKey)
#             plant_capacity = form.cleaned_data.get('plant_capacity_kw')
#             if plant_capacity:
#                 quotation.plant_capacity_kw = plant_capacity
#
#             # Handle system_na - convert boolean to bit varying compatible format
#             system_na_value = form.cleaned_data.get('system_na', False)
#
#             # Store system_na value temporarily - we'll set it via raw SQL after save
#             quotation._system_na_temp = system_na_value
#             quotation.system_na = False  # Set default for NOT NULL constraint
#
#             # -----------------------------
#             # SAVE THE QUOTATION FIRST (CRITICAL)
#             # -----------------------------
#             # Try to save - if it fails due to system_na type mismatch, use raw SQL workaround
#             try:
#                 quotation.save()
#             except Exception as e:
#                 error_str = str(e)
#                 # If save fails due to system_na type issue, use raw SQL to insert
#                 if 'system_na' in error_str or 'bit varying' in error_str or 'boolean' in error_str:
#                     import logging
#                     logger = logging.getLogger(__name__)
#                     logger.warning(f"Save failed due to system_na type issue, using raw SQL workaround: {e}")
#
#                     from django.db import transaction
#                     # Use raw SQL to insert the record with correct bit varying value
#                     with transaction.atomic():
#                         with connection.cursor() as cursor:
#                             # Get quotation_no if not set
#                             if not quotation.quotation_no:
#                                 # Get all quotation numbers and extract base numbers (before underscore for revisions)
#                                 all_quotations = Quotation.objects.exclude(quotation_no__isnull=True).exclude(quotation_no='')
#                                 max_base_no = 0
#
#                                 for q in all_quotations:
#                                     # Extract base number (part before underscore if revision exists)
#                                     base_no_str = q.quotation_no.split('_')[0]
#                                     try:
#                                         base_no = int(base_no_str)
#                                         if base_no > max_base_no:
#                                             max_base_no = base_no
#                                     except (ValueError, TypeError):
#                                         continue
#
#                                 # Increment from the maximum base number found
#                                 newno = max_base_no + 1 if max_base_no > 0 else 1000
#                                 quotation.quotation_no = str(newno)
#
#                             # Ensure plant_capacity_kw_id is set
#                             if not quotation.plant_capacity_kw_id and quotation.plant_capacity_kw:
#                                 quotation.plant_capacity_kw_id = quotation.plant_capacity_kw.pk
#
#                             # Insert using raw SQL with correct bit varying value for system_na
#                             # Handle None values properly
#                             try:
#                                 # Ensure plant_capacity_kw_id is set
#                                 if quotation.plant_capacity_kw and not quotation.plant_capacity_kw_id:
#                                     quotation.plant_capacity_kw_id = quotation.plant_capacity_kw.pk
#
#                                 # Count: 40 columns total - build parameters list matching exact order
#                                 params = [
#                                     quotation.consumer_type or 'Residential',    # 1
#                                     quotation.dc_capacity,                      # 2
#                                     quotation.ac_capacity,                      # 3
#                                     1 if system_na_value else 0,                # 4 (system_na - cast in SQL)
#                                     quotation.title or 'Mr',                    # 5
#                                     quotation.consumer_name or '',              # 6
#                                     quotation.consumer_address1 or '',          # 7
#                                     quotation.consumer_address2 or '',          # 8
#                                     quotation.consumer_no or '',                # 9
#                                     quotation.consumer_mobile or '',            # 10
#                                     quotation.quotation_no or '',               # 11
#                                     quotation.date,                            # 12
#                                     quotation.created_at,                       # 13
#                                     quotation.plant_capacity_kw_id,            # 14
#                                     quotation.employee_name or '',              # 15
#                                     quotation.panel_qty or 0,                  # 16
#                                     quotation.inverter_qty or 0,               # 17
#                                     quotation.panel_type or '',                # 18
#                                     quotation.panel_capacity_watt or '',       # 19
#                                     quotation.inv_phase or 'Single Phase',     # 20
#                                     quotation.inv_capacity_kw or 0,            # 21
#                                     quotation.panel_company_names or '',       # 22 (NEW - required by DB)
#                                     quotation.inverter_company_names or '',    # 23 (NEW - required by DB)
#                                     quotation.panel_manufacturing_warranty or '', # 24
#                                     quotation.panel_performance_warranty or '', # 25
#                                     quotation.inverter_warranty or '',          # 26
#                                     quotation.structure_type or 'GI Structure', # 27
#                                     quotation.structure_back_height_ft,         # 28
#                                     quotation.structure_front_height_ft,        # 29
#                                     quotation.structure_warranty or '',         # 30
#                                     quotation.special_discount or 0,           # 31
#                                     quotation.gst_5_percent or 0,              # 32
#                                     quotation.gst_18_percent or 0,             # 33
#                                     quotation.gst_5_amount or 0,                # 34
#                                     quotation.gst_18_amount or 0,              # 35
#                                     quotation.net_amount or 0,                 # 36
#                                     quotation.final_amount or 0,               # 37
#                                     quotation.representative_names or '',       # 38
#                                     quotation.terms_conditions_text or '',      # 39
#                                     quotation.other_details or ''              # 40
#                                 ]
#
#                                 # Debug: Verify parameter count
#                                 import logging
#                                 logger = logging.getLogger(__name__)
#                                 logger.info(f"Params count: {len(params)}, Expected: 40")
#
#                                 # Build SQL with exactly 40 placeholders for 40 columns
#                                 # We have 40 columns (added panel_company_names and inverter_company_names), so we need exactly 40 placeholders
#                                 # Note: (%s)::bit(1)::bit varying counts as 1 placeholder
#                                 sql = """
#                                     INSERT INTO quotation_quotation (
#                                         consumer_type, dc_capacity, ac_capacity, system_na, title,
#                                         consumer_name, consumer_address1, consumer_address2, consumer_no,
#                                         consumer_mobile, quotation_no, date, created_at, plant_capacity_kw_id,
#                                         employee_name, panel_qty, inverter_qty, panel_type, panel_capacity_watt,
#                                         inv_phase, inv_capacity_kw, panel_company_names, inverter_company_names,
#                                         panel_manufacturing_warranty, panel_performance_warranty, inverter_warranty,
#                                         structure_type, structure_back_height_ft, structure_front_height_ft, structure_warranty,
#                                         special_discount, gst_5_percent, gst_18_percent, gst_5_amount,
#                                         gst_18_amount, net_amount, final_amount, representative_names,
#                                         terms_conditions_text, other_details
#                                     ) VALUES (
#                                         %s, %s, %s, (%s)::bit(1)::bit varying, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#                                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#                                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#                                     ) RETURNING id
#                                 """
#                                 # Verify parameter count matches placeholder count
#                                 placeholder_count = sql.count('%s')
#                                 # Debug: Print the actual SQL to see what's being executed
#                                 logger.info(f"SQL placeholder count: {placeholder_count}, Params count: {len(params)}")
#                                 logger.info(f"SQL VALUES clause: {sql.split('VALUES')[1] if 'VALUES' in sql else 'NOT FOUND'}")
#
#                                 if len(params) != placeholder_count:
#                                     # More detailed error message
#                                     error_msg = f"Parameter count mismatch: {len(params)} params but {placeholder_count} placeholders. "
#                                     error_msg += f"SQL VALUES: {sql.split('VALUES')[1][:200] if 'VALUES' in sql else 'N/A'}"
#                                     logger.error(error_msg)
#                                     raise ValueError(error_msg)
#
#                                 cursor.execute(sql, params)
#                                 quotation.id = cursor.fetchone()[0]
#                                 # Refresh the object from database
#                                 quotation.refresh_from_db()
#                             except Exception as sql_error:
#                                 logger.error(f"Raw SQL insert failed: {sql_error}")
#                                 raise
#                 else:
#                     # Re-raise if it's a different error
#                     raise
#
#             # Update system_na using raw SQL if save succeeded normally
#             if quotation.id and hasattr(quotation, '_system_na_temp'):
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         UPDATE quotation_quotation
#                         SET system_na = (%s)::bit(1)::bit varying
#                         WHERE id = %s
#                     """, [1 if quotation._system_na_temp else 0, quotation.id])
#                 delattr(quotation, '_system_na_temp')
#
#             # -----------------------------
#             # NOW SET MANY-TO-MANY RELATIONSHIPS
#             # -----------------------------
#
#             # Save form's many-to-many data
#             form.save_m2m()
#
#             # Save representatives - Use selection order if provided, otherwise preserve existing order
#             rep_ids = request.POST.getlist('representatives')
#             rep_order_str = request.POST.get('representatives_order', '').strip()
#
#             # If order is provided, use it
#             if rep_order_str:
#                 # Parse the order from comma-separated string
#                 ordered_rep_ids = [rid.strip() for rid in rep_order_str.split(',') if rid.strip() in rep_ids]
#                 # Add any remaining reps that weren't in the order (shouldn't happen, but safety)
#                 for rid in rep_ids:
#                     if rid not in ordered_rep_ids:
#                         ordered_rep_ids.append(rid)
#                 rep_ids = ordered_rep_ids
#             else:
#                 # No order provided - preserve existing order from quotation
#                 # Parse representative_names to extract the order (most reliable source)
#                 if quotation.representative_names:
#                     # representative_names format: "1. Name - Contact\n2. Name - Contact\n..."
#                     # Create a mapping of all existing representatives
#                     all_reps = {str(r.id): r for r in Representative.objects.all()}
#                     existing_reps = {str(r.id): r for r in quotation.representatives.all()}
#
#                     # Parse lines from representative_names
#                     lines = quotation.representative_names.strip().split('\n')
#                     ordered_rep_ids = []
#
#                     for line in lines:
#                         line = line.strip()
#                         if not line or '.' not in line:
#                             continue
#
#                         # Extract name from line (format: "1. Name - Contact" or "1. Name")
#                         # Remove number prefix (e.g., "1. ")
#                         name_part = line.split('.', 1)[1].strip()
#                         # Remove contact part if exists (e.g., "Name - Contact" -> "Name")
#                         name = name_part.split(' - ', 1)[0].strip()
#
#                         # Find matching representative by name
#                         for rep_id, rep in existing_reps.items():
#                             if rep.name.strip() == name.strip() and rep_id in rep_ids:
#                                 if rep_id not in ordered_rep_ids:
#                                     ordered_rep_ids.append(rep_id)
#                                 break
#
#                     # Add any new reps that weren't in the original order
#                     for rid in rep_ids:
#                         if rid not in ordered_rep_ids:
#                             ordered_rep_ids.append(rid)
#
#                     rep_ids = ordered_rep_ids if ordered_rep_ids else rep_ids
#
#             quotation.representatives.set(rep_ids)
#
#             # Build representative names for PDF in selection order
#             # Create a mapping of ID to Representative for quick lookup
#             rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
#             rep_texts = []
#             for i, rep_id in enumerate(rep_ids):
#                 if rep_id in rep_dict:
#                     r = rep_dict[rep_id]
#                     contact_str = f" - {r.contact}" if r.contact else ""
#                     rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
#             quotation.representative_names = "\n".join(rep_texts)
#
#             # Save panel companies
#             panel_ids = request.POST.getlist('panel_companies')
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list('name', flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # Save inverter companies + warranty
#             inverter_ids = request.POST.getlist('inverter_companies')
#             quotation.inverter_companies.set(inverter_ids)
#             inverter_names = []
#             warranty_values = []
#             for inv_id in inverter_ids:
#                 name = InverterCompany.objects.get(id=inv_id).name
#                 inverter_names.append(name)
#                 wt = request.POST.get(f'inverter_warranty_{inv_id}', '').strip()
#                 if wt:
#                     warranty_values.append(wt)
#             quotation.inverter_company_names = " / ".join(inverter_names)
#             quotation.inverter_warranty = " / ".join(warranty_values)
#
#             # Save other items
#             other_qs = form.cleaned_data.get('other_items')
#             other_names = []
#             if other_qs:
#                 other_names = list(other_qs.values_list('name', flat=True))
#             dynamic_items = request.POST.getlist('dynamic_other_items[]')
#             combined = []
#             for n in other_names + dynamic_items:
#                 n = n.strip()
#                 if n and n not in combined:
#                     combined.append(n)
#             quotation.other_details = " / ".join(combined)
#
#             # -----------------------------
#             # SAVE TERMS & CONDITIONS
#             # -----------------------------
#             terms_ids = request.POST.getlist('terms_conditions')
#             quotation.terms_conditions.set(terms_ids)
#
#             # Build textual representation for PDF
#             terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids)
#             terms_texts = []
#             for i, term in enumerate(terms_qs, 1):
#                 terms_texts.append(f"{i}. {term.content}")
#             quotation.terms_conditions_text = "\n".join(terms_texts)
#
#             # -----------------------------
#             # APPLY PRICING LOGIC
#             # -----------------------------
#             pricing_mode = form.cleaned_data.get('pricing_mode')
#             net_input = form.cleaned_data.get('net_amount_input')
#             final_input = form.cleaned_data.get('final_amount_input')
#
#             if pricing_mode == 'net' and net_input:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#
#             elif pricing_mode == 'final' and final_input:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             # -----------------------------
#             # FINAL SAVE WITH ALL UPDATES
#             # -----------------------------
#             quotation.save()
#
#             # Update system_na again after final save to ensure it's persisted
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s::bit varying
#                     WHERE id = %s
#                 """, ['1' if system_na_value else '0', quotation.id])
#
#             return redirect('quotation:quotation_pdf', pk=quotation.pk)
#     else:
#         # Pre-populate the form with consumer_type and consumer_no from URL parameters
#         initial_data = {
#             'consumer_type': consumer_type,
#             'consumer_no': consumer_no,
#         }
#         # Wrap form creation in try-except to handle database schema issues
#         from django.db.utils import ProgrammingError
#         try:
#             form = QuotationForm(initial=initial_data)
#         except ProgrammingError as e:
#             # If form creation fails due to boolean type issues, create form with empty queryset
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Form creation failed due to database schema issue: {e}")
#             # Create form and manually set terms_conditions to empty queryset
#             form = QuotationForm(initial=initial_data)
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         # ------------------------------------------------
#         # MAKE FIELDS READONLY ONLY IN CREATE PAGE
#         # ------------------------------------------------
#         # form.fields['consumer_type'].widget.attrs['readonly'] = True
#         form.fields['consumer_type'].widget.attrs.update({
#             'class': 'form-control',
#             'readonly': True,
#             'style': 'pointer-events: none;'
#         })
#         form.fields['consumer_no'].widget.attrs['readonly'] = True
#
#         # form = QuotationForm()
#
#     context = {
#         'form': form,
#         'panel_companies': panel_companies,
#         'inverter_companies': inverter_companies,
#         'representatives': representatives,
#         'terms_conditions': terms_conditions,
#         'passed_consumer_type': consumer_type,  # Pass to template for display
#         'passed_consumer_no': consumer_no,  # Pass to template for display
#     }
#     return render(request, 'quotation/create_quotation.html', context)

#
# def create_quotation(request):
#     panel_companies = SolarPanelCompany.objects.all()
#     inverter_companies = InverterCompany.objects.all()
#     representatives = Representative.objects.all()
#
#     # Get terms_conditions using helper function - returns a list, not queryset
#     # This prevents any queryset evaluation errors
#     terms_conditions = get_active_terms_conditions()
#
#     # Get consumer_type and consumer_no from URL parameters
#     consumer_type = request.GET.get('consumer_type', 'Residential')
#     consumer_no = request.GET.get('consumer_no', '')
#
#     if request.method == 'POST':
#         form = QuotationForm(request.POST)
#
#         # Set terms_conditions queryset before validation to avoid "not one of the available choices" error
#         # Use raw SQL to get active term IDs to avoid boolean comparison issues
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM quotation_termsandcondition
#                     WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
#                 """)
#                 active_term_ids = [row[0] for row in cursor.fetchall()]
#             # Set queryset to include only active terms (filtering by ID only, no boolean comparison)
#             if active_term_ids:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=active_term_ids)
#             else:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#         except Exception as e:
#             # If query fails, set to empty queryset (form will still validate, but terms won't be saved)
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not set terms_conditions queryset: {e}")
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#
#             # Handle plant capacity (it's now a ForeignKey)
#             plant_capacity = form.cleaned_data.get('plant_capacity_kw')
#             if plant_capacity:
#                 quotation.plant_capacity_kw = plant_capacity
#
#             # Handle system_na - convert boolean to bit varying compatible format
#             system_na_value = form.cleaned_data.get('system_na', False)
#
#             # Store system_na value temporarily - we'll set it via raw SQL after save
#             quotation._system_na_temp = system_na_value
#             quotation.system_na = False  # Set default for NOT NULL constraint
#
#             # -----------------------------
#             # SAVE THE QUOTATION FIRST (CRITICAL)
#             # -----------------------------
#             # Try to save - if it fails due to system_na type mismatch, use raw SQL workaround
#             try:
#                 quotation.save()
#             except Exception as e:
#                 error_str = str(e)
#                 # If save fails due to system_na type issue, use raw SQL to insert
#                 if 'system_na' in error_str or 'bit varying' in error_str or 'boolean' in error_str:
#                     import logging
#                     logger = logging.getLogger(__name__)
#                     logger.warning(f"Save failed due to system_na type issue, using raw SQL workaround: {e}")
#
#                     from django.db import transaction
#                     # Use raw SQL to insert the record with correct bit varying value
#                     with transaction.atomic():
#                         with connection.cursor() as cursor:
#                             # Get quotation_no if not set
#                             if not quotation.quotation_no:
#                                 # Get all quotation numbers and extract base numbers (before underscore for revisions)
#                                 all_quotations = Quotation.objects.exclude(quotation_no__isnull=True).exclude(
#                                     quotation_no='')
#                                 max_base_no = 0
#
#                                 for q in all_quotations:
#                                     # Extract base number (part before underscore if revision exists)
#                                     base_no_str = q.quotation_no.split('_')[0]
#                                     try:
#                                         base_no = int(base_no_str)
#                                         if base_no > max_base_no:
#                                             max_base_no = base_no
#                                     except (ValueError, TypeError):
#                                         continue
#
#                                 # Increment from the maximum base number found
#                                 newno = max_base_no + 1 if max_base_no > 0 else 1000
#                                 quotation.quotation_no = str(newno)
#
#                             # Ensure plant_capacity_kw_id is set
#                             if not quotation.plant_capacity_kw_id and quotation.plant_capacity_kw:
#                                 quotation.plant_capacity_kw_id = quotation.plant_capacity_kw.pk
#
#                             # Insert using raw SQL with correct bit varying value for system_na
#                             # Handle None values properly
#                             try:
#                                 # Ensure plant_capacity_kw_id is set
#                                 if quotation.plant_capacity_kw and not quotation.plant_capacity_kw_id:
#                                     quotation.plant_capacity_kw_id = quotation.plant_capacity_kw.pk
#
#                                 # Count: 41 columns total - added electricity_unit_rate
#                                 params = [
#                                     quotation.consumer_type or 'Residential',  # 1
#                                     quotation.dc_capacity,  # 2
#                                     quotation.ac_capacity,  # 3
#                                     1 if system_na_value else 0,  # 4 (system_na - cast in SQL)
#                                     quotation.title or 'Mr',  # 5
#                                     quotation.consumer_name or '',  # 6
#                                     quotation.consumer_address1 or '',  # 7
#                                     quotation.consumer_address2 or '',  # 8
#                                     quotation.consumer_no or '',  # 9
#                                     quotation.consumer_mobile or '',  # 10
#                                     quotation.quotation_no or '',  # 11
#                                     quotation.date,  # 12
#                                     quotation.created_at,  # 13
#                                     quotation.plant_capacity_kw_id,  # 14
#                                     quotation.employee_name or '',  # 15
#                                     quotation.panel_qty or 0,  # 16
#                                     quotation.inverter_qty or 0,  # 17
#                                     quotation.panel_type or '',  # 18
#                                     quotation.panel_capacity_watt or '',  # 19
#                                     quotation.inv_phase or 'Single Phase',  # 20
#                                     quotation.inv_capacity_kw or 0,  # 21
#                                     quotation.panel_company_names or '',  # 22
#                                     quotation.inverter_company_names or '',  # 23
#                                     quotation.panel_manufacturing_warranty or '',  # 24
#                                     quotation.panel_performance_warranty or '',  # 25
#                                     quotation.inverter_warranty or '',  # 26
#                                     quotation.structure_type or 'GI Structure',  # 27
#                                     quotation.structure_back_height_ft,  # 28
#                                     quotation.structure_front_height_ft,  # 29
#                                     quotation.structure_warranty or '',  # 30
#                                     quotation.special_discount or 0,  # 31
#                                     quotation.gst_5_percent or 0,  # 32
#                                     quotation.gst_18_percent or 0,  # 33
#                                     quotation.gst_5_amount or 0,  # 34
#                                     quotation.gst_18_amount or 0,  # 35
#                                     quotation.net_amount or 0,  # 36
#                                     quotation.final_amount or 0,  # 37
#                                     quotation.representative_names or '',  # 38
#                                     quotation.terms_conditions_text or '',  # 39
#                                     quotation.other_details or '',  # 40
#                                     quotation.electricity_unit_rate or Decimal('11.00'),  # 41 - NEW
#                                 ]
#
#                                 # Build SQL with 41 placeholders for 41 columns
#                                 sql = """
#                                     INSERT INTO quotation_quotation (
#                                         consumer_type, dc_capacity, ac_capacity, system_na, title,
#                                         consumer_name, consumer_address1, consumer_address2, consumer_no,
#                                         consumer_mobile, quotation_no, date, created_at, plant_capacity_kw_id,
#                                         employee_name, panel_qty, inverter_qty, panel_type, panel_capacity_watt,
#                                         inv_phase, inv_capacity_kw, panel_company_names, inverter_company_names,
#                                         panel_manufacturing_warranty, panel_performance_warranty, inverter_warranty,
#                                         structure_type, structure_back_height_ft, structure_front_height_ft, structure_warranty,
#                                         special_discount, gst_5_percent, gst_18_percent, gst_5_amount,
#                                         gst_18_amount, net_amount, final_amount, representative_names,
#                                         terms_conditions_text, other_details, electricity_unit_rate
#                                     ) VALUES (
#                                         %s, %s, %s, (%s)::bit(1)::bit varying, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#                                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#                                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#                                     ) RETURNING id
#                                 """
#
#                                 cursor.execute(sql, params)
#                                 quotation.id = cursor.fetchone()[0]
#                                 # Refresh the object from database
#                                 quotation.refresh_from_db()
#                             except Exception as sql_error:
#                                 logger.error(f"Raw SQL insert failed: {sql_error}")
#                                 raise
#                 else:
#                     # Re-raise if it's a different error
#                     raise
#
#             # Update system_na using raw SQL if save succeeded normally
#             if quotation.id and hasattr(quotation, '_system_na_temp'):
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         UPDATE quotation_quotation
#                         SET system_na = (%s)::bit(1)::bit varying
#                         WHERE id = %s
#                     """, [1 if quotation._system_na_temp else 0, quotation.id])
#                 delattr(quotation, '_system_na_temp')
#
#             # -----------------------------
#             # NOW SET MANY-TO-MANY RELATIONSHIPS
#             # -----------------------------
#
#             # Save form's many-to-many data
#             form.save_m2m()
#
#             # Save representatives - Use selection order if provided, otherwise preserve existing order
#             rep_ids = request.POST.getlist('representatives')
#             rep_order_str = request.POST.get('representatives_order', '').strip()
#
#             # If order is provided, use it
#             if rep_order_str:
#                 # Parse the order from comma-separated string
#                 ordered_rep_ids = [rid.strip() for rid in rep_order_str.split(',') if rid.strip() in rep_ids]
#                 # Add any remaining reps that weren't in the order (shouldn't happen, but safety)
#                 for rid in rep_ids:
#                     if rid not in ordered_rep_ids:
#                         ordered_rep_ids.append(rid)
#                 rep_ids = ordered_rep_ids
#             else:
#                 # No order provided - preserve existing order from quotation
#                 # Parse representative_names to extract the order (most reliable source)
#                 if quotation.representative_names:
#                     # representative_names format: "1. Name - Contact\n2. Name - Contact\n..."
#                     # Create a mapping of all existing representatives
#                     all_reps = {str(r.id): r for r in Representative.objects.all()}
#                     existing_reps = {str(r.id): r for r in quotation.representatives.all()}
#
#                     # Parse lines from representative_names
#                     lines = quotation.representative_names.strip().split('\n')
#                     ordered_rep_ids = []
#
#                     for line in lines:
#                         line = line.strip()
#                         if not line or '.' not in line:
#                             continue
#
#                         # Extract name from line (format: "1. Name - Contact" or "1. Name")
#                         # Remove number prefix (e.g., "1. ")
#                         name_part = line.split('.', 1)[1].strip()
#                         # Remove contact part if exists (e.g., "Name - Contact" -> "Name")
#                         name = name_part.split(' - ', 1)[0].strip()
#
#                         # Find matching representative by name
#                         for rep_id, rep in existing_reps.items():
#                             if rep.name.strip() == name.strip() and rep_id in rep_ids:
#                                 if rep_id not in ordered_rep_ids:
#                                     ordered_rep_ids.append(rep_id)
#                                 break
#
#                     # Add any new reps that weren't in the original order
#                     for rid in rep_ids:
#                         if rid not in ordered_rep_ids:
#                             ordered_rep_ids.append(rid)
#
#                     rep_ids = ordered_rep_ids if ordered_rep_ids else rep_ids
#
#             quotation.representatives.set(rep_ids)
#
#             # Build representative names for PDF in selection order
#             # Create a mapping of ID to Representative for quick lookup
#             rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
#             rep_texts = []
#             for i, rep_id in enumerate(rep_ids):
#                 if rep_id in rep_dict:
#                     r = rep_dict[rep_id]
#                     contact_str = f" - {r.contact}" if r.contact else ""
#                     rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
#             quotation.representative_names = "\n".join(rep_texts)
#
#             # Save panel companies
#             panel_ids = request.POST.getlist('panel_companies')
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list('name', flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # Save inverter companies + warranty
#             inverter_ids = request.POST.getlist('inverter_companies')
#             quotation.inverter_companies.set(inverter_ids)
#             inverter_names = []
#             warranty_values = []
#             for inv_id in inverter_ids:
#                 name = InverterCompany.objects.get(id=inv_id).name
#                 inverter_names.append(name)
#                 wt = request.POST.get(f'inverter_warranty_{inv_id}', '').strip()
#                 if wt:
#                     warranty_values.append(wt)
#             quotation.inverter_company_names = " / ".join(inverter_names)
#             quotation.inverter_warranty = " / ".join(warranty_values)
#
#             # Save other items
#             other_qs = form.cleaned_data.get('other_items')
#             other_names = []
#             if other_qs:
#                 other_names = list(other_qs.values_list('name', flat=True))
#             dynamic_items = request.POST.getlist('dynamic_other_items[]')
#             combined = []
#             for n in other_names + dynamic_items:
#                 n = n.strip()
#                 if n and n not in combined:
#                     combined.append(n)
#             quotation.other_details = " / ".join(combined)
#
#             # -----------------------------
#             # SAVE TERMS & CONDITIONS
#             # -----------------------------
#             terms_ids = request.POST.getlist('terms_conditions')
#             quotation.terms_conditions.set(terms_ids)
#
#             # Build textual representation for PDF
#             terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids)
#             terms_texts = []
#             for i, term in enumerate(terms_qs, 1):
#                 terms_texts.append(f"{i}. {term.content}")
#             quotation.terms_conditions_text = "\n".join(terms_texts)
#
#             # -----------------------------
#             # APPLY PRICING LOGIC
#             # -----------------------------
#             pricing_mode = form.cleaned_data.get('pricing_mode')
#             net_input = form.cleaned_data.get('net_amount_input')
#             final_input = form.cleaned_data.get('final_amount_input')
#
#             if pricing_mode == 'net' and net_input:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#
#             elif pricing_mode == 'final' and final_input:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             # -----------------------------
#             # FINAL SAVE WITH ALL UPDATES
#             # -----------------------------
#             quotation.save()
#
#             # Update system_na again after final save to ensure it's persisted
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s::bit varying
#                     WHERE id = %s
#                 """, ['1' if system_na_value else '0', quotation.id])
#
#             # Check if it's an AJAX request
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'success': True,
#                     'quotation_id': quotation.pk,
#                     'message': 'Quotation saved successfully!'
#                 })
#             else:
#                 # For non-AJAX requests, redirect to regular PDF
#                 return redirect('quotation:quotation_pdf', pk=quotation.pk)
#         else:
#             # Form is invalid
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Form validation failed',
#                     'errors': form.errors
#                 })
#     else:
#         # Pre-populate the form with consumer_type and consumer_no from URL parameters
#         initial_data = {
#             'consumer_type': consumer_type,
#             'consumer_no': consumer_no,
#         }
#         # Wrap form creation in try-except to handle database schema issues
#         from django.db.utils import ProgrammingError
#         try:
#             form = QuotationForm(initial=initial_data)
#         except ProgrammingError as e:
#             # If form creation fails due to boolean type issues, create form with empty queryset
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Form creation failed due to database schema issue: {e}")
#             # Create form and manually set terms_conditions to empty queryset
#             form = QuotationForm(initial=initial_data)
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         # ------------------------------------------------
#         # MAKE FIELDS READONLY ONLY IN CREATE PAGE
#         # ------------------------------------------------
#         form.fields['consumer_type'].widget.attrs.update({
#             'class': 'form-control',
#             'readonly': True,
#             'style': 'pointer-events: none;'
#         })
#         form.fields['consumer_no'].widget.attrs['readonly'] = True
#
#     context = {
#         'form': form,
#         'panel_companies': panel_companies,
#         'inverter_companies': inverter_companies,
#         'representatives': representatives,
#         'terms_conditions': terms_conditions,
#         'passed_consumer_type': consumer_type,  # Pass to template for display
#         'passed_consumer_no': consumer_no,  # Pass to template for display
#     }
#     return render(request, 'quotation/create_quotation.html', context)

def create_quotation(request):
    panel_companies = SolarPanelCompany.objects.all()
    inverter_companies = InverterCompany.objects.all()
    representatives = Representative.objects.all()

    # Get terms_conditions using helper function - returns a list, not queryset
    # This prevents any queryset evaluation errors
    terms_conditions = get_active_terms_conditions()

    # Get consumer_type and consumer_no from URL parameters
    consumer_type = request.GET.get('consumer_type', 'Residential')
    consumer_no = request.GET.get('consumer_no', '')

    if request.method == 'POST':
        form = QuotationForm(request.POST, form_user=request.user)

        # Set terms_conditions queryset before validation to avoid "not one of the available choices" error
        # Use raw SQL to get active term IDs to avoid boolean comparison issues
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM quotation_termsandcondition
                    WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
                """)
                active_term_ids = [row[0] for row in cursor.fetchall()]
            # Set queryset to include only active terms (filtering by ID only, no boolean comparison)
            if active_term_ids:
                form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=active_term_ids)
            else:
                form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
        except Exception as e:
            # If query fails, set to empty queryset (form will still validate, but terms won't be saved)
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not set terms_conditions queryset: {e}")
            form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()

        if form.is_valid():
            quotation = form.save(commit=False)

            # Handle new fields manually since they're not in the model
            quotation.consumer_state = request.POST.get('consumer_state', '')
            quotation.consumer_email = request.POST.get('consumer_email', '')
            quotation.project_type = request.POST.get('project_type', '')

            # Handle plant capacity (it's now a ForeignKey)
            plant_capacity = form.cleaned_data.get('plant_capacity_kw')
            if plant_capacity:
                quotation.plant_capacity_kw = plant_capacity

            # Handle system_na - convert boolean to bit varying compatible format
            system_na_value = form.cleaned_data.get('system_na', False)

            # Store system_na value temporarily - we'll set it via raw SQL after save
            quotation._system_na_temp = system_na_value
            quotation.system_na = False  # Set default for NOT NULL constraint

            # -----------------------------
            # SAVE THE QUOTATION FIRST (CRITICAL)
            # -----------------------------
            # Try to save - if it fails due to system_na type mismatch, use raw SQL workaround
            try:
                quotation.save()
            except Exception as e:
                error_str = str(e)
                # If save fails due to system_na type issue, use raw SQL to insert
                if 'system_na' in error_str or 'bit varying' in error_str or 'boolean' in error_str:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Save failed due to system_na type issue, using raw SQL workaround: {e}")

                    from django.db import transaction
                    # Use raw SQL to insert the record with correct bit varying value
                    with transaction.atomic():
                        with connection.cursor() as cursor:
                            # Get quotation_no if not set
                            if not quotation.quotation_no:
                                # Get all quotation numbers and extract base numbers (before underscore for revisions)
                                all_quotations = Quotation.objects.exclude(quotation_no__isnull=True).exclude(
                                    quotation_no='')
                                max_base_no = 0

                                for q in all_quotations:
                                    # Extract base number (part before underscore if revision exists)
                                    base_no_str = q.quotation_no.split('_')[0]
                                    try:
                                        base_no = int(base_no_str)
                                        if base_no > max_base_no:
                                            max_base_no = base_no
                                    except (ValueError, TypeError):
                                        continue

                                # Increment from the maximum base number found
                                newno = max_base_no + 1 if max_base_no > 0 else 1000
                                quotation.quotation_no = str(newno)

                            # Ensure plant_capacity_kw_id is set
                            if not quotation.plant_capacity_kw_id and quotation.plant_capacity_kw:
                                quotation.plant_capacity_kw_id = quotation.plant_capacity_kw.pk

                            # Insert using raw SQL with correct bit varying value for system_na
                            # Handle None values properly
                            try:
                                # Ensure plant_capacity_kw_id is set
                                if quotation.plant_capacity_kw and not quotation.plant_capacity_kw_id:
                                    quotation.plant_capacity_kw_id = quotation.plant_capacity_kw.pk

                                # Count: 44 columns total - added new fields
                                params = [
                                    quotation.consumer_type or 'Residential',  # 1
                                    quotation.dc_capacity,  # 2
                                    quotation.ac_capacity,  # 3
                                    1 if system_na_value else 0,  # 4 (system_na - cast in SQL)
                                    quotation.title or 'Mr',  # 5
                                    quotation.consumer_name or '',  # 6
                                    quotation.consumer_address1 or '',  # 7
                                    quotation.consumer_address2 or '',  # 8
                                    quotation.consumer_no or '',  # 9
                                    quotation.consumer_mobile or '',  # 10
                                    quotation.consumer_state or '',  # 11 - NEW
                                    quotation.consumer_email or '',  # 12 - NEW
                                    quotation.project_type or '',  # 13 - NEW
                                    quotation.quotation_no or '',  # 14
                                    quotation.date,  # 15
                                    quotation.created_at,  # 16
                                    quotation.plant_capacity_kw_id,  # 17
                                    quotation.employee_name or '',  # 18
                                    quotation.panel_qty or 0,  # 19
                                    quotation.inverter_qty or 0,  # 20
                                    quotation.panel_type or '',  # 21
                                    quotation.panel_capacity_watt or '',  # 22
                                    quotation.inv_phase or 'Single Phase',  # 23
                                    quotation.inv_capacity_kw or 0,  # 24
                                    quotation.panel_company_names or '',  # 25
                                    quotation.inverter_company_names or '',  # 26
                                    quotation.panel_manufacturing_warranty or '',  # 27
                                    quotation.panel_performance_warranty or '',  # 28
                                    quotation.inverter_warranty or '',  # 29
                                    quotation.structure_type or 'GI Structure',  # 30
                                    quotation.structure_back_height_ft,  # 31
                                    quotation.structure_front_height_ft,  # 32
                                    quotation.structure_warranty or '',  # 33
                                    quotation.special_discount or 0,  # 34
                                    quotation.gst_5_percent or 0,  # 35
                                    quotation.gst_18_percent or 0,  # 36
                                    quotation.gst_5_amount or 0,  # 37
                                    quotation.gst_18_amount or 0,  # 38
                                    quotation.net_amount or 0,  # 39
                                    quotation.final_amount or 0,  # 40
                                    quotation.representative_names or '',  # 41
                                    quotation.terms_conditions_text or '',  # 42
                                    quotation.other_details or '',  # 43
                                    quotation.electricity_unit_rate or Decimal('11.00'),  # 44
                                    quotation.assigned_associate_id,  # 45
                                ]

                                # Build SQL (includes assigned_associate_id)
                                sql = """
                                    INSERT INTO quotation_quotation (
                                        consumer_type, dc_capacity, ac_capacity, system_na, title,
                                        consumer_name, consumer_address1, consumer_address2, consumer_no,
                                        consumer_mobile, consumer_state, consumer_email, project_type,
                                        quotation_no, date, created_at, plant_capacity_kw_id,
                                        employee_name, panel_qty, inverter_qty, panel_type, panel_capacity_watt,
                                        inv_phase, inv_capacity_kw, panel_company_names, inverter_company_names,
                                        panel_manufacturing_warranty, panel_performance_warranty, inverter_warranty,
                                        structure_type, structure_back_height_ft, structure_front_height_ft, structure_warranty,
                                        special_discount, gst_5_percent, gst_18_percent, gst_5_amount,
                                        gst_18_amount, net_amount, final_amount, representative_names,
                                        terms_conditions_text, other_details, electricity_unit_rate,
                                        assigned_associate_id
                                    ) VALUES (
                                        %s, %s, %s, (%s)::bit(1)::bit varying, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                    ) RETURNING id
                                """

                                cursor.execute(sql, params)
                                quotation.id = cursor.fetchone()[0]
                                # Refresh the object from database
                                quotation.refresh_from_db()
                            except Exception as sql_error:
                                logger.error(f"Raw SQL insert failed: {sql_error}")
                                raise
                else:
                    # Re-raise if it's a different error
                    raise

            # Update system_na using raw SQL if save succeeded normally
            if quotation.id and hasattr(quotation, '_system_na_temp'):
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE quotation_quotation 
                        SET system_na = (%s)::bit(1)::bit varying
                        WHERE id = %s
                    """, [1 if quotation._system_na_temp else 0, quotation.id])
                delattr(quotation, '_system_na_temp')

            # -----------------------------
            # NOW SET MANY-TO-MANY RELATIONSHIPS
            # -----------------------------

            # Save form's many-to-many data
            form.save_m2m()

            # Save representatives - Use selection order if provided, otherwise preserve existing order
            rep_ids = request.POST.getlist('representatives')
            rep_order_str = request.POST.get('representatives_order', '').strip()

            # If order is provided, use it
            if rep_order_str:
                # Parse the order from comma-separated string
                ordered_rep_ids = [rid.strip() for rid in rep_order_str.split(',') if rid.strip() in rep_ids]
                # Add any remaining reps that weren't in the order (shouldn't happen, but safety)
                for rid in rep_ids:
                    if rid not in ordered_rep_ids:
                        ordered_rep_ids.append(rid)
                rep_ids = ordered_rep_ids
            else:
                # No order provided - preserve existing order from quotation
                # Parse representative_names to extract the order (most reliable source)
                if quotation.representative_names:
                    # representative_names format: "1. Name - Contact\n2. Name - Contact\n..."
                    # Create a mapping of all existing representatives
                    all_reps = {str(r.id): r for r in Representative.objects.all()}
                    existing_reps = {str(r.id): r for r in quotation.representatives.all()}

                    # Parse lines from representative_names
                    lines = quotation.representative_names.strip().split('\n')
                    ordered_rep_ids = []

                    for line in lines:
                        line = line.strip()
                        if not line or '.' not in line:
                            continue

                        # Extract name from line (format: "1. Name - Contact" or "1. Name")
                        # Remove number prefix (e.g., "1. ")
                        name_part = line.split('.', 1)[1].strip()
                        # Remove contact part if exists (e.g., "Name - Contact" -> "Name")
                        name = name_part.split(' - ', 1)[0].strip()

                        # Find matching representative by name
                        for rep_id, rep in existing_reps.items():
                            if rep.name.strip() == name.strip() and rep_id in rep_ids:
                                if rep_id not in ordered_rep_ids:
                                    ordered_rep_ids.append(rep_id)
                                break

                    # Add any new reps that weren't in the original order
                    for rid in rep_ids:
                        if rid not in ordered_rep_ids:
                            ordered_rep_ids.append(rid)

                    rep_ids = ordered_rep_ids if ordered_rep_ids else rep_ids

            quotation.representatives.set(rep_ids)

            # Build representative names for PDF in selection order
            # Create a mapping of ID to Representative for quick lookup
            rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
            rep_texts = []
            for i, rep_id in enumerate(rep_ids):
                if rep_id in rep_dict:
                    r = rep_dict[rep_id]
                    contact_str = f" - {r.contact}" if r.contact else ""
                    rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
            quotation.representative_names = "\n".join(rep_texts)

            # Save panel companies
            panel_ids = request.POST.getlist('panel_companies')
            quotation.panel_companies.set(panel_ids)
            panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list('name', flat=True)
            quotation.panel_company_names = " / ".join(panel_names)

            # Save inverter companies + warranty
            inverter_ids = request.POST.getlist('inverter_companies')
            quotation.inverter_companies.set(inverter_ids)
            inverter_names = []
            warranty_values = []
            for inv_id in inverter_ids:
                name = InverterCompany.objects.get(id=inv_id).name
                inverter_names.append(name)
                wt = request.POST.get(f'inverter_warranty_{inv_id}', '').strip()
                if wt:
                    warranty_values.append(wt)
            quotation.inverter_company_names = " / ".join(inverter_names)
            quotation.inverter_warranty = " / ".join(warranty_values)

            # Save other items
            other_qs = form.cleaned_data.get('other_items')
            other_names = []
            if other_qs:
                other_names = list(other_qs.values_list('name', flat=True))
            dynamic_items = request.POST.getlist('dynamic_other_items[]')
            combined = []
            for n in other_names + dynamic_items:
                n = n.strip()
                if n and n not in combined:
                    combined.append(n)
            quotation.other_details = " / ".join(combined)

            # -----------------------------
            # SAVE TERMS & CONDITIONS
            # -----------------------------
            terms_ids = request.POST.getlist('terms_conditions')
            quotation.terms_conditions.set(terms_ids)

            # Build textual representation for PDF
            terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids)
            terms_texts = []
            for i, term in enumerate(terms_qs, 1):
                terms_texts.append(f"{i}. {term.content}")
            quotation.terms_conditions_text = "\n".join(terms_texts)

            # -----------------------------
            # APPLY PRICING LOGIC
            # -----------------------------
            pricing_mode = form.cleaned_data.get('pricing_mode')
            net_input = form.cleaned_data.get('net_amount_input')
            final_input = form.cleaned_data.get('final_amount_input')

            if pricing_mode == 'net' and net_input:
                quotation.net_amount = net_input
                quotation.calculate_from_net()

            elif pricing_mode == 'final' and final_input:
                quotation.final_amount = final_input
                quotation.calculate_from_final()

            # -----------------------------
            # FINAL SAVE WITH ALL UPDATES
            # -----------------------------
            quotation.save()

            # Update system_na again after final save to ensure it's persisted
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE quotation_quotation 
                    SET system_na = %s::bit varying 
                    WHERE id = %s
                """, ['1' if system_na_value else '0', quotation.id])

            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'quotation_id': quotation.pk,
                    'message': 'Quotation saved successfully!'
                })
            else:
                # For non-AJAX requests, redirect to regular PDF
                return redirect('quotation:quotation_pdf', pk=quotation.pk)
        else:
            # Form is invalid
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Form validation failed',
                    'errors': form.errors
                })
    else:
        # Pre-populate the form with consumer_type and consumer_no from URL parameters
        initial_data = {
            'consumer_type': consumer_type,
            'consumer_no': consumer_no,
        }
        if (
            request.user.is_authenticated
            and is_associate_staff(request.user)
            and not request.user.is_superuser
        ):
            initial_data['assigned_associate'] = request.user.pk
        # Wrap form creation in try-except to handle database schema issues
        from django.db.utils import ProgrammingError
        try:
            form = QuotationForm(initial=initial_data, form_user=request.user)
        except ProgrammingError as e:
            # If form creation fails due to boolean type issues, create form with empty queryset
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Form creation failed due to database schema issue: {e}")
            # Create form and manually set terms_conditions to empty queryset
            form = QuotationForm(initial=initial_data, form_user=request.user)
            form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()

        # ------------------------------------------------
        # MAKE FIELDS READONLY ONLY IN CREATE PAGE
        # ------------------------------------------------
        form.fields['consumer_type'].widget.attrs.update({
            'class': 'form-control',
            'readonly': True,
            'style': 'pointer-events: none;'
        })
        form.fields['consumer_no'].widget.attrs['readonly'] = True

    context = {
        'form': form,
        'panel_companies': panel_companies,
        'inverter_companies': inverter_companies,
        'representatives': representatives,
        'terms_conditions': terms_conditions,
        'passed_consumer_type': consumer_type,  # Pass to template for display
        'passed_consumer_no': consumer_no,  # Pass to template for display
    }
    return render(request, 'quotation/create_quotation.html', context)

#
# @login_required(login_url='user-login')
# def industrial_quotation_pdf(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#     reps = list(quotation.representatives.all())
#
#     # Format other_details to replace / with ,
#     if quotation.other_details:
#         formatted_other_details = quotation.other_details.replace(' / ', ', ').replace('/', ', ')
#     else:
#         formatted_other_details = ''
#
#     # Your existing calculations
#     plant_capacity = float(quotation.plant_capacity_kw.capacity) if quotation.plant_capacity_kw else 0.0
#     # unit_rate = 11
#     unit_rate = float(quotation.electricity_unit_rate or 11.00)  # Use stored value
#
#     subsidy = 78000.0
#     investment_cost = float(quotation.final_amount or quotation.net_amount or 0)
#
#     units_generated_per_year = plant_capacity * 4 * 365
#     yearly_saving = units_generated_per_year * unit_rate
#     after_subsidy_amount = investment_cost - subsidy
#     payback_period = round(after_subsidy_amount / yearly_saving, 1) if yearly_saving > 0 else 0
#
#     amount_words = amount_in_words(quotation.final_amount)
#
#     try:
#         net = float(quotation.net_amount or 0)
#         disc = float(quotation.special_discount or 0)
#         after_discount_amount = net - disc
#     except:
#         after_discount_amount = 0
#
#     # -------------------------------
#     # BASIC COST PER WATT (FLOAT)
#     # -------------------------------
#     basic_cost_per_watt = 0.0
#
#     if quotation.plant_capacity_kw and quotation.plant_capacity_kw.capacity:
#         plant_capacity_kw = float(quotation.plant_capacity_kw.capacity)
#         total_watts = plant_capacity_kw * 1000
#
#         if total_watts > 0:
#             basic_cost_per_watt = round(
#                 after_discount_amount / total_watts, 2
#             )
#
#     context = {
#         'quotation': quotation,
#         'formatted_other_details': formatted_other_details,  # Add the formatted version
#         'units_generated_per_year': units_generated_per_year,
#         'yearly_saving': yearly_saving,
#         'after_subsidy_amount': after_subsidy_amount,
#         'payback_period': payback_period,
#         'subsidy_amount': subsidy,
#         'amount_words': amount_words,
#         'unit_rate': unit_rate,
#         'after_discount_amount': after_discount_amount,
#         'basic_cost_per_watt': basic_cost_per_watt,
#         'representatives': reps,
#     }
#
#     html = render_to_string('quotation/industrial_quotation.html', context)
#     sanitized_html = sanitize_css_units(html, content_width_pts=525)
#
#     result = BytesIO()
#     pisa_status = pisa.CreatePDF(
#         sanitized_html,
#         dest=result,
#         encoding='utf-8',
#         link_callback=link_callback,
#     )
#
#     if pisa_status.err:
#         return HttpResponse(
#             "Error creating PDF.<hr><pre>%s</pre>" % sanitized_html[:2000],
#             status=500
#         )
#
#     response = HttpResponse(result.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'filename="quotation_{quotation.pk}.pdf"'
#     return response

#
# def industrial_quotation_pdf(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#     # Refresh from database to ensure all fields are loaded
#     quotation.refresh_from_db()
#     reps = list(quotation.representatives.all())
#
#     # Format other_details to replace / with ,
#     if quotation.other_details:
#         formatted_other_details = quotation.other_details.replace(' / ', ', ').replace('/', ', ')
#     else:
#         formatted_other_details = ''
#
#     # Your existing calculations
#     plant_capacity = float(quotation.plant_capacity_kw.capacity) if quotation.plant_capacity_kw else 0.0
#     # Use electricity_unit_rate from the model
#     unit_rate = float(quotation.electricity_unit_rate or 11.00)
#     subsidy = 78000.0
#     investment_cost = float(quotation.final_amount or quotation.net_amount or 0)
#
#     units_generated_per_year = plant_capacity * 4 * 365
#     yearly_saving = units_generated_per_year * unit_rate
#     after_subsidy_amount = investment_cost - subsidy
#     payback_period = round(after_subsidy_amount / yearly_saving, 1) if yearly_saving > 0 else 0
#
#     amount_words = amount_in_words(quotation.final_amount)
#
#     try:
#         net = float(quotation.net_amount or 0)
#         disc = float(quotation.special_discount or 0)
#         after_discount_amount = net - disc
#     except:
#         after_discount_amount = 0
#
#     # BASIC COST PER WATT (FLOAT)
#     basic_cost_per_watt = 0.0
#
#     if quotation.plant_capacity_kw and quotation.plant_capacity_kw.capacity:
#         plant_capacity_kw = float(quotation.plant_capacity_kw.capacity)
#         total_watts = plant_capacity_kw * 1000
#
#         if total_watts > 0:
#             basic_cost_per_watt = round(
#                 after_discount_amount / total_watts, 2
#             )
#
#     # Get terms with yellow background flag - check raw database value
#     terms_with_yellow = set()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT id FROM quotation_termsandcondition
#                 WHERE CAST(has_yellow_background AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
#             """)
#             terms_with_yellow = {row[0] for row in cursor.fetchall()}
#     except Exception as e:
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.warning(f"Could not fetch terms with yellow background: {e}")
#
#     # Format date for template - ensure it's available and formatted
#     from django.utils import timezone
#
#     # Get the date value
#     date_value = quotation.date if quotation.date else (
#         quotation.created_at if quotation.created_at else timezone.now())
#
#     # Format the date as string - handle both datetime objects and strings
#     try:
#         if date_value:
#             # Check if it's a datetime object (has strftime method)
#             if hasattr(date_value, 'strftime') and callable(getattr(date_value, 'strftime', None)):
#                 formatted_date = date_value.strftime('%d/%m/%Y')
#             elif isinstance(date_value, str):
#                 # If it's a string, try to extract date part or use as-is
#                 # If it looks like a date string, try to format it
#                 if len(date_value) >= 10:
#                     # Try to extract YYYY-MM-DD format
#                     date_part = date_value[:10] if len(date_value) >= 10 else date_value
#                     # Reverse from YYYY-MM-DD to DD/MM/YYYY
#                     try:
#                         parts = date_part.split('-')
#                         if len(parts) == 3:
#                             formatted_date = f"{parts[2]}/{parts[1]}/{parts[0]}"
#                         else:
#                             formatted_date = date_value
#                     except:
#                         formatted_date = date_value
#                 else:
#                     formatted_date = date_value
#             else:
#                 # Convert to string as fallback
#                 formatted_date = str(date_value)
#         else:
#             formatted_date = timezone.now().strftime('%d/%m/%Y')
#     except Exception as e:
#         # Fallback to current date if anything fails
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.warning(f"Error formatting date: {e}")
#         formatted_date = timezone.now().strftime('%d/%m/%Y')
#
#     context = {
#         'quotation': quotation,
#         'quotation_date': date_value,  # Pass date object for template
#         'formatted_date': formatted_date,  # Pass pre-formatted date string
#         'formatted_other_details': formatted_other_details,  # Add the formatted version
#         'units_generated_per_year': units_generated_per_year,
#         'yearly_saving': yearly_saving,
#         'after_subsidy_amount': after_subsidy_amount,
#         'payback_period': payback_period,
#         'subsidy_amount': subsidy,
#         'amount_words': amount_words,
#         'unit_rate': unit_rate,
#         'after_discount_amount': after_discount_amount,
#         'basic_cost_per_watt': basic_cost_per_watt,
#         'representatives': reps,
#         'terms_with_yellow': terms_with_yellow,  # Set of term IDs with yellow background
#     }
#
#     html = render_to_string('quotation/industrial_quotation.html', context)
#     sanitized_html = sanitize_css_units(html, content_width_pts=525)
#
#     result = BytesIO()
#     pisa_status = pisa.CreatePDF(
#         sanitized_html,
#         dest=result,
#         encoding='utf-8',
#         link_callback=link_callback,
#     )
#
#     if pisa_status.err:
#         return HttpResponse(
#             "Error creating PDF.<hr><pre>%s</pre>" % sanitized_html[:2000],
#             status=500
#         )
#
#     response = HttpResponse(result.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'filename="industrial_quotation_{quotation.pk}.pdf"'
#     return response

def industrial_quotation_pdf(request, pk):
    quotation = get_quotation_or_404_for_request(request, pk)
    # Refresh from database to ensure all fields are loaded
    quotation.refresh_from_db()
    reps = list(quotation.representatives.all())

    # Format other_details to replace / with ,
    if quotation.other_details:
        formatted_other_details = quotation.other_details.replace(' / ', ', ').replace('/', ', ')
    else:
        formatted_other_details = ''

    # Your existing calculations
    plant_capacity = float(quotation.plant_capacity_kw.capacity) if quotation.plant_capacity_kw else 0.0
    # Use electricity_unit_rate from the model
    unit_rate = float(quotation.electricity_unit_rate or 11.00)
    subsidy = 78000.0
    investment_cost = float(quotation.final_amount or quotation.net_amount or 0)

    # Energy generation calculations
    units_generated_per_year = plant_capacity * 4 * 365  # kWh per year

    # CO2 Emission Reduction calculation
    # CO2 emission factor for Indian grid: 0.82 kg CO2/kWh = 0.00082 tons CO2/kWh
    co2_emission_factor = 0.00082  # tons CO2 per kWh
    co2_reduction_tons_per_year = units_generated_per_year * co2_emission_factor

    yearly_saving = units_generated_per_year * unit_rate
    after_subsidy_amount = investment_cost - subsidy
    payback_period = round(after_subsidy_amount / yearly_saving, 1) if yearly_saving > 0 else 0

    amount_words = amount_in_words(quotation.final_amount)

    try:
        net = float(quotation.net_amount or 0)
        disc = float(quotation.special_discount or 0)
        after_discount_amount = net - disc
    except:
        after_discount_amount = 0

    # BASIC COST PER WATT (FLOAT)
    basic_cost_per_watt = 0.0

    if quotation.plant_capacity_kw and quotation.plant_capacity_kw.capacity:
        plant_capacity_kw = float(quotation.plant_capacity_kw.capacity)
        total_watts = plant_capacity_kw * 1000

        if total_watts > 0:
            basic_cost_per_watt = round(
                after_discount_amount / total_watts, 2
            )

    # Get terms with yellow background flag - check raw database value
    terms_with_yellow = set()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM quotation_termsandcondition
                WHERE CAST(has_yellow_background AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
            """)
            terms_with_yellow = {row[0] for row in cursor.fetchall()}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not fetch terms with yellow background: {e}")

    # Format date for template - ensure it's available and formatted
    from django.utils import timezone

    # Get the date value
    date_value = quotation.date if quotation.date else (
        quotation.created_at if quotation.created_at else timezone.now())

    # Format the date as string - handle both datetime objects and strings
    try:
        if date_value:
            # Check if it's a datetime object (has strftime method)
            if hasattr(date_value, 'strftime') and callable(getattr(date_value, 'strftime', None)):
                formatted_date = date_value.strftime('%d/%m/%Y')
            elif isinstance(date_value, str):
                # If it's a string, try to extract date part or use as-is
                # If it looks like a date string, try to format it
                if len(date_value) >= 10:
                    # Try to extract YYYY-MM-DD format
                    date_part = date_value[:10] if len(date_value) >= 10 else date_value
                    # Reverse from YYYY-MM-DD to DD/MM/YYYY
                    try:
                        parts = date_part.split('-')
                        if len(parts) == 3:
                            formatted_date = f"{parts[2]}/{parts[1]}/{parts[0]}"
                        else:
                            formatted_date = date_value
                    except:
                        formatted_date = date_value
                else:
                    formatted_date = date_value
            else:
                # Convert to string as fallback
                formatted_date = str(date_value)
        else:
            formatted_date = timezone.now().strftime('%d/%m/%Y')
    except Exception as e:
        # Fallback to current date if anything fails
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error formatting date: {e}")
        formatted_date = timezone.now().strftime('%d/%m/%Y')

    context = {
        'quotation': quotation,
        'quotation_date': date_value,  # Pass date object for template
        'formatted_date': formatted_date,  # Pass pre-formatted date string
        'formatted_other_details': formatted_other_details,  # Add the formatted version
        'units_generated_per_year': units_generated_per_year,
        'yearly_saving': yearly_saving,
        'after_subsidy_amount': after_subsidy_amount,
        'payback_period': payback_period,
        'subsidy_amount': subsidy,
        'amount_words': amount_words,
        'unit_rate': unit_rate,
        'after_discount_amount': after_discount_amount,
        'basic_cost_per_watt': basic_cost_per_watt,
        'representatives': reps,
        'terms_with_yellow': terms_with_yellow,  # Set of term IDs with yellow background
        'co2_reduction_tons_per_year': round(co2_reduction_tons_per_year, 1),  # Rounded to 1 decimal
    }

    html = render_to_string('quotation/industrial_quotation.html', context)
    sanitized_html = sanitize_css_units(html, content_width_pts=525)

    result = BytesIO()
    pisa_status = pisa.CreatePDF(
        sanitized_html,
        dest=result,
        encoding='utf-8',
        link_callback=link_callback,
    )

    if pisa_status.err:
        return HttpResponse(
            "Error creating PDF.<hr><pre>%s</pre>" % sanitized_html[:2000],
            status=500
        )

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'filename="industrial_quotation_{quotation.pk}.pdf"'
    return response



# Helper functions (add these to views.py)
def calculate_yearly_saving(quotation):
    """Calculate yearly energy savings"""
    units_per_kw_per_day = Decimal('4.5')
    units_generated_per_year = quotation.plant_capacity_kw.capacity * units_per_kw_per_day * Decimal('365')

    if quotation.consumer_type == 'Industrial':
        unit_rate = Decimal('8.50')
    elif quotation.consumer_type == 'Commercial':
        unit_rate = Decimal('7.50')
    else:
        unit_rate = Decimal('6.50')

    return units_generated_per_year * unit_rate


def calculate_payback_period(quotation):
    """Calculate payback period in years"""
    yearly_saving = calculate_yearly_saving(quotation)
    if yearly_saving > 0:
        payback = quotation.final_amount / yearly_saving
        return round(payback, 1)
    return Decimal('0.0')


# NEW: API to add plant capacity
@require_POST
def add_plant_capacity_api(request):
    capacity = request.POST.get('capacity', '').strip()
    if not capacity:
        return JsonResponse({'success': False, 'error': 'Capacity required'}, status=400)

    try:
        capacity_decimal = Decimal(capacity)
        # Check if capacity already exists
        existing = PlantCapacity.objects.filter(capacity=capacity_decimal).first()
        if existing:
            return JsonResponse({
                'success': True,
                'id': existing.id,
                'capacity': str(existing.capacity),
                'message': 'Capacity already exists'
            })

        obj = PlantCapacity.objects.create(capacity=capacity_decimal)
        return JsonResponse({
            'success': True,
            'id': obj.id,
            'capacity': str(obj.capacity)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # DON'T use csrf_exempt in production; keep CSRF token in JS

@require_POST
def add_representative_api(request):
    # expects POST fields: name, contact
    name = request.POST.get('name', '').strip()
    contact = request.POST.get('contact', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Name required'}, status=400)

    # create (allow duplicates to be handled as you prefer)
    rep, created = Representative.objects.get_or_create(name=name, contact=contact)
    return JsonResponse({
        'success': True,
        'id': rep.id,
        'name': rep.name,
        'contact': rep.contact
    })



# def quotation_pdf(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#     current_date = timezone.now().strftime('%d-%m-%Y')
#
#     html = render_to_string('quotation/quotation_template.html', {
#         'quotation': quotation,
#         'current_date': current_date,
#     })
#
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="quotation_{quotation.quotation_no}.pdf"'
#     pisa.CreatePDF(html, dest=response)
#     return response
#
# # views.py (xhtml2pdf + sanitizer fallback)
# import re
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from django.shortcuts import get_object_or_404
# from io import BytesIO
# from xhtml2pdf import pisa
# from .models import Quotation
#
# # helper: convert percent values in HTML to approximate points (so they are numeric)
# def sanitize_css_units(html, content_width_pts=520):
#     """
#     Replace occurrences like 'width: 58%;' or '58%' inside style attributes
#     with approximate point values (e.g., 'width: 300pt;') to avoid xhtml2pdf/ReportLab errors.
#     content_width_pts: available width in points (approx A4 minus margins).
#     """
#     # replace occurrences like 'NN%' with 'MMpt' where MM = NN% of content_width_pts
#     def pct_to_pt(match):
#         num = float(match.group(1))
#         pts = int(round(content_width_pts * (num / 100.0)))
#         return f'{pts}pt'
#
#     html = re.sub(r'(\d+(?:\.\d+)?)\s*%', pct_to_pt, html)
#
#     # convert px to pt (1px ~ 0.75pt). Replace 'NNpx' -> 'MMpt'
#     def px_to_pt(match):
#         px = float(match.group(1))
#         pts = int(round(px * 0.75))
#         return f'{pts}pt'
#
#     html = re.sub(r'(\d+(?:\.\d+)?)\s*px', px_to_pt, html)
#
#     # Optionally remove percentage-only width attributes like width="58%"
#     html = re.sub(r'width=["\']\s*(\d+(?:\.\d+)?)\s*%["\']', lambda m: f'width="{int(round(content_width_pts*(float(m.group(1))/100)))}pt"', html)
#
#     return html
#
# def quotation_pdf(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     def to_float(value):
#         try:
#             return float(value)
#         except (TypeError, ValueError):
#             return 0.0
#
#     # Normalization (safe)
#     fields = ["special_discount", "after_discount_amount", "gst_5_amount", "gst_18_amount", "net_amount",
#               "plant_capacity_kw", "inv_capacity_kw", "panel_capacity_watt", "yearly_saving",
#               "subsidy_amount", "after_subsidy_amount", "payback_years", "units_generated_per_year", "electricity_unit_cost"]
#     for f in fields:
#         if hasattr(quotation, f):
#             setattr(quotation, f, to_float(getattr(quotation, f)))
#
#     if hasattr(quotation, "items"):
#         for item in quotation.items.all():
#             if hasattr(item, "quantity"):
#                 item.quantity = to_float(getattr(item, "quantity"))
#             if hasattr(item, "line_total"):
#                 item.line_total = to_float(getattr(item, "line_total"))
#
#     html = render_to_string('quotation/quotation_template.html', {'quotation': quotation})
#
#     # Sanitize units so ReportLab won't be handed strings like '58%' or '20px'
#     # Choose content width in points: A4 width = 595.27pt; subtract margins (approx 35pt each side) -> ~525pt
#     sanitized_html = sanitize_css_units(html, content_width_pts=525)
#
#     # Create PDF with xhtml2pdf
#     result = BytesIO()
#     pisa_status = pisa.CreatePDF(sanitized_html, dest=result, encoding='utf-8')
#
#     if pisa_status.err:
#         # Return HTML for debugging (show sanitized HTML) - remove in production
#         return HttpResponse("Error creating PDF with xhtml2pdf. Debug sanitized HTML below:<hr><pre>%s</pre>" % (sanitized_html[:2000]), status=500)
#
#     response = HttpResponse(result.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'filename="quotation_{quotation.pk}.pdf"'
#     return response


import os
import re
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from xhtml2pdf import pisa
from .models import Quotation


# ✅ Convert CSS % and px to pt to avoid xhtml2pdf rendering errors
def sanitize_css_units(html, content_width_pts=520):
    """
    Replace % and px values in style attributes with point (pt) values
    so xhtml2pdf / ReportLab can render them safely.
    """
    def pct_to_pt(match):
        num = float(match.group(1))
        pts = int(round(content_width_pts * (num / 100.0)))
        return f'{pts}pt'

    def px_to_pt(match):
        px = float(match.group(1))
        pts = int(round(px * 0.75))  # 1px ≈ 0.75pt
        return f'{pts}pt'

    html = re.sub(r'(\d+(?:\.\d+)?)\s*%', pct_to_pt, html)
    html = re.sub(r'(\d+(?:\.\d+)?)\s*px', px_to_pt, html)
    html = re.sub(
        r'width=["\']\s*(\d+(?:\.\d+)?)\s*%["\']',
        lambda m: f'width="{int(round(content_width_pts*(float(m.group(1))/100)))}pt"',
        html
    )
    return html

def link_callback(uri, rel):
    """
    Convert HTML URIs (e.g. /static/img/foo.png) to absolute system paths
    so xhtml2pdf can access them both in dev and prod.
    """
    # 1. Fully-qualified URL? Return directly
    if uri.startswith('http://') or uri.startswith('https://'):
        return uri

    # 2. Handle media files
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
        if os.path.isfile(path):
            return path

    # 3. Handle static files from STATICFILES_DIRS and STATIC_ROOT
    if uri.startswith(settings.STATIC_URL):
        static_path = uri.replace(settings.STATIC_URL, '')

        # First look in each STATICFILES_DIR
        for static_dir in getattr(settings, 'STATICFILES_DIRS', []):
            path = os.path.join(static_dir, static_path)
            if os.path.isfile(path):
                return path

        # Then look in STATIC_ROOT
        path = os.path.join(settings.STATIC_ROOT, static_path)
        if os.path.isfile(path):
            return path

    # 4. Otherwise, let xhtml2pdf try to handle it
    return uri

#
# # ✅ Main PDF generator view
# def quotation_pdf(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     # render HTML template
#     html = render_to_string('quotation/quotation_template.html', {'quotation': quotation})
#
#     # sanitize CSS for xhtml2pdf
#     sanitized_html = sanitize_css_units(html, content_width_pts=525)
#
#     # generate PDF
#     result = BytesIO()
#     pisa_status = pisa.CreatePDF(
#         sanitized_html,
#         dest=result,
#         encoding='utf-8',
#         link_callback=link_callback,  # important for images
#     )
#
#     if pisa_status.err:
#         return HttpResponse(
#             "Error creating PDF.<hr><pre>%s</pre>" % sanitized_html[:2000],
#             status=500
#         )
#
#     response = HttpResponse(result.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'filename="quotation_{quotation.pk}.pdf"'
#     return response
#
from num2words import num2words
#
# def amount_in_words(amount):
#     """
#     Convert a numeric amount (e.g. 665.87) into:
#       "Six Hundred Sixty-Five Rupees And Eighty-Seven Paisa Only"
#     Removes internal 'and' inserted by num2words (but preserves the 'And' between Rupees and Paisa).
#     """
#     try:
#         # safe float conversion
#         amt = float(amount or 0)
#     except (TypeError, ValueError):
#         return ""
#
#     # split rupees and paise reliably with rounding
#     rupees = int(amt)
#     paise = int(round((amt - rupees) * 100))
#
#     # if rounding paise gives 100, carry to rupees
#     if paise == 100:
#         rupees += 1
#         paise = 0
#
#     # get words from num2words (english india)
#     rupees_words = num2words(rupees, lang='en_IN')
#     # remove internal ' and ' produced by num2words (so "one hundred and five" -> "one hundred five")
#     rupees_words = rupees_words.replace(" and ", " ")
#     # title case and cleanup extra spaces
#     rupees_words = " ".join(rupees_words.split()).title()
#
#     if paise > 0:
#         paise_words = num2words(paise, lang='en_IN')
#         paise_words = paise_words.replace(" and ", " ")
#         paise_words = " ".join(paise_words.split()).title()
#         return f"{rupees_words} Rupees And {paise_words} Paisa Only"
#     else:
#         return f"{rupees_words} Rupees Only"



from num2words import num2words
import re

def clean_num2words_text(s: str) -> str:
    """
    Clean num2words output:
      - remove commas and extra punctuation except hyphen
      - remove internal ' and ' between number words
      - collapse multiple spaces
      - title case
    """
    if not s:
        return ""
    # remove commas and other punctuation except hyphen and spaces (keep hyphen for 21-99 style)
    s = re.sub(r'[\,\u2019\']', '', s)     # remove commas and apostrophes
    # remove " and " inserted inside number words
    s = s.replace(" and ", " ")
    # collapse whitespace
    s = " ".join(s.split())
    # title-case (preserve existing hyphens correctly)
    # .title() will also capitalize parts after hyphen (desired)
    return s.title()


def amount_in_words(amount):
    """
    Convert numeric amount (e.g. 665.87) to:
      "Six Hundred Sixty-Five Rupees And Eighty-Seven Paisa Only"
    Ensures there are NO commas in result.
    """
    try:
        amt = float(amount or 0)
    except (TypeError, ValueError):
        return ""

    # split rupees and paise with rounding
    rupees = int(amt)
    paise = int(round((amt - rupees) * 100))

    # handle paise rounding carry
    if paise == 100:
        rupees += 1
        paise = 0

    # get words
    rupees_words = num2words(rupees, lang='en_IN')
    rupees_words = clean_num2words_text(rupees_words)

    if paise > 0:
        paise_words = num2words(paise, lang='en_IN')
        paise_words = clean_num2words_text(paise_words)
        return f"{rupees_words} Rupees And {paise_words} Paisa Only"
    else:
        return f"{rupees_words} Rupees Only"


#
# def quotation_pdf(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     # --- Perform Calculations ---
#     plant_capacity = float(quotation.plant_capacity_kw or 0)
#     # unit_rate = float(quotation.electricity_unit_cost or 11)  # default ₹11/unit if empty
#     unit_rate = 11  # default ₹11/unit if empty
#     subsidy = 78000.0
#     investment_cost = float(quotation.final_amount or quotation.net_amount or 0)
#
#     # 1️⃣ Units Generated Per Year
#     units_generated_per_year = plant_capacity * 4 * 365
#
#     # 2️⃣ Yearly Saving
#     yearly_saving = units_generated_per_year * unit_rate
#
#     # 3️⃣ After Subsidy Amount
#     after_subsidy_amount = investment_cost - subsidy
#
#     # 4️⃣ Payback Period (1 decimal)
#     payback_period = round(after_subsidy_amount / yearly_saving, 1) if yearly_saving > 0 else 0
#
#     # --- Pass calculated values to template ---
#     context = {
#         'quotation': quotation,
#         'units_generated_per_year': f"{units_generated_per_year:,.2f}",
#         'yearly_saving': f"{yearly_saving:,.2f}",
#         'after_subsidy_amount': f"{after_subsidy_amount:,.2f}",
#         'payback_period': payback_period,
#         'subsidy_amount': f"{subsidy:,.2f}",
#     }
#
#     # render template
#     html = render_to_string('quotation/quotation_template.html', context)
#
#     sanitized_html = sanitize_css_units(html, content_width_pts=525)
#
#     result = BytesIO()
#     pisa_status = pisa.CreatePDF(
#         sanitized_html,
#         dest=result,
#         encoding='utf-8',
#         link_callback=link_callback,
#     )
#
#     if pisa_status.err:
#         return HttpResponse(
#             "Error creating PDF.<hr><pre>%s</pre>" % sanitized_html[:2000],
#             status=500
#         )
#
#     response = HttpResponse(result.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'filename="quotation_{quotation.pk}.pdf"'
#     return response
#
#
# def edit_quotation(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = SolarPanelCompany.objects.all()
#     inverter_companies = InverterCompany.objects.all()
#
#     if request.method == 'POST':
#         form = QuotationForm(request.POST, instance=quotation)
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#
#             # --- Save M2M ---
#             form.save_m2m()
#
#             # --- PANEL COMPANIES ---
#             panel_ids = request.POST.getlist('panel_companies')
#             quotation.panel_companies.set(panel_ids)
#             quotation.panel_company_names = " / ".join(
#                 SolarPanelCompany.objects.filter(id__in=panel_ids).values_list('name', flat=True)
#             )
#
#             # --- INVERTER COMPANIES ---
#             inverter_ids = request.POST.getlist('inverter_companies')
#             quotation.inverter_companies.set(inverter_ids)
#
#             inverter_names = []
#             warranty_values = []
#
#             for inv_id in inverter_ids:
#                 name = InverterCompany.objects.get(id=inv_id).name
#                 inverter_names.append(name)
#
#                 wt = request.POST.get(f'inverter_warranty_{inv_id}', '').strip()
#                 if wt:
#                     warranty_values.append(wt)
#
#             quotation.inverter_company_names = " / ".join(inverter_names)
#             quotation.inverter_warranty = " / ".join(warranty_values)
#
#             # --- OTHER ITEMS ---
#             static_items = form.cleaned_data.get("other_items", [])
#             dynamic_items = request.POST.getlist("dynamic_other_items[]")
#
#             combined = list(static_items.values_list('name', flat=True)) + dynamic_items
#             quotation.other_details = " / ".join(dict.fromkeys([x.strip() for x in combined if x.strip()]))
#
#             # --- PRICING LOGIC ---
#             pricing_mode = form.cleaned_data['pricing_mode']
#             net = form.cleaned_data['net_amount_input']
#             final = form.cleaned_data['final_amount_input']
#
#             if pricing_mode == 'net' and net:
#                 quotation.net_amount = net
#                 quotation.calculate_from_net()
#             elif pricing_mode == 'final' and final:
#                 quotation.final_amount = final
#                 quotation.calculate_from_final()
#
#             quotation.save()
#             return redirect('quotation:quotation_pdf', pk=quotation.pk)
#
#     else:
#         form = QuotationForm(instance=quotation)
#
#     return render(request, 'quotation/edit_quotation.html', {
#         'form': form,
#         'quotation': quotation,
#         'panel_companies': panel_companies,
#         'inverter_companies': inverter_companies,
#     })


# def edit_quotation(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#
#     if request.method == "POST":
#         form = QuotationForm(request.POST, instance=quotation)
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#             form.save_m2m()
#
#             # ---------------------------------------------
#             # PANEL COMPANIES
#             # ---------------------------------------------
#             panel_ids = request.POST.getlist("panel_companies")
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # ---------------------------------------------
#             # INVERTER COMPANIES + WARRANTIES
#             # ---------------------------------------------
#             inverter_ids = request.POST.getlist("inverter_companies")
#             quotation.inverter_companies.set(inverter_ids)
#
#             selected_names = []
#             selected_warranties = []
#
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 selected_names.append(inv.name)
#
#                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                 selected_warranties.append(wt)
#
#             quotation.inverter_company_names = " / ".join(selected_names)
#             quotation.inverter_warranty = " / ".join(selected_warranties)
#
#             # ---------------------------------------------
#             # OTHER ITEMS (static + dynamic)
#             # ---------------------------------------------
#             static_selected = list(form.cleaned_data.get("other_items").values_list("name", flat=True))
#             dynamic_new = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#
#             all_items = []
#             for x in static_selected + dynamic_new:
#                 if x not in all_items:
#                     all_items.append(x)
#
#             quotation.other_details = " / ".join(all_items)
#
#             # ---------------------------------------------
#             # PRICING LOGIC
#             # ---------------------------------------------
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_value = form.cleaned_data.get("net_amount_input")
#             final_value = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_value:
#                 quotation.net_amount = net_value
#                 quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_value:
#                 quotation.final_amount = final_value
#                 quotation.calculate_from_final()
#
#             quotation.save()
#             return redirect("quotation:quotation_pdf", pk=quotation.pk)
#
#     else:
#         form = QuotationForm(instance=quotation)
#
#     # ------------------------------------------------------------
#     # PREPARE DATA FOR TEMPLATE (avoid ANY Python calls in HTML)
#     # ------------------------------------------------------------
#
#     # inverter warranties
#     stored_names = quotation.inverter_company_names.split(" / ") if quotation.inverter_company_names else []
#     stored_warranties = quotation.inverter_warranty.split(" / ") if quotation.inverter_warranty else []
#
#     warranty_map = {}
#     for i, name in enumerate(stored_names):
#         warranty_map[name] = stored_warranties[i] if i < len(stored_warranties) else ""
#
#     # attach warranty to each company for template rendering
#     for comp in inverter_companies:
#         comp.warranty = warranty_map.get(comp.name, "")
#
#     # dynamic other items
#     other_dynamic_list = quotation.other_details.split(" / ") if quotation.other_details else []
#
#     # static item names for template comparison
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     return render(request, "quotation/edit_quotation.html", {
#         "form": form,
#         "quotation": quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#     })

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Quotation, SolarPanelCompany, InverterCompany, OtherItem
from .forms import QuotationForm

# def edit_quotation(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#
#     if request.method == 'POST':
#         form = QuotationForm(request.POST, instance=quotation)
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#             # save basic fields
#             form.save_m2m()
#
#             # -----------------------------
#             # PANEL COMPANIES
#             # -----------------------------
#             panel_ids = request.POST.getlist('panel_companies')
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list('name', flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # -----------------------------
#             # INVERTER COMPANIES + warranties
#             # -----------------------------
#             inverter_ids = request.POST.getlist('inverter_companies')
#             quotation.inverter_companies.set(inverter_ids)
#
#             inverter_names = []
#             warranty_values = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inverter_names.append(inv.name)
#                 wt = request.POST.get(f'inverter_warranty_{inv_id}', '').strip()
#                 warranty_values.append(wt)
#
#             quotation.inverter_company_names = " / ".join(inverter_names)
#             quotation.inverter_warranty = " / ".join(warranty_values)
#
#             # -----------------------------
#             # OTHER ITEMS: static + dynamic
#             # -----------------------------
#             static_qs = form.cleaned_data.get('other_items') or []
#             static_names = list(static_qs.values_list('name', flat=True))
#             dynamic_items = [x.strip() for x in request.POST.getlist('dynamic_other_items[]') if x.strip()]
#
#             combined = []
#             for n in static_names + dynamic_items:
#                 if n and n not in combined:
#                     combined.append(n)
#             quotation.other_details = " / ".join(combined)
#
#             # -----------------------------
#             # PRICING logic
#             # -----------------------------
#             pricing_mode = form.cleaned_data.get('pricing_mode')
#             net_input = form.cleaned_data.get('net_amount_input')
#             final_input = form.cleaned_data.get('final_amount_input')
#
#             if pricing_mode == 'net' and net_input:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#             elif pricing_mode == 'final' and final_input:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             quotation.save()
#             return redirect('quotation:quotation_pdf', pk=quotation.pk)
#
#     else:
#         form = QuotationForm(instance=quotation)
#
#     # -----------------------------
#     # Prepare data for template (avoid method calls in template)
#     # -----------------------------
#     # Prepare inverter warranty mapping: name -> warranty
#     stored_names = quotation.inverter_company_names.split(" / ") if quotation.inverter_company_names else []
#     stored_wts = quotation.inverter_warranty.split(" / ") if quotation.inverter_warranty else []
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     # Attach warranty string to each inverter company instance for template use
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     # other dynamic items list
#     other_dynamic_list = [x.strip() for x in quotation.other_details.split(" / ")] if quotation.other_details else []
#
#     # static item names (for template dedupe check)
#     static_item_names = set(OtherItem.objects.values_list('name', flat=True))
#
#     context = {
#         'form': form,
#         'quotation': quotation,
#         'panel_companies': panel_companies,
#         'inverter_companies': inverter_companies,
#         'other_dynamic_list': other_dynamic_list,
#         'static_item_names': static_item_names,
#     }
#     return render(request, 'quotation/edit_quotation.html', context)

# def edit_quotation(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#
#     other_dynamic_list = []
#     if quotation.other_details:
#         other_dynamic_list = [x.strip() for x in quotation.other_details.split(" / ") if x.strip()]
#
#     static_item_names = set(OtherItem.objects.values_list('name', flat=True))
#
#     if request.method == 'POST':
#         form = QuotationForm(request.POST, instance=quotation)
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist('panel_companies')
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list('name', flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER + WARRANTY
#             inverter_ids = request.POST.getlist('inverter_companies')
#             quotation.inverter_companies.set(inverter_ids)
#
#             inverter_names = []
#             warranty_values = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inverter_names.append(inv.name)
#                 wt = request.POST.get(f'inverter_warranty_{inv_id}', '').strip()
#                 warranty_values.append(wt)
#
#             quotation.inverter_company_names = " / ".join(inverter_names)
#             quotation.inverter_warranty = " / ".join(warranty_values)
#
#             # OTHER ITEMS
#             static_items = form.cleaned_data.get('other_items') or []
#             static_names_list = list(static_items.values_list('name', flat=True))
#             dynamic_items = [x.strip() for x in request.POST.getlist('dynamic_other_items[]') if x.strip()]
#
#             combined = []
#             for n in static_names_list + dynamic_items:
#                 if n and n not in combined:
#                     combined.append(n)
#
#             quotation.other_details = " / ".join(combined)
#
#             # PRICING
#             mode = form.cleaned_data.get('pricing_mode')
#             net = form.cleaned_data.get('net_amount_input')
#             final = form.cleaned_data.get('final_amount_input')
#
#             if mode == 'net' and net:
#                 quotation.net_amount = net
#                 quotation.calculate_from_net()
#
#             elif mode == 'final' and final:
#                 quotation.final_amount = final
#                 quotation.calculate_from_final()
#
#             quotation.save()
#             return redirect('quotation:quotation_pdf', pk=quotation.pk)
#
#     else:
#         form = QuotationForm(instance=quotation)
#
#         # PREFILL TAX FIELDS
#         form.fields['gst_5_percent'].initial = quotation.gst_5_percent
#         form.fields['gst_18_percent'].initial = quotation.gst_18_percent
#         form.fields['special_discount'].initial = quotation.special_discount
#         form.fields['net_amount_input'].initial = quotation.net_amount
#         form.fields['final_amount_input'].initial = quotation.final_amount
#
#         # MAP static items
#         static_names_from_db = [i for i in other_dynamic_list if i in static_item_names]
#         checked_static_items = OtherItem.objects.filter(name__in=static_names_from_db)
#         form.fields['other_items'].initial = checked_static_items
#
#     # SET WARRANTY FOR INVERTER FIELD
#     stored_names = quotation.inverter_company_names.split(" / ") if quotation.inverter_company_names else []
#     stored_wts = quotation.inverter_warranty.split(" / ") if quotation.inverter_warranty else []
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     return render(request, 'quotation/edit_quotation.html', {
#         'form': form,
#         'quotation': quotation,
#         'panel_companies': panel_companies,
#         'inverter_companies': inverter_companies,
#         'other_dynamic_list': other_dynamic_list,
#         'static_item_names': static_item_names,
#     })
#
# # Keep your AJAX endpoints (unchanged)
# @require_POST
# def add_panel_company_api(request):
#     name = request.POST.get('name', '').strip()
#     if not name:
#         return JsonResponse({'success': False, 'error': 'Name required'}, status=400)
#     obj, created = SolarPanelCompany.objects.get_or_create(name=name)
#     return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name})
#
#
# @require_POST
# def add_inverter_company_api(request):
#     name = request.POST.get('name', '').strip()
#     if not name:
#         return JsonResponse({'success': False, 'error': 'Name required'}, status=400)
#     obj, created = InverterCompany.objects.get_or_create(name=name)
#     return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name})
#
#
# @require_POST
# def add_other_item_api(request):
#     name = request.POST.get('name', '').strip()
#     if not name:
#         return JsonResponse({'success': False, 'error': 'Name required'}, status=400)
#     obj, created = OtherItem.objects.get_or_create(name=name)
#     return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name, 'created': created})
#

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Quotation, SolarPanelCompany, InverterCompany, OtherItem
from .forms import QuotationForm
#
# def edit_quotation(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table (for dedupe / checked mapping)
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         form = QuotationForm(request.POST, instance=quotation)
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             quotation.inverter_companies.set(inverter_ids)
#
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inv_names.append(inv.name)
#                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                 inv_warranties.append(wt)
#
#             quotation.inverter_company_names = " / ".join(inv_names)
#             quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # inside edit_quotation POST handling, after handling inverter/panel etc.
#
#             # REPRESENTATIVES (save selected representative ids to M2M)
#             rep_ids = request.POST.getlist('representatives')
#             quotation.representatives.set(rep_ids)
#
#             # optional: store textual representation for PDF (ordered by PK)
#             rep_qs = Representative.objects.filter(id__in=rep_ids)
#             rep_texts = [f"{i + 1}. {r.name} - {r.contact}" for i, r in enumerate(rep_qs)]
#             quotation.representative_names = "\n".join(rep_texts)
#
#
#             # OTHER ITEMS (static from ModelMultipleChoice + dynamic inputs)
#             static_qs = form.cleaned_data.get("other_items") or []
#             static_names = list(static_qs.values_list("name", flat=True))
#             dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#
#             combined = []
#             for n in static_names + dynamic_inputs:
#                 if n and n not in combined:
#                     combined.append(n)
#
#             quotation.other_details = " / ".join(combined)
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             quotation.save()
#             return redirect("quotation:quotation_pdf", pk=quotation.pk)
#
#     else:
#         # GET - unbound form with instance
#         form = QuotationForm(instance=quotation)
#
#         # Prefill pricing & tax fields (so form.field.value will be present)
#         # Only set if the form actually has the field (it does per your QuotationForm)
#         try:
#             form.fields["gst_5_percent"].initial = quotation.gst_5_percent
#             form.fields["gst_18_percent"].initial = quotation.gst_18_percent
#         except Exception:
#             pass
#
#         try:
#             form.fields["special_discount"].initial = quotation.special_discount
#             form.fields["net_amount_input"].initial = quotation.net_amount
#             form.fields["final_amount_input"].initial = quotation.final_amount
#         except Exception:
#             pass
#
#         # Pre-check static other_items checkboxes that exist in DB
#         # pick those stored in other_details that match existing OtherItem rows
#         static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#         if static_names_to_check:
#             checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#             form.fields["other_items"].initial = checked_qs
#
#     # prepare warranty mapping to attach to company objects for template ease
#     stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "quotation": quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),  # <-- ADDED
#     }
#     return render(request, "quotation/edit_quotation.html", context)
#

# def edit_quotation(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#     terms_conditions = TermsAndCondition.objects.filter(is_active=True)  # ADD THIS
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table (for dedupe / checked mapping)
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         form = QuotationForm(request.POST, instance=quotation)
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#
#             # Handle system_na checkbox - clear capacities if NA is checked
#             system_na = form.cleaned_data.get('system_na', False)
#             if system_na:
#                 quotation.dc_capacity = None
#                 quotation.ac_capacity = None
#             else:
#                 # Ensure capacities are saved if not NA
#                 quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
#                 quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
#
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             quotation.inverter_companies.set(inverter_ids)
#
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inv_names.append(inv.name)
#                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                 inv_warranties.append(wt)
#
#             quotation.inverter_company_names = " / ".join(inv_names)
#             quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES
#             rep_ids = request.POST.getlist('representatives')
#             quotation.representatives.set(rep_ids)
#
#             # optional: store textual representation for PDF (ordered by PK)
#             rep_qs = Representative.objects.filter(id__in=rep_ids)
#             rep_texts = [f"{i + 1}. {r.name} - {r.contact}" for i, r in enumerate(rep_qs)]
#             quotation.representative_names = "\n".join(rep_texts)
#
#             # TERMS & CONDITIONS - ADD THIS SECTION
#             terms_ids = request.POST.getlist('terms_conditions')
#             quotation.terms_conditions.set(terms_ids)
#
#             # Store terms content for PDF (ordered by PK)
#             terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
#             terms_texts = []
#             for i, term in enumerate(terms_qs):
#                 terms_texts.append(f"{i + 1}. {term.content}")
#             quotation.terms_conditions_text = "\n".join(terms_texts)
#
#             # # OTHER ITEMS (static from ModelMultipleChoice + dynamic inputs)
#             # static_qs = form.cleaned_data.get("other_items") or []
#             # static_names = list(static_qs.values_list("name", flat=True))
#             # dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#             #
#             # combined = []
#             # for n in static_names + dynamic_inputs:
#             #     if n and n not in combined:
#             #         combined.append(n)
#             #
#             # quotation.other_details = " / ".join(combined)
#
#             # OTHER ITEMS (static from ModelMultipleChoice + dynamic inputs)
#             static_qs = form.cleaned_data.get("other_items")
#             static_names = []
#
#             # Check if static_qs is a QuerySet (has values_list method) or a list
#             if static_qs and hasattr(static_qs, 'values_list'):
#                 static_names = list(static_qs.values_list("name", flat=True))
#             elif static_qs:  # It's a regular list
#                 static_names = [item.name for item in static_qs if hasattr(item, 'name')]
#
#             dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#
#             combined = []
#             for n in static_names + dynamic_inputs:
#                 if n and n not in combined:
#                     combined.append(n)
#
#             quotation.other_details = " / ".join(combined)
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             quotation.save()
#             return redirect("quotation:quotation_pdf", pk=quotation.pk)
#
#     else:
#         # GET - unbound form with instance
#         form = QuotationForm(instance=quotation)
#
#         # Prefill pricing & tax fields
#         try:
#             form.fields["consumer_type"].initial = quotation.consumer_type
#             form.fields["consumer_no"].initial = quotation.consumer_no
#             form.fields["dc_capacity"].initial = quotation.dc_capacity
#             form.fields["ac_capacity"].initial = quotation.ac_capacity
#             form.fields["system_na"].initial = quotation.system_na
#             form.fields["gst_5_percent"].initial = quotation.gst_5_percent
#             form.fields["gst_18_percent"].initial = quotation.gst_18_percent
#         except Exception:
#             pass
#
#         try:
#             form.fields["special_discount"].initial = quotation.special_discount
#             form.fields["net_amount_input"].initial = quotation.net_amount
#             form.fields["final_amount_input"].initial = quotation.final_amount
#         except Exception:
#             pass
#
#         # Pre-check static other_items checkboxes
#         static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#         if static_names_to_check:
#             checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#             form.fields["other_items"].initial = checked_qs
#
#     # prepare warranty mapping
#     stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "quotation": quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,  # ADD THIS
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/edit_quotation.html", context)

# def edit_quotation(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#     terms_conditions = get_active_terms_conditions()
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table (for dedupe / checked mapping)
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         form = QuotationForm(request.POST, instance=quotation)
#
#         if form.is_valid():
#             quotation = form.save(commit=False)
#
#             # Handle system_na checkbox - clear capacities if NA is checked
#             system_na = form.cleaned_data.get('system_na', False)
#             if system_na:
#                 quotation.dc_capacity = None
#                 quotation.ac_capacity = None
#             else:
#                 # Ensure capacities are saved if not NA
#                 quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
#                 quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
#
#             # Handle Other Details NA checkbox
#             na_other_checked = request.POST.get("na_other_checkbox") == "on"
#             if na_other_checked:
#                 # Clear other details if NA is checked
#                 quotation.other_details = ""
#             else:
#                 # Process other items only if NA is not checked
#                 static_qs = form.cleaned_data.get("other_items") or []
#                 static_names = []
#
#                 # Handle both QuerySet and list cases
#                 for item in static_qs:
#                     if hasattr(item, 'name'):
#                         static_names.append(item.name)
#
#                 dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#
#                 combined = []
#                 for n in static_names + dynamic_inputs:
#                     if n and n not in combined:
#                         combined.append(n)
#
#                 quotation.other_details = " / ".join(combined)
#
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             quotation.inverter_companies.set(inverter_ids)
#
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inv_names.append(inv.name)
#                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                 inv_warranties.append(wt)
#
#             quotation.inverter_company_names = " / ".join(inv_names)
#             quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES
#             rep_ids = request.POST.getlist('representatives')
#             quotation.representatives.set(rep_ids)
#
#             # optional: store textual representation for PDF (ordered by PK)
#             rep_qs = Representative.objects.filter(id__in=rep_ids)
#             rep_texts = [f"{i + 1}. {r.name} - {r.contact}" for i, r in enumerate(rep_qs)]
#             quotation.representative_names = "\n".join(rep_texts)
#
#             # TERMS & CONDITIONS
#             terms_ids = request.POST.getlist('terms_conditions')
#             quotation.terms_conditions.set(terms_ids)
#
#             # Store terms content for PDF (ordered by PK)
#             terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
#             terms_texts = []
#             for i, term in enumerate(terms_qs):
#                 terms_texts.append(f"{i + 1}. {term.content}")
#             quotation.terms_conditions_text = "\n".join(terms_texts)
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             quotation.save()
#             return redirect("quotation:quotation_pdf", pk=quotation.pk)
#
#     else:
#         # GET - unbound form with instance
#         form = QuotationForm(instance=quotation)
#
#         # Prefill pricing & tax fields
#         try:
#             form.fields["consumer_type"].initial = quotation.consumer_type
#             form.fields["consumer_no"].initial = quotation.consumer_no
#             form.fields["dc_capacity"].initial = quotation.dc_capacity
#             form.fields["ac_capacity"].initial = quotation.ac_capacity
#             form.fields["system_na"].initial = quotation.system_na
#             form.fields["gst_5_percent"].initial = quotation.gst_5_percent
#             form.fields["gst_18_percent"].initial = quotation.gst_18_percent
#         except Exception:
#             pass
#
#         try:
#             form.fields["special_discount"].initial = quotation.special_discount
#             form.fields["net_amount_input"].initial = quotation.net_amount
#             form.fields["final_amount_input"].initial = quotation.final_amount
#         except Exception:
#             pass
#
#         # Pre-check static other_items checkboxes only if other_details exists
#         if quotation.other_details:
#             static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#             if static_names_to_check:
#                 checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#                 form.fields["other_items"].initial = checked_qs
#
#     # prepare warranty mapping
#     stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "quotation": quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/edit_quotation.html", context)


# def edit_quotation(request, pk):
#     """
#     Edit an existing quotation (not create a revision).
#     Similar to revise_quotation but updates the same quotation instead of creating a new one.
#     """
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#     terms_conditions = get_active_terms_conditions()
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         # Get existing term IDs from the quotation BEFORE creating the form
#         # This ensures we can include them in the queryset
#         existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#
#         # Get submitted term IDs from POST data
#         submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
#
#         # IMPORTANT: When editing, we need to include ALL existing terms (even if inactive)
#         # because Django validates them when instance is provided
#         # Get active term IDs using raw SQL
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM quotation_termsandcondition
#                     WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
#                 """)
#                 active_term_ids = [row[0] for row in cursor.fetchall()]
#
#             # Combine: active + existing + submitted
#             # CRITICAL: existing_term_ids MUST be included to pass validation
#             all_term_ids = list(set(active_term_ids + existing_term_ids + submitted_term_ids))
#
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not get active term IDs: {e}")
#             # Fallback: use existing + submitted terms
#             all_term_ids = list(set(existing_term_ids + submitted_term_ids))
#
#         # For editing, we MUST include ALL existing terms to pass validation
#         # Get ALL term IDs from database to ensure any existing term can be validated
#         # This is necessary because existing terms might not be active anymore
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT id FROM quotation_termsandcondition")
#                 all_db_term_ids = [int(row[0]) for row in cursor.fetchall()]  # Ensure integers
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not get all term IDs: {e}")
#             all_db_term_ids = []
#
#         # Ensure existing_term_ids are also integers
#         existing_term_ids = [int(id) for id in existing_term_ids if id is not None]
#
#         # Combine: all database terms (to validate existing) + submitted terms
#         # CRITICAL: Make sure ALL existing terms are included
#         final_term_ids = list(set(all_db_term_ids + existing_term_ids + submitted_term_ids))
#
#         # Debug: Verify all existing terms are in final list
#         import logging
#         logger = logging.getLogger(__name__)
#         missing_terms = set(existing_term_ids) - set(final_term_ids)
#         if missing_terms:
#             logger.error(f"CRITICAL: Existing terms {missing_terms} are missing from final_term_ids!")
#             # Force include them
#             final_term_ids = list(set(final_term_ids + list(missing_terms)))
#
#         # Debug logging
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.info(f"Edit quotation - Existing term IDs: {existing_term_ids}")
#         logger.info(f"Edit quotation - Submitted term IDs: {submitted_term_ids}")
#         logger.info(f"Edit quotation - All DB term IDs: {all_db_term_ids}")
#         logger.info(f"Edit quotation - Final term IDs: {final_term_ids}")
#
#         # Create queryset with ALL terms from database
#         # This ensures existing terms (even if inactive) will validate
#         if final_term_ids:
#             terms_queryset = TermsAndCondition.objects.filter(id__in=final_term_ids)
#         else:
#             terms_queryset = TermsAndCondition.objects.none()
#
#         # Create form with instance AND pass terms_conditions_queryset parameter
#         # The form's __init__ will set the queryset on base_fields BEFORE super().__init__()
#         # This ensures Django uses the correct queryset during validation
#         form = QuotationForm(request.POST, instance=quotation, terms_conditions_queryset=terms_queryset)
#
#         # Double-check queryset is set correctly
#         form.fields['terms_conditions'].queryset = terms_queryset
#
#         # Validate the form
#         is_valid = form.is_valid()
#
#         # CRITICAL: Clear terms_conditions validation errors if they're about invalid choices
#         # We know all terms exist because we got them from the database
#         if not is_valid and 'terms_conditions' in form.errors:
#             terms_errors = form.errors.get('terms_conditions', [])
#             # Check if any error is about invalid choices
#             has_invalid_choice_error = any('not one of the available choices' in str(e) for e in terms_errors)
#             if has_invalid_choice_error:
#                 # Clear the error - we verified these terms exist in the database
#                 form._errors.pop('terms_conditions', None)
#                 # Initialize cleaned_data if it doesn't exist
#                 if not hasattr(form, 'cleaned_data'):
#                     form.cleaned_data = {}
#                 # Manually set cleaned_data for terms_conditions to bypass validation
#                 submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
#                 if submitted_term_ids:
#                     form.cleaned_data['terms_conditions'] = list(
#                         TermsAndCondition.objects.filter(id__in=submitted_term_ids))
#                 # Re-check if form is now valid (no errors left)
#                 remaining_errors = {k: v for k, v in form.errors.items() if k != 'terms_conditions'}
#                 if len(remaining_errors) == 0:
#                     is_valid = True
#
#         if is_valid:
#             quotation = form.save(commit=False)
#
#             # Handle system_na checkbox - clear capacities if NA is checked
#             system_na = form.cleaned_data.get('system_na', False)
#             if system_na:
#                 quotation.dc_capacity = None
#                 quotation.ac_capacity = None
#             else:
#                 # Ensure capacities are saved if not NA
#                 quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
#                 quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
#
#             # Set system_na to False - we'll update it via raw SQL immediately after save
#             quotation.system_na = False
#
#             # Handle Other Details NA checkbox
#             na_other_checked = request.POST.get("na_other_checkbox") == "on"
#             if na_other_checked:
#                 quotation.other_details = ""
#             else:
#                 # Process other items only if NA is not checked
#                 static_qs = form.cleaned_data.get("other_items") or []
#                 static_names = []
#                 for item in static_qs:
#                     if hasattr(item, 'name'):
#                         static_names.append(item.name)
#                 dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#                 combined = []
#                 for n in static_names + dynamic_inputs:
#                     if n and n not in combined:
#                         combined.append(n)
#                 quotation.other_details = " / ".join(combined)
#
#             quotation.save()
#
#             # Update system_na using raw SQL to handle bit varying type
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s::bit varying
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', quotation.id])
#
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             quotation.inverter_companies.set(inverter_ids)
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 inv = InverterCompany.objects.get(id=inv_id)
#                 inv_names.append(inv.name)
#                 wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                 inv_warranties.append(wt)
#             quotation.inverter_company_names = " / ".join(inv_names)
#             quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES - Use selection order if provided
#             rep_ids = request.POST.getlist('representatives')
#             rep_order_str = request.POST.get('representatives_order', '').strip()
#
#             # If order is provided, use it; otherwise use default order
#             if rep_order_str:
#                 # Parse the order from comma-separated string
#                 ordered_rep_ids = [rid.strip() for rid in rep_order_str.split(',') if rid.strip() in rep_ids]
#                 # Add any remaining reps that weren't in the order (shouldn't happen, but safety)
#                 for rid in rep_ids:
#                     if rid not in ordered_rep_ids:
#                         ordered_rep_ids.append(rid)
#                 rep_ids = ordered_rep_ids
#
#             quotation.representatives.set(rep_ids)
#
#             # Store textual representation for PDF in selection order
#             # Create a mapping of ID to Representative for quick lookup
#             rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
#             rep_texts = []
#             for i, rep_id in enumerate(rep_ids):
#                 if rep_id in rep_dict:
#                     r = rep_dict[rep_id]
#                     contact_str = f" - {r.contact}" if r.contact else ""
#                     rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
#             quotation.representative_names = "\n".join(rep_texts)
#
#             # TERMS & CONDITIONS
#             terms_ids = request.POST.getlist('terms_conditions')
#             if terms_ids:
#                 quotation.terms_conditions.set(terms_ids)
#                 terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
#                 terms_texts = []
#                 for i, term in enumerate(terms_qs, 1):
#                     terms_texts.append(f"{i}. {term.content}")
#                 quotation.terms_conditions_text = "\n".join(terms_texts)
#             else:
#                 # Clear terms if none selected
#                 quotation.terms_conditions.clear()
#                 quotation.terms_conditions_text = ""
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             quotation.save()
#
#             # Update system_na again after final save
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s::bit varying
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', quotation.id])
#
#             return redirect("quotation:quotation_pdf", pk=quotation.pk)
#     else:
#         # GET - create form pre-filled with existing quotation data
#         form = QuotationForm(instance=quotation)
#
#         # Set terms_conditions queryset to include:
#         # 1. All active terms (for new selections)
#         # 2. Existing terms from this quotation (so validation passes)
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM quotation_termsandcondition
#                     WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
#                 """)
#                 active_term_ids = [row[0] for row in cursor.fetchall()]
#
#             # Get existing term IDs from the quotation
#             existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#
#             # Combine both lists (active + existing) to ensure validation passes
#             all_term_ids = list(set(active_term_ids + existing_term_ids))
#
#             if all_term_ids:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
#             else:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Could not set terms_conditions queryset: {e}")
#             # Fallback: include at least the existing terms
#             try:
#                 existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#                 if existing_term_ids:
#                     form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(
#                         id__in=existing_term_ids)
#                 else:
#                     form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#             except:
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         # Pre-check static other_items checkboxes
#         if quotation.other_details:
#             static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#             if static_names_to_check:
#                 checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#                 form.fields["other_items"].initial = checked_qs
#
#     # Prepare warranty mapping
#     stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#     stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#
#     name_to_wt = {}
#     for i, name in enumerate(stored_names):
#         name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#
#     for comp in inverter_companies:
#         comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "quotation": quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/edit_quotation.html", context)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db import connection
from .models import Quotation, SolarPanelCompany, InverterCompany, TermsAndCondition, OtherItem, Representative, \
    PlantCapacity
from .forms import QuotationForm
import logging

logger = logging.getLogger(__name__)
#
#
# def edit_quotation(request, pk):
#     """
#     Edit an existing quotation (not create a revision).
#     Similar to revise_quotation but updates the same quotation instead of creating a new one.
#     """
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#
#     # Get active terms and conditions using raw SQL to handle bit varying
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT id FROM quotation_termsandcondition
#                 WHERE is_active = '1'::bit varying OR is_active = true
#             """)
#             active_term_ids = [row[0] for row in cursor.fetchall()]
#         terms_conditions = TermsAndCondition.objects.filter(id__in=active_term_ids).order_by('id')
#     except Exception as e:
#         logger.error(f"Error getting active terms: {e}")
#         # Fallback: try boolean filter
#         try:
#             terms_conditions = TermsAndCondition.objects.filter(is_active=True).order_by('id')
#             active_term_ids = list(terms_conditions.values_list('id', flat=True))
#         except:
#             terms_conditions = TermsAndCondition.objects.all().order_by('id')
#             active_term_ids = list(terms_conditions.values_list('id', flat=True))
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         # Check if this is an AJAX save request
#         is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('save_only')
#
#         # Get existing term IDs from the quotation
#         existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#
#         # Get submitted term IDs from POST data
#         submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
#
#         # Combine: active + existing + submitted
#         all_term_ids = list(set(active_term_ids + existing_term_ids + submitted_term_ids))
#
#         # Create queryset
#         if all_term_ids:
#             terms_queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
#         else:
#             terms_queryset = TermsAndCondition.objects.none()
#
#         # Create form with instance
#         form = QuotationForm(request.POST, instance=quotation)
#         form.fields['terms_conditions'].queryset = terms_queryset
#
#         # Validate the form
#         if form.is_valid():
#             quotation = form.save(commit=False)
#
#             # Handle system_na checkbox
#             system_na = form.cleaned_data.get('system_na', False)
#             if system_na:
#                 quotation.dc_capacity = None
#                 quotation.ac_capacity = None
#             else:
#                 quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
#                 quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
#
#             quotation.system_na = False
#
#             # Handle Other Details NA checkbox
#             na_other_checked = request.POST.get("na_other_checkbox") == "on"
#             if na_other_checked:
#                 quotation.other_details = ""
#             else:
#                 static_qs = form.cleaned_data.get("other_items") or []
#                 static_names = []
#                 for item in static_qs:
#                     if hasattr(item, 'name'):
#                         static_names.append(item.name)
#                 dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#                 combined = []
#                 for n in static_names + dynamic_inputs:
#                     if n and n not in combined:
#                         combined.append(n)
#                 quotation.other_details = " / ".join(combined)
#
#             quotation.save()
#
#             # Update system_na using raw SQL to handle bit varying
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', quotation.id])
#
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             quotation.inverter_companies.set(inverter_ids)
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 try:
#                     inv = InverterCompany.objects.get(id=inv_id)
#                     inv_names.append(inv.name)
#                     wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                     inv_warranties.append(wt)
#                 except InverterCompany.DoesNotExist:
#                     continue
#             quotation.inverter_company_names = " / ".join(inv_names)
#             quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES
#             rep_ids = request.POST.getlist('representatives')
#             quotation.representatives.set(rep_ids)
#
#             rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
#             rep_texts = []
#             for i, rep_id in enumerate(rep_ids):
#                 if rep_id in rep_dict:
#                     r = rep_dict[rep_id]
#                     contact_str = f" - {r.contact}" if r.contact else ""
#                     rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
#             quotation.representative_names = "\n".join(rep_texts)
#
#             # TERMS & CONDITIONS
#             terms_ids = request.POST.getlist('terms_conditions')
#             if terms_ids:
#                 quotation.terms_conditions.set(terms_ids)
#                 terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
#                 terms_texts = []
#                 for i, term in enumerate(terms_qs, 1):
#                     terms_texts.append(f"{i}. {term.content}")
#                 quotation.terms_conditions_text = "\n".join(terms_texts)
#             else:
#                 quotation.terms_conditions.clear()
#                 quotation.terms_conditions_text = ""
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             quotation.save()
#
#             # Update system_na again
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = %s
#                     WHERE id = %s
#                 """, ['1' if system_na else '0', quotation.id])
#
#             # If this is an AJAX save request (save_only), return JSON success
#             if is_ajax:
#                 return JsonResponse({
#                     'success': True,
#                     'quotation_id': quotation.pk,
#                     'message': 'Quotation saved successfully'
#                 })
#
#             # If this is a normal POST with pdf_template selected, redirect to PDF
#             pdf_template = request.POST.get('pdf_template', 'quotation')
#             if pdf_template == 'industrial':
#                 return redirect("quotation:industrial_quotation_pdf", pk=quotation.pk)
#             else:
#                 return redirect("quotation:quotation_pdf", pk=quotation.pk)
#
#         else:
#             # Form has errors
#             logger.error(f"Form errors: {form.errors}")
#
#             # If AJAX request, return errors as JSON
#             if is_ajax:
#                 return JsonResponse({
#                     'success': False,
#                     'errors': dict(form.errors)
#                 }, status=400)
#
#             # For normal POST with errors, render the form with errors
#             # Re-prepare inverter companies warranty mapping
#             stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#             stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#             name_to_wt = {}
#             for i, name in enumerate(stored_names):
#                 name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#             for comp in inverter_companies:
#                 comp.warranty = name_to_wt.get(comp.name, "")
#
#     else:
#         # GET request - create form pre-filled with existing quotation data
#         form = QuotationForm(instance=quotation)
#
#         # Get existing term IDs from the quotation
#         existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#
#         # Combine active and existing term IDs
#         all_term_ids = list(set(active_term_ids + existing_term_ids))
#
#         if all_term_ids:
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
#         else:
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         # Pre-check static other_items checkboxes
#         if quotation.other_details:
#             static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#             if static_names_to_check:
#                 checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#                 form.fields["other_items"].initial = checked_qs
#
#     # Prepare warranty mapping (for GET and POST with errors)
#     if 'form' in locals() and form.errors:
#         # If we're re-rendering with errors, use the POST data for inverter warranties
#         pass  # Already handled above
#     else:
#         # For GET or successful POST
#         stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#         stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#         name_to_wt = {}
#         for i, name in enumerate(stored_names):
#             name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#         for comp in inverter_companies:
#             comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "quotation": quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/edit_quotation.html", context)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db import connection
from .models import Quotation, SolarPanelCompany, InverterCompany, TermsAndCondition, OtherItem, Representative, \
    PlantCapacity
from .forms import QuotationForm
import logging

logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db import connection
from .models import Quotation, SolarPanelCompany, InverterCompany, TermsAndCondition, OtherItem, Representative, \
    PlantCapacity
from .forms import QuotationForm
import logging

logger = logging.getLogger(__name__)

#
# def edit_quotation(request, pk):
#     """
#     Edit an existing quotation (not create a revision).
#     Similar to revise_quotation but updates the same quotation instead of creating a new one.
#     """
#     quotation = get_object_or_404(Quotation, pk=pk)
#
#     panel_companies = list(SolarPanelCompany.objects.all())
#     inverter_companies = list(InverterCompany.objects.all())
#
#     # Get active terms and conditions - handle bit varying properly
#     try:
#         # Try with text cast first (most reliable)
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT id FROM quotation_termsandcondition
#                 WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes', 'on')
#             """)
#             active_term_ids = [row[0] for row in cursor.fetchall()]
#         terms_conditions = TermsAndCondition.objects.filter(id__in=active_term_ids).order_by('id')
#     except Exception as e:
#         logger.error(f"Error getting active terms with text cast: {e}")
#         try:
#             # Try alternative - just check for '1' in bit varying
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM quotation_termsandcondition
#                     WHERE is_active = '1'::bit varying
#                 """)
#                 active_term_ids = [row[0] for row in cursor.fetchall()]
#             terms_conditions = TermsAndCondition.objects.filter(id__in=active_term_ids).order_by('id')
#         except Exception as e2:
#             logger.error(f"Error getting active terms with bit varying: {e2}")
#             # Last resort: get all terms and filter in Python
#             all_terms = TermsAndCondition.objects.all().order_by('id')
#             # Try to determine active terms by checking their values
#             active_term_ids = []
#             for term in all_terms:
#                 try:
#                     # Try to get the raw value
#                     with connection.cursor() as cursor:
#                         cursor.execute("""
#                             SELECT is_active FROM quotation_termsandcondition WHERE id = %s
#                         """, [term.id])
#                         result = cursor.fetchone()
#                         if result:
#                             # Check if value indicates active (1, t, true, etc.)
#                             value = str(result[0]).lower()
#                             if value in ('1', 't', 'true', 'y', 'yes', 'on'):
#                                 active_term_ids.append(term.id)
#                 except:
#                     continue
#             terms_conditions = TermsAndCondition.objects.filter(id__in=active_term_ids).order_by('id')
#             if not active_term_ids:
#                 # If still no active terms, use all terms
#                 terms_conditions = all_terms
#                 active_term_ids = list(all_terms.values_list('id', flat=True))
#
#     # Build other_dynamic_list from stored other_details
#     other_dynamic_list = [x.strip() for x in (quotation.other_details or "").split(" / ") if x.strip()]
#
#     # Set of names existing in OtherItem table
#     static_item_names = set(OtherItem.objects.values_list("name", flat=True))
#
#     if request.method == "POST":
#         # Check if this is an AJAX save request
#         is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('save_only')
#
#         # Get existing term IDs from the quotation
#         existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#
#         # Get submitted term IDs from POST data
#         submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
#
#         # Combine: active + existing + submitted
#         all_term_ids = list(set(active_term_ids + existing_term_ids + submitted_term_ids))
#
#         # Create queryset
#         if all_term_ids:
#             terms_queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
#         else:
#             terms_queryset = TermsAndCondition.objects.none()
#
#         # Create form with instance
#         form = QuotationForm(request.POST, instance=quotation)
#         form.fields['terms_conditions'].queryset = terms_queryset
#
#         # Validate the form
#         if form.is_valid():
#             quotation = form.save(commit=False)
#
#             # Handle system_na checkbox
#             system_na = form.cleaned_data.get('system_na', False)
#             if system_na:
#                 quotation.dc_capacity = None
#                 quotation.ac_capacity = None
#             else:
#                 quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
#                 quotation.ac_capacity = form.cleaned_data.get('ac_capacity')
#
#             quotation.system_na = False
#
#             # Handle Other Details NA checkbox
#             na_other_checked = request.POST.get("na_other_checkbox") == "on"
#             if na_other_checked:
#                 quotation.other_details = ""
#             else:
#                 static_qs = form.cleaned_data.get("other_items") or []
#                 static_names = []
#                 for item in static_qs:
#                     if hasattr(item, 'name'):
#                         static_names.append(item.name)
#                 dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
#                 combined = []
#                 for n in static_names + dynamic_inputs:
#                     if n and n not in combined:
#                         combined.append(n)
#                 quotation.other_details = " / ".join(combined)
#
#             quotation.save()
#
#             # Update system_na using raw SQL to handle bit varying
#             try:
#                 # First try Django's save
#                 quotation.system_na = system_na
#                 quotation.save()
#             except Exception as e:
#                 logger.warning(f"Django save failed for system_na, using raw SQL: {e}")
#                 # If Django save fails, use raw SQL with text value
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         UPDATE quotation_quotation
#                         SET system_na = %s
#                         WHERE id = %s
#                     """, ['1' if system_na else '0', quotation.id])
#
#             form.save_m2m()
#
#             # PANEL COMPANIES
#             panel_ids = request.POST.getlist("panel_companies")
#             quotation.panel_companies.set(panel_ids)
#             panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
#             quotation.panel_company_names = " / ".join(panel_names)
#
#             # INVERTER COMPANIES + warranty
#             inverter_ids = request.POST.getlist("inverter_companies")
#             quotation.inverter_companies.set(inverter_ids)
#             inv_names = []
#             inv_warranties = []
#             for inv_id in inverter_ids:
#                 try:
#                     inv = InverterCompany.objects.get(id=inv_id)
#                     inv_names.append(inv.name)
#                     wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
#                     inv_warranties.append(wt)
#                 except InverterCompany.DoesNotExist:
#                     continue
#             quotation.inverter_company_names = " / ".join(inv_names)
#             quotation.inverter_warranty = " / ".join(inv_warranties)
#
#             # REPRESENTATIVES
#             rep_ids = request.POST.getlist('representatives')
#             quotation.representatives.set(rep_ids)
#
#             rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
#             rep_texts = []
#             for i, rep_id in enumerate(rep_ids):
#                 if rep_id in rep_dict:
#                     r = rep_dict[rep_id]
#                     contact_str = f" - {r.contact}" if r.contact else ""
#                     rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
#             quotation.representative_names = "\n".join(rep_texts)
#
#             # TERMS & CONDITIONS
#             terms_ids = request.POST.getlist('terms_conditions')
#             if terms_ids:
#                 quotation.terms_conditions.set(terms_ids)
#                 terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
#                 terms_texts = []
#                 for i, term in enumerate(terms_qs, 1):
#                     terms_texts.append(f"{i}. {term.content}")
#                 quotation.terms_conditions_text = "\n".join(terms_texts)
#             else:
#                 quotation.terms_conditions.clear()
#                 quotation.terms_conditions_text = ""
#
#             # PRICING
#             pricing_mode = form.cleaned_data.get("pricing_mode")
#             net_input = form.cleaned_data.get("net_amount_input")
#             final_input = form.cleaned_data.get("final_amount_input")
#
#             if pricing_mode == "net" and net_input is not None:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#             elif pricing_mode == "final" and final_input is not None:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             quotation.save()
#
#             # Update system_na again
#             try:
#                 quotation.system_na = system_na
#                 quotation.save()
#             except:
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         UPDATE quotation_quotation
#                         SET system_na = %s
#                         WHERE id = %s
#                     """, ['1' if system_na else '0', quotation.id])
#
#             # If this is an AJAX save request (save_only), return JSON success
#             if is_ajax:
#                 return JsonResponse({
#                     'success': True,
#                     'quotation_id': quotation.pk,
#                     'message': 'Quotation saved successfully'
#                 })
#
#             # If this is a normal POST with pdf_template selected, redirect to PDF
#             pdf_template = request.POST.get('pdf_template', 'quotation')
#             if pdf_template == 'industrial':
#                 return redirect("quotation:industrial_quotation_pdf", pk=quotation.pk)
#             else:
#                 return redirect("quotation:quotation_pdf", pk=quotation.pk)
#
#         else:
#             # Form has errors
#             logger.error(f"Form errors: {form.errors}")
#
#             # If AJAX request, return errors as JSON
#             if is_ajax:
#                 return JsonResponse({
#                     'success': False,
#                     'errors': dict(form.errors)
#                 }, status=400)
#
#             # For normal POST with errors, render the form with errors
#             # Re-prepare inverter companies warranty mapping
#             stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#             stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#             name_to_wt = {}
#             for i, name in enumerate(stored_names):
#                 name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#             for comp in inverter_companies:
#                 comp.warranty = name_to_wt.get(comp.name, "")
#
#             # Re-set terms queryset for error display
#             if 'all_term_ids' in locals():
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(
#                     id__in=all_term_ids) if all_term_ids else TermsAndCondition.objects.none()
#             else:
#                 # Recalculate all_term_ids for error display
#                 existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#                 submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
#                 all_term_ids = list(set(active_term_ids + existing_term_ids + submitted_term_ids))
#                 form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(
#                     id__in=all_term_ids) if all_term_ids else TermsAndCondition.objects.none()
#
#     else:
#         # GET request - create form pre-filled with existing quotation data
#         form = QuotationForm(instance=quotation)
#
#         # Get existing term IDs from the quotation
#         existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
#
#         # Combine active and existing term IDs
#         all_term_ids = list(set(active_term_ids + existing_term_ids))
#
#         if all_term_ids:
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
#         else:
#             form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         # Pre-check static other_items checkboxes
#         if quotation.other_details:
#             static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
#             if static_names_to_check:
#                 checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
#                 form.fields["other_items"].initial = checked_qs
#
#     # Prepare warranty mapping (for GET and POST with errors)
#     if 'form' in locals() and form.errors:
#         # If we're re-rendering with errors, use the POST data for inverter warranties
#         pass  # Already handled above
#     else:
#         # For GET or successful POST
#         stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
#         stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
#         name_to_wt = {}
#         for i, name in enumerate(stored_names):
#             name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
#         for comp in inverter_companies:
#             comp.warranty = name_to_wt.get(comp.name, "")
#
#     context = {
#         "form": form,
#         "quotation": quotation,
#         "panel_companies": panel_companies,
#         "inverter_companies": inverter_companies,
#         "terms_conditions": terms_conditions,
#         "other_dynamic_list": other_dynamic_list,
#         "static_item_names": static_item_names,
#         "representatives": Representative.objects.all().order_by('name'),
#     }
#     return render(request, "quotation/edit_quotation.html", context)


def edit_quotation(request, pk):
    """
    Edit an existing quotation (not create a revision).
    Similar to revise_quotation but updates the same quotation instead of creating a new one.
    """
    quotation = get_quotation_or_404_for_request(request, pk)

    panel_companies = list(SolarPanelCompany.objects.all())
    inverter_companies = list(InverterCompany.objects.all())

    # Get active terms and conditions - handle bit varying properly
    try:
        # Try with text cast first (most reliable)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM quotation_termsandcondition 
                WHERE CAST(is_active AS TEXT) IN ('1', 't', 'true', 'y', 'yes', 'on')
            """)
            active_term_ids = [row[0] for row in cursor.fetchall()]
        terms_conditions = TermsAndCondition.objects.filter(id__in=active_term_ids).order_by('id')
    except Exception as e:
        logger.error(f"Error getting active terms with text cast: {e}")
        try:
            # Try alternative - just check for '1' in bit varying
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM quotation_termsandcondition 
                    WHERE is_active = '1'::bit varying
                """)
                active_term_ids = [row[0] for row in cursor.fetchall()]
            terms_conditions = TermsAndCondition.objects.filter(id__in=active_term_ids).order_by('id')
        except Exception as e2:
            logger.error(f"Error getting active terms with bit varying: {e2}")
            # Last resort: get all terms and filter in Python
            all_terms = TermsAndCondition.objects.all().order_by('id')
            # Try to determine active terms by checking their values
            active_term_ids = []
            for term in all_terms:
                try:
                    # Try to get the raw value
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT is_active FROM quotation_termsandcondition WHERE id = %s
                        """, [term.id])
                        result = cursor.fetchone()
                        if result:
                            # Check if value indicates active (1, t, true, etc.)
                            value = str(result[0]).lower()
                            if value in ('1', 't', 'true', 'y', 'yes', 'on'):
                                active_term_ids.append(term.id)
                except:
                    continue
            terms_conditions = TermsAndCondition.objects.filter(id__in=active_term_ids).order_by('id')
            if not active_term_ids:
                # If still no active terms, use all terms
                terms_conditions = all_terms
                active_term_ids = list(all_terms.values_list('id', flat=True))

    # Build other_dynamic_list from stored other_details
    other_dynamic_list = [x.strip() for x in (quotation.other_details or "").split(" / ") if x.strip()]

    # Set of names existing in OtherItem table
    static_item_names = set(OtherItem.objects.values_list("name", flat=True))

    if request.method == "POST":
        # Check if this is an AJAX save request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('save_only')

        # Get existing term IDs from the quotation
        existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))

        # Get submitted term IDs from POST data
        submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]

        # Combine: active + existing + submitted
        all_term_ids = list(set(active_term_ids + existing_term_ids + submitted_term_ids))

        # Create queryset
        if all_term_ids:
            terms_queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
        else:
            terms_queryset = TermsAndCondition.objects.none()

        # Create form with instance
        form = QuotationForm(
            request.POST,
            instance=quotation,
            terms_conditions_queryset=terms_queryset,
            form_user=request.user,
        )
        # # Create form with instance
        # form = QuotationForm(request.POST, instance=quotation)
        # form.fields['terms_conditions'].queryset = terms_queryset

        # Validate the form
        if form.is_valid():
            quotation = form.save(commit=False)

            # Handle system_na checkbox
            system_na = form.cleaned_data.get('system_na', False)
            if system_na:
                quotation.dc_capacity = None
                quotation.ac_capacity = None
            else:
                quotation.dc_capacity = form.cleaned_data.get('dc_capacity')
                quotation.ac_capacity = form.cleaned_data.get('ac_capacity')

            quotation.system_na = False

            # Handle new fields from form
            quotation.consumer_state = form.cleaned_data.get('consumer_state', '')
            quotation.consumer_email = form.cleaned_data.get('consumer_email', '')
            quotation.project_type = form.cleaned_data.get('project_type', '')

            # Handle Other Details NA checkbox
            na_other_checked = request.POST.get("na_other_checkbox") == "on"
            if na_other_checked:
                quotation.other_details = ""
            else:
                static_qs = form.cleaned_data.get("other_items") or []
                static_names = []
                for item in static_qs:
                    if hasattr(item, 'name'):
                        static_names.append(item.name)
                dynamic_inputs = [x.strip() for x in request.POST.getlist("dynamic_other_items[]") if x.strip()]
                combined = []
                for n in static_names + dynamic_inputs:
                    if n and n not in combined:
                        combined.append(n)
                quotation.other_details = " / ".join(combined)

            quotation.save()

            # Update system_na using raw SQL to handle bit varying
            try:
                # First try Django's save
                quotation.system_na = system_na
                quotation.save()
            except Exception as e:
                logger.warning(f"Django save failed for system_na, using raw SQL: {e}")
                # If Django save fails, use raw SQL with text value
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE quotation_quotation 
                        SET system_na = %s 
                        WHERE id = %s
                    """, ['1' if system_na else '0', quotation.id])

            form.save_m2m()

            # PANEL COMPANIES
            panel_ids = request.POST.getlist("panel_companies")
            quotation.panel_companies.set(panel_ids)
            panel_names = SolarPanelCompany.objects.filter(id__in=panel_ids).values_list("name", flat=True)
            quotation.panel_company_names = " / ".join(panel_names)

            # INVERTER COMPANIES + warranty
            inverter_ids = request.POST.getlist("inverter_companies")
            quotation.inverter_companies.set(inverter_ids)
            inv_names = []
            inv_warranties = []
            for inv_id in inverter_ids:
                try:
                    inv = InverterCompany.objects.get(id=inv_id)
                    inv_names.append(inv.name)
                    wt = request.POST.get(f"inverter_warranty_{inv_id}", "").strip()
                    inv_warranties.append(wt)
                except InverterCompany.DoesNotExist:
                    continue
            quotation.inverter_company_names = " / ".join(inv_names)
            quotation.inverter_warranty = " / ".join(inv_warranties)

            # REPRESENTATIVES
            rep_ids = request.POST.getlist('representatives')
            quotation.representatives.set(rep_ids)

            rep_dict = {str(r.id): r for r in Representative.objects.filter(id__in=rep_ids)}
            rep_texts = []
            for i, rep_id in enumerate(rep_ids):
                if rep_id in rep_dict:
                    r = rep_dict[rep_id]
                    contact_str = f" - {r.contact}" if r.contact else ""
                    rep_texts.append(f"{i + 1}. {r.name}{contact_str}")
            quotation.representative_names = "\n".join(rep_texts)

            # TERMS & CONDITIONS
            terms_ids = request.POST.getlist('terms_conditions')
            if terms_ids:
                quotation.terms_conditions.set(terms_ids)
                terms_qs = TermsAndCondition.objects.filter(id__in=terms_ids).order_by('id')
                terms_texts = []
                for i, term in enumerate(terms_qs, 1):
                    terms_texts.append(f"{i}. {term.content}")
                quotation.terms_conditions_text = "\n".join(terms_texts)
            else:
                quotation.terms_conditions.clear()
                quotation.terms_conditions_text = ""

            # PRICING
            pricing_mode = form.cleaned_data.get("pricing_mode")
            net_input = form.cleaned_data.get("net_amount_input")
            final_input = form.cleaned_data.get("final_amount_input")

            if pricing_mode == "net" and net_input is not None:
                quotation.net_amount = net_input
                quotation.calculate_from_net()
            elif pricing_mode == "final" and final_input is not None:
                quotation.final_amount = final_input
                quotation.calculate_from_final()

            quotation.save()

            # Update system_na again
            try:
                quotation.system_na = system_na
                quotation.save()
            except:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE quotation_quotation 
                        SET system_na = %s 
                        WHERE id = %s
                    """, ['1' if system_na else '0', quotation.id])

            # If this is an AJAX save request (save_only), return JSON success
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'quotation_id': quotation.pk,
                    'message': 'Quotation saved successfully'
                })

            # If this is a normal POST with pdf_template selected, redirect to PDF
            pdf_template = request.POST.get('pdf_template', 'quotation')
            if pdf_template == 'industrial':
                return redirect("quotation:industrial_quotation_pdf", pk=quotation.pk)
            else:
                return redirect("quotation:quotation_pdf", pk=quotation.pk)

        else:
            # Form has errors
            logger.error(f"Form errors: {form.errors}")

            # If AJAX request, return errors as JSON
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors)
                }, status=400)

            # For normal POST with errors, render the form with errors
            # Re-prepare inverter companies warranty mapping
            stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
            stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
            name_to_wt = {}
            for i, name in enumerate(stored_names):
                name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
            for comp in inverter_companies:
                comp.warranty = name_to_wt.get(comp.name, "")

            # Re-set terms queryset for error display
            if 'all_term_ids' in locals():
                form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(
                    id__in=all_term_ids) if all_term_ids else TermsAndCondition.objects.none()
            else:
                # Recalculate all_term_ids for error display
                existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))
                submitted_term_ids = [int(id) for id in request.POST.getlist('terms_conditions') if id.isdigit()]
                all_term_ids = list(set(active_term_ids + existing_term_ids + submitted_term_ids))
                form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(
                    id__in=all_term_ids) if all_term_ids else TermsAndCondition.objects.none()

    else:
        # GET request - create form pre-filled with existing quotation data
        form = QuotationForm(instance=quotation, form_user=request.user)

        # Get existing term IDs from the quotation
        existing_term_ids = list(quotation.terms_conditions.values_list('id', flat=True))

        # Combine active and existing term IDs
        all_term_ids = list(set(active_term_ids + existing_term_ids))

        if all_term_ids:
            form.fields['terms_conditions'].queryset = TermsAndCondition.objects.filter(id__in=all_term_ids)
        else:
            form.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()

        # Pre-check static other_items checkboxes
        if quotation.other_details:
            static_names_to_check = [n for n in other_dynamic_list if n in static_item_names]
            if static_names_to_check:
                checked_qs = OtherItem.objects.filter(name__in=static_names_to_check)
                form.fields["other_items"].initial = checked_qs

    # Prepare warranty mapping (for GET and POST with errors)
    if 'form' in locals() and form.errors:
        # If we're re-rendering with errors, use the POST data for inverter warranties
        pass  # Already handled above
    else:
        # For GET or successful POST
        stored_names = [n.strip() for n in (quotation.inverter_company_names or "").split(" / ") if n.strip()]
        stored_wts = [w.strip() for w in (quotation.inverter_warranty or "").split(" / ") if w.strip()]
        name_to_wt = {}
        for i, name in enumerate(stored_names):
            name_to_wt[name] = stored_wts[i] if i < len(stored_wts) else ""
        for comp in inverter_companies:
            comp.warranty = name_to_wt.get(comp.name, "")

    context = {
        "form": form,
        "quotation": quotation,
        "panel_companies": panel_companies,
        "inverter_companies": inverter_companies,
        "terms_conditions": terms_conditions,
        "other_dynamic_list": other_dynamic_list,
        "static_item_names": static_item_names,
        "representatives": Representative.objects.all().order_by('name'),
    }
    return render(request, "quotation/edit_quotation.html", context)


# ---- AJAX: Add Panel Company ----
@require_POST
def add_panel_company_api(request):
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Name required'}, status=400)

    obj, created = SolarPanelCompany.objects.get_or_create(name=name)
    return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name})


# ---- AJAX: Add Inverter Company ----
@require_POST
def add_inverter_company_api(request):
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Name required'}, status=400)

    obj, created = InverterCompany.objects.get_or_create(name=name)
    return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name})


# def create_panel_company(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         if name:
#             obj, created = SolarPanelCompany.objects.get_or_create(name=name)
#             return JsonResponse({"success": True, "id": obj.id, "name": obj.name})
#     return JsonResponse({"success": False})
#
# def create_inverter_company(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         if name:
#             obj, created = InverterCompany.objects.get_or_create(name=name)
#             return JsonResponse({"success": True, "id": obj.id, "name": obj.name})
#     return JsonResponse({"success": False})


#
# def edit_quotation(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#     # ItemFormSet = modelformset_factory(QuotationItem, form=QuotationItemForm, extra=0, can_delete=True)
#     panel_companies = SolarPanelCompany.objects.all()
#     inverter_companies = InverterCompany.objects.all()
#
#     if request.method == 'POST':
#         form = QuotationForm(request.POST, instance=quotation)
#         # formset = ItemFormSet(request.POST, queryset=quotation.items.all())
#
#         # if form.is_valid() and formset.is_valid():
#             q = form.save()
#             q.panel_companies.set(request.POST.getlist('panel_companies'))
#             q.inverter_companies.set(request.POST.getlist('inverter_companies'))
#
#             # for item_form in formset:
#                 if item_form.cleaned_data:
#                     if item_form.cleaned_data.get('DELETE'):
#                         if item_form.instance.pk:
#                             item_form.instance.delete()
#                     else:
#                         item = item_form.save(commit=False)
#                         item.quotation = q
#                         item.save()
#
#             q.calculate_totals()
#             return redirect('quotation:quotation_pdf', pk=q.pk)
#         else:
#             print("Edit form errors:", form.errors)
#             print("Edit formset errors:", formset.errors)
#     else:
#         form = QuotationForm(instance=quotation)
#         formset = ItemFormSet(queryset=quotation.items.all())
#
#     context = {
#         'form': form,
#         'formset': formset,
#         'quotation': quotation,
#         'panel_companies': panel_companies,
#         'inverter_companies': inverter_companies,
#     }
#     return render(request, 'quotation/edit_quotation.html', context)


# def create_quotation(request):
#     # ItemFormSet = modelformset_factory(QuotationItem, form=QuotationItemForm, extra=1, can_delete=True)
#     panel_companies = SolarPanelCompany.objects.all()
#     inverter_companies = InverterCompany.objects.all()
#
#     if request.method == 'POST':
#         form = QuotationForm(request.POST)
#         # formset = ItemFormSet(request.POST, queryset=QuotationItem.objects.none())
#
#         if form.is_valid() and formset.is_valid():
#             quotation = form.save(commit=False)
#             pricing_mode = form.cleaned_data.get('pricing_mode')
#             net_input = form.cleaned_data.get('net_amount_input')
#             final_input = form.cleaned_data.get('final_amount_input')
#
#             quotation.save()
#             form.save_m2m()  # REQUIRED for many-to-many
#
#             panel_ids = request.POST.getlist('panel_companies')
#             quotation.panel_companies.set(panel_ids)
#
#             quotation.panel_company_names = "/".join(
#                 SolarPanelCompany.objects.filter(id__in=panel_ids).values_list('name', flat=True)
#             )
#
#             inverter_ids = request.POST.getlist('inverter_companies')
#             quotation.inverter_companies.set(inverter_ids)
#
#             quotation.inverter_company_names = "/".join(
#                 InverterCompany.objects.filter(id__in=inverter_ids).values_list('name', flat=True)
#             )
#
#             quotation.save()
#
#             # quotation.save()
#             # quotation.panel_companies.set(request.POST.getlist('panel_companies'))
#             # quotation.inverter_companies.set(request.POST.getlist('inverter_companies'))
#
#             # # Save all item rows
#             # for item_form in formset:
#             #     if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
#             #         item = item_form.save(commit=False)
#             #         item.quotation = quotation
#             #         item.save()
#
#             # Apply pricing logic
#             if pricing_mode == 'net' and net_input:
#                 quotation.net_amount = net_input
#                 quotation.calculate_from_net()
#             elif pricing_mode == 'final' and final_input:
#                 quotation.final_amount = final_input
#                 quotation.calculate_from_final()
#
#             return redirect('quotation:quotation_pdf', pk=quotation.pk)
#     else:
#         form = QuotationForm()
#         # formset = ItemFormSet(queryset=QuotationItem.objects.none())
#
#     context = {
#         'form': form,
#         'formset': formset,
#         'panel_companies': panel_companies,
#         'inverter_companies': inverter_companies,
#     }
#     return render(request, 'quotation/create_quotation.html', context)


@require_POST
def add_other_item_api(request):
    """
    AJAX endpoint to create a new OtherItem.
    Expects: POST 'name'
    Returns: JSON { success: True, id: ..., name: ... } or error
    """
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Name required'}, status=400)

    # create or get existing
    obj, created = OtherItem.objects.get_or_create(name=name)
    return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name, 'created': created})


@require_POST
def add_terms_condition_api(request):
    content = request.POST.get('content', '').strip()
    # Handle both 'true'/'false' strings and boolean values
    has_yellow_background_str = request.POST.get('has_yellow_background', 'false')
    has_yellow_background = has_yellow_background_str in ('true', 'True', '1', 1, True)

    if not content:
        return JsonResponse({'success': False, 'error': 'Content required'}, status=400)

    # Handle bit varying columns using raw SQL to avoid type mismatch errors
    try:
        with connection.cursor() as cursor:
            # Insert using raw SQL with proper bit varying casting
            cursor.execute("""
                INSERT INTO quotation_termsandcondition (content, has_yellow_background, is_active, created_at)
                VALUES (%s, (%s)::bit(1)::bit varying, B'1'::bit varying, now())
                RETURNING id
            """, [content, 1 if has_yellow_background else 0])
            new_id = cursor.fetchone()[0]

        # Fetch the created object to return
        obj = TermsAndCondition.objects.get(id=new_id)
        # Convert bit varying to boolean for JSON response
        # The BitVaryingBooleanField should handle this, but ensure we return boolean
        has_yellow_value = bool(obj.has_yellow_background) if hasattr(obj,
                                                                      'has_yellow_background') else has_yellow_background

        return JsonResponse({
            'success': True,
            'id': obj.id,
            'content': obj.content,
            'has_yellow_background': has_yellow_value
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating term and condition: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Alias for add_terms_api URL
add_terms_api = add_terms_condition_api


# def add_terms_api(request):
#     if request.method == "POST":
#         content = request.POST.get('content', '').strip()
#         has_yellow_background = request.POST.get('has_yellow_background') == 'true'
#
#         if not content:
#             return JsonResponse({'success': False, 'error': 'Content is required'})
#
#         try:
#             term = TermsAndCondition.objects.create(
#                 content=content,
#                 has_yellow_background=has_yellow_background
#             )
#             return JsonResponse({
#                 'success': True,
#                 'id': term.id,
#                 'content': term.content
#             })
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#
#     return JsonResponse({'success': False, 'error': 'Invalid method'})


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404

@require_POST
@csrf_protect
def update_representative_api(request):
    """
    Expects POST: id, name, contact
    Returns JSON: success, id, name, contact
    """
    rep_id = request.POST.get('id')
    name = request.POST.get('name', '').strip()
    contact = request.POST.get('contact', '').strip()

    if not rep_id:
        return JsonResponse({'success': False, 'error': 'Representative id required'}, status=400)
    if not name:
        return JsonResponse({'success': False, 'error': 'Name required'}, status=400)

    rep = get_object_or_404(Representative, pk=rep_id)
    rep.name = name
    rep.contact = contact
    rep.save()

    return JsonResponse({'success': True, 'id': rep.id, 'name': rep.name, 'contact': rep.contact})


# AJAX endpoints kept unchanged
@require_POST
def add_panel_company_api(request):
    name = request.POST.get("name", "").strip()
    if not name:
        return JsonResponse({"success": False, "error": "Name required"}, status=400)
    obj, created = SolarPanelCompany.objects.get_or_create(name=name)
    return JsonResponse({"success": True, "id": obj.id, "name": obj.name})


@require_POST
def add_inverter_company_api(request):
    name = request.POST.get("name", "").strip()
    if not name:
        return JsonResponse({"success": False, "error": "Name required"}, status=400)
    obj, created = InverterCompany.objects.get_or_create(name=name)
    return JsonResponse({"success": True, "id": obj.id, "name": obj.name})


@require_POST
def add_other_item_api(request):
    name = request.POST.get("name", "").strip()
    if not name:
        return JsonResponse({"success": False, "error": "Name required"}, status=400)
    obj, created = OtherItem.objects.get_or_create(name=name)
    return JsonResponse({"success": True, "id": obj.id, "name": obj.name, "created": created})

#
# def quotation_pdf(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#     reps = list(quotation.representatives.all())
#
#
#     # --- Calculations ---
#     # plant_capacity = float(quotation.plant_capacity_kw or 0)
#     plant_capacity = float(quotation.plant_capacity_kw.capacity) if quotation.plant_capacity_kw else 0.0
#
#
#
#     unit_rate = 11
#     subsidy = 78000.0
#     investment_cost = float(quotation.final_amount or quotation.net_amount or 0)
#
#     units_generated_per_year = plant_capacity * 4 * 365
#     yearly_saving = units_generated_per_year * unit_rate
#     after_subsidy_amount = investment_cost - subsidy
#     payback_period = round(after_subsidy_amount / yearly_saving, 1) if yearly_saving > 0 else 0
#
#     # Convert Amount to Words
#     amount_words = amount_in_words(quotation.final_amount)
#     # --- Calculate After Discount Amount ---
#     try:
#         net = float(quotation.net_amount or 0)
#         disc = float(quotation.special_discount or 0)
#         after_discount_amount = net - disc
#     except:
#         after_discount_amount = 0
#
#     # context = {
#     #     'quotation': quotation,
#     #     'units_generated_per_year': f"{units_generated_per_year:,.2f}",
#     #     'yearly_saving': f"{yearly_saving:,.2f}",
#     #     'after_subsidy_amount': f"{after_subsidy_amount:,.2f}",
#     #     'payback_period': payback_period,
#     #     'subsidy_amount': f"{subsidy:,.2f}",
#     #     'amount_words': amount_words,  # <-- ADDED
#     # }
#
#     context = {
#         'quotation': quotation,
#         'units_generated_per_year': units_generated_per_year,
#         'yearly_saving': yearly_saving,
#         'after_subsidy_amount': after_subsidy_amount,
#         'payback_period': payback_period,
#         'subsidy_amount': subsidy,
#         'amount_words': amount_words,
#         'unit_rate': unit_rate,
#         'after_discount_amount': after_discount_amount,  # <-- ADD THIS
#         'representatives': reps,
#     }
#
#     html = render_to_string('quotation/quotation_template.html', context)
#     sanitized_html = sanitize_css_units(html, content_width_pts=525)
#
#     result = BytesIO()
#     pisa_status = pisa.CreatePDF(
#         sanitized_html,
#         dest=result,
#         encoding='utf-8',
#         link_callback=link_callback,
#     )
#
#     if pisa_status.err:
#         return HttpResponse(
#             "Error creating PDF.<hr><pre>%s</pre>" % sanitized_html[:2000],
#             status=500
#         )
#
#     response = HttpResponse(result.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'filename="quotation_{quotation.pk}.pdf"'
#     return response

def quotation_pdf(request, pk):
    quotation = get_quotation_or_404_for_request(request, pk)
    # Refresh from database to ensure all fields are loaded
    quotation.refresh_from_db()
    reps = list(quotation.representatives.all())

    # Format other_details to replace / with ,
    if quotation.other_details:
        formatted_other_details = quotation.other_details.replace(' / ', ', ').replace('/', ', ')
    else:
        formatted_other_details = ''

    # Your existing calculations
    plant_capacity = float(quotation.plant_capacity_kw.capacity) if quotation.plant_capacity_kw else 0.0
    unit_rate = 11
    subsidy = 78000.0
    investment_cost = float(quotation.final_amount or quotation.net_amount or 0)

    units_generated_per_year = plant_capacity * 4 * 365
    yearly_saving = units_generated_per_year * unit_rate
    after_subsidy_amount = investment_cost - subsidy
    payback_period = round(after_subsidy_amount / yearly_saving, 1) if yearly_saving > 0 else 0

    amount_words = amount_in_words(quotation.final_amount)

    try:
        net = float(quotation.net_amount or 0)
        disc = float(quotation.special_discount or 0)
        after_discount_amount = net - disc
    except:
        after_discount_amount = 0

    # Get terms with yellow background flag - check raw database value
    terms_with_yellow = set()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM quotation_termsandcondition
                WHERE CAST(has_yellow_background AS TEXT) IN ('1', 't', 'true', 'y', 'yes')
            """)
            terms_with_yellow = {row[0] for row in cursor.fetchall()}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not fetch terms with yellow background: {e}")

    # Format date for template - ensure it's available and formatted
    from django.utils import timezone
    
    # Get the date value
    date_value = quotation.date if quotation.date else (quotation.created_at if quotation.created_at else timezone.now())
    
    # Format the date as string - handle both datetime objects and strings
    try:
        if date_value:
            # Check if it's a datetime object (has strftime method)
            if hasattr(date_value, 'strftime') and callable(getattr(date_value, 'strftime', None)):
                formatted_date = date_value.strftime('%d/%m/%Y')
            elif isinstance(date_value, str):
                # If it's a string, try to extract date part or use as-is
                # If it looks like a date string, try to format it
                if len(date_value) >= 10:
                    # Try to extract YYYY-MM-DD format
                    date_part = date_value[:10] if len(date_value) >= 10 else date_value
                    # Reverse from YYYY-MM-DD to DD/MM/YYYY
                    try:
                        parts = date_part.split('-')
                        if len(parts) == 3:
                            formatted_date = f"{parts[2]}/{parts[1]}/{parts[0]}"
                        else:
                            formatted_date = date_value
                    except:
                        formatted_date = date_value
                else:
                    formatted_date = date_value
            else:
                # Convert to string as fallback
                formatted_date = str(date_value)
        else:
            formatted_date = timezone.now().strftime('%d/%m/%Y')
    except Exception as e:
        # Fallback to current date if anything fails
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error formatting date: {e}")
        formatted_date = timezone.now().strftime('%d/%m/%Y')
    
    context = {
        'quotation': quotation,
        'quotation_date': date_value,  # Pass date object for template
        'formatted_date': formatted_date,  # Pass pre-formatted date string
        'formatted_other_details': formatted_other_details,  # Add the formatted version
        'units_generated_per_year': units_generated_per_year,
        'yearly_saving': yearly_saving,
        'after_subsidy_amount': after_subsidy_amount,
        'payback_period': payback_period,
        'subsidy_amount': subsidy,
        'amount_words': amount_words,
        'unit_rate': unit_rate,
        'after_discount_amount': after_discount_amount,
        'representatives': reps,
        'terms_with_yellow': terms_with_yellow,  # Set of term IDs with yellow background
    }

    html = render_to_string('quotation/quotation_template.html', context)
    sanitized_html = sanitize_css_units(html, content_width_pts=525)

    result = BytesIO()
    pisa_status = pisa.CreatePDF(
        sanitized_html,
        dest=result,
        encoding='utf-8',
        link_callback=link_callback,
    )

    if pisa_status.err:
        return HttpResponse(
            "Error creating PDF.<hr><pre>%s</pre>" % sanitized_html[:2000],
            status=500
        )

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'filename="quotation_{quotation.pk}.pdf"'
    return response

# def quotation_pdf(request, pk):
#     quotation = get_object_or_404(Quotation, pk=pk)
#     reps = list(quotation.representatives.all())
#
#     # Get PDF type from request
#     pdf_type = request.GET.get('pdf_type', 'quotation_template')
#
#     # Format other_details to replace / with ,
#     if quotation.other_details:
#         formatted_other_details = quotation.other_details.replace(' / ', ', ').replace('/', ', ')
#     else:
#         formatted_other_details = ''
#
#     # Your existing calculations
#     plant_capacity = float(quotation.plant_capacity_kw.capacity) if quotation.plant_capacity_kw else 0.0
#     unit_rate = 11
#     subsidy = 78000.0
#     investment_cost = float(quotation.final_amount or quotation.net_amount or 0)
#
#     units_generated_per_year = plant_capacity * 4 * 365
#     yearly_saving = units_generated_per_year * unit_rate
#     after_subsidy_amount = investment_cost - subsidy
#     payback_period = round(after_subsidy_amount / yearly_saving, 1) if yearly_saving > 0 else 0
#
#     amount_words = amount_in_words(quotation.final_amount)
#
#     try:
#         net = float(quotation.net_amount or 0)
#         disc = float(quotation.special_discount or 0)
#         after_discount_amount = net - disc
#     except:
#         after_discount_amount = 0
#
#     context = {
#         'quotation': quotation,
#         'formatted_other_details': formatted_other_details,
#         'units_generated_per_year': units_generated_per_year,
#         'yearly_saving': yearly_saving,
#         'after_subsidy_amount': after_subsidy_amount,
#         'payback_period': payback_period,
#         'subsidy_amount': subsidy,
#         'amount_words': amount_words,
#         'unit_rate': unit_rate,
#         'after_discount_amount': after_discount_amount,
#         'representatives': reps,
#     }
#
#     # Select template based on PDF type
#     if pdf_type == 'industrial_quotation':
#         template_name = 'quotation/industrial_quotation.html'
#     elif pdf_type == 'quotation_no_header_footer':
#         template_name = 'quotation/quotation_template.html'
#         # You can modify context or add flags to remove header/footer
#     elif pdf_type == 'industrial_no_header_footer':
#         template_name = 'quotation/industrial_quotation.html'
#         # You can modify context or add flags to remove header/footer
#     else:
#         template_name = 'quotation/quotation_template.html'
#
#     print(f"Generating PDF with template: {template_name}")  # Debug line
#
#     html = render_to_string(template_name, context)
#
#     # For debugging, you can check what template is being used
#     print(f"PDF Type: {pdf_type}")
#     print(f"Template: {template_name}")
#
#     # For no header/footer versions, modify the HTML
#     if 'no_header_footer' in pdf_type:
#         # Remove header and footer content
#         html = html.replace('id="header_content"', 'id="header_content" style="display:none;"')
#         html = html.replace('id="footer_content"', 'id="footer_content" style="display:none;"')
#         # Also remove any @frame directives for xhtml2pdf
#         html = html.replace('@frame header_frame', '/* @frame header_frame */')
#         html = html.replace('@frame footer_frame', '/* @frame footer_frame */')
#
#     sanitized_html = sanitize_css_units(html, content_width_pts=525)
#
#     result = BytesIO()
#     pisa_status = pisa.CreatePDF(
#         sanitized_html,
#         dest=result,
#         encoding='utf-8',
#         link_callback=link_callback,
#     )
#
#     if pisa_status.err:
#         return HttpResponse(
#             "Error creating PDF.<hr><pre>%s</pre>" % sanitized_html[:2000],
#             status=500
#         )
#
#     response = HttpResponse(result.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'filename="quotation_{quotation.pk}_{pdf_type}.pdf"'

#     return response


@require_POST
@csrf_protect
def check_consumer(request):
    """
    Check if a consumer number already exists in quotations.
    Returns JSON with consumer details if exists, or allows redirect if not.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        consumer_type = request.POST.get('consumer_type', '').strip()
        consumer_no = request.POST.get('consumer_no', '').strip()
        
        logger.info(f"check_consumer called with consumer_type={consumer_type}, consumer_no={consumer_no}")
        
        if not consumer_type or not consumer_no:
            return JsonResponse({
                'error': 'Consumer type and consumer number are required'
            }, status=400)
        
        # Check for quotations with this consumer_no
        try:
            quotations = Quotation.objects.filter(consumer_no=consumer_no).order_by('-created_at')
            quotations_count = quotations.count()
            
            logger.info(f"Found {quotations_count} quotations for consumer_no={consumer_no}")
            
            if quotations_count == 0:
                # No quotations found, allow redirect
                return JsonResponse({
                    'exists': False
                })
            
            # Get all quotations as a list to avoid multiple queries
            quotations_list = list(quotations[:10])  # Limit to 10 most recent
            
            # Check if there are multiple quotations with different consumer types
            unique_types = []
            for q in quotations_list:
                if q.consumer_type and q.consumer_type not in unique_types:
                    unique_types.append(q.consumer_type)
            
            if len(unique_types) > 1 or (len(unique_types) == 1 and unique_types[0] != consumer_type):
                # Multiple types or different type exists
                quotations_data = []
                for quot in quotations_list:
                    try:
                        # Format date safely
                        date_str = 'N/A'
                        if quot.date:
                            try:
                                if hasattr(quot.date, 'strftime'):
                                    date_str = quot.date.strftime('%d/%m/%Y')
                                else:
                                    date_str = str(quot.date)
                            except:
                                date_str = str(quot.date) if quot.date else 'N/A'
                        
                        # Format final_amount safely
                        final_amount_str = '0.00'
                        if quot.final_amount is not None:
                            try:
                                final_amount_str = str(quot.final_amount)
                            except:
                                final_amount_str = '0.00'
                        
                        quotations_data.append({
                            'consumer_type': quot.consumer_type or 'N/A',
                            'quotation_no': quot.quotation_no or 'N/A',
                            'final_amount': final_amount_str,
                            'date': date_str,
                            'consumer_name': quot.consumer_name or 'N/A'
                        })
                    except Exception as e:
                        logger.error(f"Error processing quotation {quot.pk}: {e}")
                        continue
                
                return JsonResponse({
                    'exists': True,
                    'multiple': True,
                    'quotations': quotations_data
                })
            
            # Single quotation exists with same or different type
            latest_quotation = quotations_list[0]
            
            # Format date safely
            date_str = 'N/A'
            if latest_quotation.date:
                try:
                    if hasattr(latest_quotation.date, 'strftime'):
                        date_str = latest_quotation.date.strftime('%d/%m/%Y')
                    else:
                        date_str = str(latest_quotation.date)
                except:
                    date_str = str(latest_quotation.date) if latest_quotation.date else 'N/A'
            
            # Format final_amount safely
            final_amount_str = '0.00'
            if latest_quotation.final_amount is not None:
                try:
                    final_amount_str = str(latest_quotation.final_amount)
                except:
                    final_amount_str = '0.00'
            
            return JsonResponse({
                'exists': True,
                'multiple': False,
                'consumer_name': latest_quotation.consumer_name or 'N/A',
                'quotation_no': latest_quotation.quotation_no or 'N/A',
                'final_amount': final_amount_str,
                'date': date_str,
                'consumer_type': latest_quotation.consumer_type or 'N/A'
            })
            
        except Exception as db_error:
            logger.error(f"Database error in check_consumer: {str(db_error)}", exc_info=True)
            return JsonResponse({
                'error': f'Database error: {str(db_error)}'
            }, status=500)
        
    except Exception as e:
        logger.error(f"Error in check_consumer: {str(e)}", exc_info=True)
        
        return JsonResponse({
            'error': f'An error occurred while checking consumer number: {str(e)}'
        }, status=500)