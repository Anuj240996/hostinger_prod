import datetime
from io import BytesIO
import os
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

from customer.models import Customer
from dashboard.models import staff_Notification
from user.models import Profile
from .models import *
from datetime import date
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from .decorators import auth_users, allowed_users
from django.contrib.auth import get_user, logout, login
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q

#from django.shortcuts import render, HttpResponse
import json
import traceback
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
try:
    from detect_barcodes.models import BarcodeImage, InverterImage
except Exception:
    BarcodeImage = None
    InverterImage = None


def now_ist():
    """Return current time in Indian Standard Time (Asia/Kolkata). Use this when saving timestamps."""
    return timezone.localtime(timezone.now())

# Create your views here.

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib import messages


def _firereport_qs_scoped_for_staff(qs, user):
    """
    Superuser: no extra filter.
    Associate: complaints raised by consumers (Account_id) linked via Assoc_Assign.
    Other staff: complaints assigned to this user (AssignTo).
    """
    from customer.staff_access import associate_consumer_user_ids, is_associate_staff

    if not user.is_authenticated:
        return qs.none()
    if user.is_superuser:
        return qs
    if is_associate_staff(user):
        ids = associate_consumer_user_ids(user)
        if not ids:
            return qs.none()
        return qs.filter(Account_id__in=ids)
    return qs.filter(AssignTo_id=user.id)


def _assert_firereport_staff_access(request, firereport):
    """Return HttpResponse (403/401) if user may not access this row; else None."""
    from django.http import HttpResponse
    from customer.staff_access import associate_consumer_user_ids, is_associate_staff

    u = request.user
    if not u.is_authenticated:
        return HttpResponse("Authentication required.", status=401)
    # Consumers (non-staff): only their own raised complaints
    if not u.is_staff:
        if firereport.Account_id != u.id:
            return HttpResponse("You are not authorized to view this complaint.", status=403)
        return None
    if u.is_superuser:
        return None
    if is_associate_staff(u):
        allowed = set(associate_consumer_user_ids(u))
        if firereport.Account_id not in allowed:
            return HttpResponse(
                "You are not authorized to view complaints outside your assigned consumers.",
                status=403,
            )
        return None
    if firereport.AssignTo_id != u.id:
        return HttpResponse("You are not authorized to view this complaint.", status=403)
    return None


def _service_qs_scoped_for_staff(qs, user):
    from customer.staff_access import associate_consumer_user_ids, is_associate_staff
    if not user.is_authenticated:
        return qs.none()
    if user.is_superuser:
        return qs
    if is_associate_staff(user):
        ids = associate_consumer_user_ids(user)
        if not ids:
            return qs.none()
        return qs.filter(Account_id__in=ids)
    return qs.filter(AssignTo_id=user.id)


def _assert_service_staff_access(request, service_request):
    """Return HttpResponse (403/401) if staff user may not access this service row; else None."""
    from django.http import HttpResponse
    from customer.staff_access import associate_consumer_user_ids, is_associate_staff

    u = request.user
    if not u.is_authenticated:
        return HttpResponse("Authentication required.", status=401)
    if u.is_superuser:
        return None
    # Service pages are staff-facing; keep non-staff blocked.
    if not u.is_staff:
        return HttpResponse("You are not authorized to view this service request.", status=403)
    if is_associate_staff(u):
        allowed = set(associate_consumer_user_ids(u))
        if service_request.Account_id not in allowed:
            return HttpResponse(
                "You are not authorized to view service requests outside your assigned consumers.",
                status=403,
            )
        return None
    if service_request.AssignTo_id != u.id:
        return HttpResponse("You are not authorized to view this service request.", status=403)
    return None


def _dedupe_firereport_rows(rows):
    """
    Some environments contain duplicate complaint IDs in the DB.
    Keep only one newest row per complaint id for list pages.
    """
    ordered = rows.order_by('-UpdationDate', '-Postingdate', '-id') if hasattr(rows, "order_by") else list(rows)
    seen = set()
    result = []
    for row in ordered:
        rid = getattr(row, "id", None)
        if rid in seen:
            continue
        seen.add(rid)
        result.append(row)
    # Keep final output strictly latest-first by reporting time.
    result.sort(
        key=lambda r: (
            getattr(r, "Postingdate", None) or getattr(r, "UpdationDate", None),
            getattr(r, "id", 0),
        ),
        reverse=True,
    )
    return result


@login_required(login_url='user-login')
def reporting(request):
    error = ""
    complaint_categories = [
        "Billing Issue",
        "Technical Issue",
        "Installation Issue",
        "Warranty Issue",
        "Service / Maintenance",
        "Other",
    ]
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    User = get_user_model()
    #user = request.user
    customer = Customer.objects.get(new_customer=request.user)
    if request.method == "POST":
        FullName = request.POST['FullName']
        MobileNumber = request.POST['MobileNumber']
        Location = request.POST['Location']
        complaint_category = (request.POST.get("ComplaintCategory") or "").strip()
        complaint_title = (request.POST.get("ComplaintTitle") or "").strip()
        complaint_description = (request.POST.get("Message") or "").strip()

        # Store in the Firereport.Message column in requested format:
        # [Category: Billing Issue] [Title: Test1Testing complaint]
        # Test complain .
        Message = f"[Category: {complaint_category}] [Title: {complaint_title}]\n{complaint_description}".strip()
        try:
            # Get the current user's id
            Account_id = request.user.id
            # MobileNumber = request.user.profile.phone
            # Location = request.user.profile.city
            # FullName = request.user.first_name + " " + request.user.last_name
            Firereport.objects.create(
                FullName=FullName,
                MobileNumber=MobileNumber,
                Location=Location,
                Message=Message,
                Account_id=Account_id,
                Status="Pending",
            )
            error = "no"
            try:
                messages.success(request, "Complaint submitted successfully.")
            except Exception:
                pass
        except Exception as e:
            traceback.print_exc()
            error = "yes"
            try:
                messages.error(request, "Something went wrong while submitting the complaint. Please try again.")
            except Exception:
                pass
    return render(request, 'reporting.html', locals())


@login_required(login_url='user-login')
def viewStatus(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if not request.user.is_authenticated:
        return redirect('admin_login')
    User = get_user_model()
    # Consumers: own complaints only. Staff (associates / engineers): scoped list same as Assign / dashboard_staff.
    if request.user.is_staff:
        firereport_qs = _firereport_qs_scoped_for_staff(Firereport.objects.all(), request.user).order_by("-id")
    else:
        all_users = request.user.id
        firereport_qs = Firereport.objects.filter(Account_id=all_users).order_by("-id")

    sd = None
    if request.method == 'POST':
        sd = (request.POST.get('searchdata') or "").strip()
        try:
            q = Q(FullName__icontains=sd) | Q(MobileNumber__icontains=sd) | Q(Location__icontains=sd)
            if sd.isdigit():
                q = q | Q(id=int(sd))
            firereport_qs = firereport_qs.filter(q)
        except:
            user = get_user(request)
            logout(request)
            login(request, user)
            if request.user.is_staff:
                firereport_qs = _firereport_qs_scoped_for_staff(Firereport.objects.all(), request.user).order_by("-id")
            else:
                firereport_qs = Firereport.objects.filter(Account_id=request.user.id).order_by("-id")

    # Parse message header into Title/Category for nicer display
    import re

    complaints = []
    for fr in firereport_qs:
        raw = fr.Message or ""
        cat = ""
        title = ""
        body = raw
        m = re.match(
            r"^\[Category:\s*(?P<cat>.*?)\]\s*\[Title:\s*(?P<title>.*?)\]\s*(?:\r?\n)?(?P<body>[\s\S]*)$",
            raw.strip(),
        )
        if m:
            cat = (m.group("cat") or "").strip()
            title = (m.group("title") or "").strip()
            body = (m.group("body") or "").strip()

        complaints.append(
            {
                "id": fr.id,
                "full_name": fr.FullName,
                "mobile": fr.MobileNumber,
                "location": fr.Location,
                "title": title,
                "category": cat,
                "message": body if body else raw,
                "postingdate": fr.Postingdate,
                "status": fr.Status or "Pending",
            }
        )

    # Small summary counts for header cards
    pending_q = Q(Status__isnull=True) | Q(Status="Pending")
    stats = {
        "total": firereport_qs.count(),
        "pending": firereport_qs.filter(pending_q).count(),
        "assigned": firereport_qs.filter(Status="Assigned").count(),
        "in_progress": firereport_qs.filter(Status="In Progress").count(),
        "work_in_progress": firereport_qs.filter(Status="Work in Progress").count(),
        "completed": firereport_qs.filter(Status="Request Completed").count(),
    }

    return render(request, 'viewStatus.html', locals())


@login_required(login_url='user-login')
def viewStatusDetails(request,pid):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    firereport = get_object_or_404(Firereport, pk=pid)
    denied = _assert_firereport_staff_access(request, firereport)
    if denied is not None:
        return denied
    # Parse "[Category: ...] [Title: ...]\n<message>" format for display.
    complaint_category = ""
    complaint_title = ""
    complaint_message = firereport.Message or ""
    try:
        import re

        m = re.match(
            r"^\[Category:\s*(?P<cat>.*?)\]\s*\[Title:\s*(?P<title>.*?)\]\s*(?:\r?\n)?(?P<body>[\s\S]*)$",
            complaint_message.strip(),
        )
        if m:
            complaint_category = (m.group("cat") or "").strip()
            complaint_title = (m.group("title") or "").strip()
            complaint_message = (m.group("body") or "").strip()
    except Exception:
        pass
    report1 = Firetequesthistory.objects.filter(firereport=firereport)
    reportcount = Firetequesthistory.objects.filter(firereport=firereport).count()
    return render(request, 'viewStatusDetails.html', locals())


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def admin_login(request):
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if request.method == 'POST':
        u = request.POST['uname']
        p = request.POST['password']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    return render(request, 'admin_login.html', locals())


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def dashboard(request):
    base = Firereport.objects.all()
    if not request.user.is_superuser:
        base = _firereport_qs_scoped_for_staff(base, request.user)
    totalnewequest = base.filter(Q(Status__isnull=True) | Q(Status="Pending")).count()
    totalAssign = base.filter(Status='Assigned').count()
    totalontheway = base.filter(Status='In Progress').count()
    totalworkprocess = base.filter(Status='Work in Progress').count()
    totalreqcomplete = base.filter(Status='Request Completed').count()
    totalfire = base.count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    return render(request, 'admin/dashboard.html', locals())


@login_required(login_url='user-login')
def dashboard_staff(request):
    base = Firereport.objects.all()
    if not request.user.is_superuser:
        base = _firereport_qs_scoped_for_staff(base, request.user)
    totalnewrequest = base.filter(Q(Status__isnull=True) | Q(Status="Pending")).count()
    totalAssign = base.filter(Status='Assigned').count()
    totalontheway = base.filter(Status='In Progress').count()
    totalworkprocess = base.filter(Status='Work in Progress').count()
    totalreqcomplete = base.filter(Status='Request Completed').count()
    totalfire = base.count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    return render(request, 'admin/dashboard_staff.html', locals())




@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def addTeam(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if request.method == "POST":
        teamName = request.POST['teamName']
        teamLeaderName = request.POST['teamLeaderName']
        teamLeadMobno = request.POST['teamLeadMobno']
        teamMembers = request.POST['teamMembers']

        try:
            Teams.objects.create(teamName=teamName, teamLeaderName=teamLeaderName, teamLeadMobno=teamLeadMobno, teamMembers=teamMembers)
            error = "no"
        except:
            error = "yes"
    return render(request, 'admin/addTeam.html', locals())



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def task(request):
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    User = get_user_model()
    # all_users = User.objects.filter(is_staff=True)
    all_users = User.objects.filter(is_staff=1, is_active=1)
    customer = Customer.objects.all()
    all_profiles = Profile.objects.all()
    departments = Profile._meta.get_field('department').choices
    companies = Customer.objects.values('Comp_name').distinct()

    if request.method == "POST":

        Teamid = request.POST.get('AssignToID')
        AssignTo = request.POST.get('AssignTo')
        task_type = (request.POST.get('task_type') or 'complaint').strip().lower()
        is_service_task = task_type == 'service'
        Status = "Assigned"
        team1 = User.objects.get(id=Teamid)


        FullName = request.POST['comp_name']
        MobileNumber = request.POST['phone']
        Location = request.POST['city']
        Message = request.POST['Message']
        Account_id = request.POST['new_customer_id']
        AssignBy = request.user.id
        now = now_ist()
        # AssignedTime = now.strftime("%d/%m/%Y %H:%M:%S")
        AssignedTime = now
        UpdationDate = now

        try:
            if is_service_task:
                service_req = ServiceRequest.objects.create(
                    FullName=FullName,
                    MobileNumber=MobileNumber,
                    Location=Location,
                    Message=Message,
                    AssignTo=team1,
                    Status=Status,
                    AssignedTime=AssignedTime,
                    Account_id=Account_id,
                    AssignBy=AssignBy,
                    UpdationDate=UpdationDate,
                )
                ServiceRequestHistory.objects.create(
                    service_request=service_req,
                    status=Status,
                    remark="Created from New Task",
                    AssignTo=team1,
                    AssignBy=AssignBy,
                )
            else:
                Firereport.objects.create(FullName=FullName, MobileNumber=MobileNumber, Location=Location,
                                          Message=Message, AssignTo=team1, Status=Status, AssignedTime=AssignedTime,
                                          Account_id=Account_id, AssignBy=AssignBy, UpdationDate=UpdationDate)
            error = "no"
        except Exception as e:
            error = "yes"
        return render(request, 'admin/task.html', {'error': error})

    return render(request, 'admin/task.html', {
        'error': error,
        'count1': count1,
        'notification1': notification1,
        'all_users': all_users,
        'customer': customer,
        'all_profiles': all_profiles,
        'departments': departments,
        'companies': companies,
    })


@login_required(login_url='user-login')
def serviceRequestsInProcess(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    qs = ServiceRequest.objects.filter(Status='In Process').order_by('-id')
    if not request.user.is_superuser:
        qs = _service_qs_scoped_for_staff(qs, request.user)
    return render(request, 'admin/service_in_process.html', {
        'service_requests': qs,
        'count1': count1,
        'notification1': notification1,
    })


@login_required(login_url='user-login')
def serviceRequestsAssigned(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    qs = ServiceRequest.objects.filter(Status='Assigned').order_by('-id')
    if not request.user.is_superuser:
        qs = _service_qs_scoped_for_staff(qs, request.user)
    return render(request, 'admin/service_assigned.html', {
        'service_requests': qs,
        'count1': count1,
        'notification1': notification1,
    })


@login_required(login_url='user-login')
def serviceMarkInProcess(request, pid):
    if request.method != 'POST':
        return redirect('firereport-service-assigned')
    req = get_object_or_404(ServiceRequest, pk=pid)
    if not request.user.is_superuser and req.AssignTo_id != request.user.id:
        return HttpResponse("You are not authorized to update this service request.", status=403)
    if req.Status != 'Assigned':
        return redirect('firereport-service-viewRequestDetails', pid=pid)

    now = now_ist()
    req.Status = 'In Process'
    req.UpdationDate = now
    req.save()
    ServiceRequestHistory.objects.create(
        service_request=req,
        status='In Process',
        remark='Service work approved',
        AssignTo=req.AssignTo,
        AssignBy=request.user.id,
    )
    return redirect('firereport-service-in-process')


@login_required(login_url='user-login')
def serviceRequestsCompleted(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    qs = ServiceRequest.objects.filter(Status='Completed').order_by('-id')
    if not request.user.is_superuser:
        qs = _service_qs_scoped_for_staff(qs, request.user)
    return render(request, 'admin/service_completed.html', {
        'service_requests': qs,
        'count1': count1,
        'notification1': notification1,
    })


@login_required(login_url='user-login')
def serviceMarkCompleted(request, pid):
    if request.method != 'POST':
        return redirect('firereport-service-in-process')
    req = get_object_or_404(ServiceRequest, pk=pid)
    if not request.user.is_superuser and req.AssignTo_id != request.user.id:
        return HttpResponse("You are not authorized to update this service request.", status=403)
    remark_lines = []
    selected_remark_ids = request.POST.getlist('selected_remark_ids')
    for rid in selected_remark_ids:
        try:
            rm = ServiceRemarkMaster.objects.filter(id=int(rid), is_active=True).first()
            if rm:
                remark_lines.append(rm.remark.strip())
        except Exception:
            continue
    manual_remark = (request.POST.get('remark') or '').strip()
    if manual_remark:
        remark_lines.append(manual_remark)
    new_remark = (request.POST.get('new_remark') or '').strip()
    if new_remark:
        rm, _ = ServiceRemarkMaster.objects.get_or_create(remark=new_remark[:250], defaults={'is_active': True})
        if rm.remark not in remark_lines:
            remark_lines.append(rm.remark)
    combined_remark = " | ".join([r for r in remark_lines if r])[:250]
    if not combined_remark:
        messages.error(request, "Please select or add at least one remark before submitting the service report.")
        return redirect('firereport-service-viewRequestDetails', pid=pid)

    phase_type = (request.POST.get('phase_type') or 'single').strip().lower()
    required_fields = [
        'report_date', 'report_time',
        'acdb_pn', 'acdb_ne', 'acdb_pn2',
        'generation_today', 'generation_yesterday', 'generation_monthly', 'generation_yearly',
        'import_units', 'export_units', 'meter_generation_units',
        'consumer_sign_name', 'engg_sign_name', 'engg_id', 'engg_sign_date',
    ]
    missing_labels = []
    for field_name in required_fields:
        if not (request.POST.get(field_name) or '').strip():
            missing_labels.append(field_name.replace('_', ' ').title())

    if phase_type == 'three':
        ac_required = ['ac_voltage_rn', 'ac_voltage_yn', 'ac_voltage_bn', 'ac_current_r', 'ac_current_y', 'ac_current_b']
    else:
        ac_required = ['ac_voltage_rn', 'ac_current_r']
    for field_name in ac_required:
        if not (request.POST.get(field_name) or '').strip():
            missing_labels.append(field_name.replace('_', ' ').title())

    if missing_labels:
        messages.error(request, "Service report not saved. Please fill all required textbox values.")
        return redirect('firereport-service-viewRequestDetails', pid=pid)

    dc_rows = []
    mppts = request.POST.getlist('dc_mppt[]')
    strings = request.POST.getlist('dc_string[]')
    voltages = request.POST.getlist('dc_voltage[]')
    currents = request.POST.getlist('dc_current[]')
    max_len = max(len(mppts), len(strings), len(voltages), len(currents), 1)
    for i in range(max_len):
        row = {
            'mppt': mppts[i].strip() if i < len(mppts) and mppts[i] else '',
            'string': strings[i].strip() if i < len(strings) and strings[i] else '',
            'voltage': voltages[i].strip() if i < len(voltages) and voltages[i] else '',
            'current': currents[i].strip() if i < len(currents) and currents[i] else '',
        }
        if any(row.values()):
            dc_rows.append(row)

    existing_report = ServiceReport.objects.filter(service_request=req).first()
    customer = Customer.objects.filter(phone=req.MobileNumber).order_by('-Cust_id').first()
    if not customer:
        customer = Customer.objects.filter(Comp_name__icontains=req.FullName).order_by('-Cust_id').first()

    def _capacity_text(qs):
        rows = qs.values('wattage').annotate(total=Count('id')).order_by('wattage')
        parts = []
        for row in rows:
            wattage = (row.get('wattage') or '').strip()
            if not wattage:
                continue
            parts.append(f"{wattage} kW ({row.get('total', 0)} Nos.)")
        return ", ".join(parts)

    solar_capacity_default = ''
    inverter_capacity_default = ''
    if customer and BarcodeImage:
        consumer_user_id = customer.new_customer_id
        company_name = (customer.Comp_name or '').strip()

        solar_qs = BarcodeImage.objects.none()
        if consumer_user_id:
            solar_qs = BarcodeImage.objects.filter(AssignTo_id=consumer_user_id)
        if not solar_qs.exists() and company_name:
            solar_qs = BarcodeImage.objects.filter(company_name=company_name)
        solar_qs = solar_qs.filter(Q(product_name__icontains='solar') | Q(product_name__icontains='panel'))
        solar_capacity_default = _capacity_text(solar_qs)

        inverter_qs = BarcodeImage.objects.none()
        if consumer_user_id:
            inverter_qs = BarcodeImage.objects.filter(AssignTo_id=consumer_user_id)
        if not inverter_qs.exists() and company_name:
            inverter_qs = BarcodeImage.objects.filter(company_name=company_name)
        inverter_qs = inverter_qs.filter(product_name__icontains='inverter')
        inverter_capacity_default = _capacity_text(inverter_qs)

    if not inverter_capacity_default and customer and InverterImage:
        consumer_user_id = customer.new_customer_id
        company_name = (customer.Comp_name or '').strip()
        inverter_img_qs = InverterImage.objects.none()
        if consumer_user_id:
            inverter_img_qs = InverterImage.objects.filter(AssignTo_id=consumer_user_id)
        if not inverter_img_qs.exists() and company_name:
            inverter_img_qs = InverterImage.objects.filter(company_name=company_name)
        inverter_capacity_default = _capacity_text(inverter_img_qs)

    def _pick(field_name, fallback=''):
        v = (request.POST.get(field_name) or '').strip()
        if v:
            return v
        if existing_report:
            prev = getattr(existing_report, field_name, None)
            if prev is not None and str(prev).strip():
                return str(prev).strip()
        return str(fallback).strip() if fallback is not None else ''

    ServiceReport.objects.update_or_create(
        service_request=req,
        defaults={
            'report_date': request.POST.get('report_date') or None,
            'report_time': request.POST.get('report_time') or None,
            'consumer_name': _pick('consumer_name', req.FullName),
            'consumer_address': _pick('consumer_address', customer.Address if customer else ''),
            'consumer_phone': _pick('consumer_phone', req.MobileNumber),
            'plant_capacity': _pick('plant_capacity', customer.Plant_Capacity if customer else ''),
            'load_sanction': _pick('load_sanction', customer.loadsancution if customer else ''),
            'phase_type': request.POST.get('phase_type', 'single').strip() or 'single',
            'solar_module_make': _pick('solar_module_make', customer.solar_comp if customer else ''),
            'solar_module_quantity': _pick('solar_module_quantity', customer.qunt_solar if customer else ''),
            'solar_module_capacity': _pick('solar_module_capacity', solar_capacity_default),
            'inverter_make': _pick('inverter_make', customer.UPSC if customer else ''),
            'inverter_quantity': _pick('inverter_quantity', customer.qunt_inv if customer else ''),
            'inverter_capacity': _pick('inverter_capacity', inverter_capacity_default),
            'ac_voltage_rn': request.POST.get('ac_voltage_rn', '').strip(),
            'ac_voltage_yn': request.POST.get('ac_voltage_yn', '').strip(),
            'ac_voltage_bn': request.POST.get('ac_voltage_bn', '').strip(),
            'ac_current_r': request.POST.get('ac_current_r', '').strip(),
            'ac_current_y': request.POST.get('ac_current_y', '').strip(),
            'ac_current_b': request.POST.get('ac_current_b', '').strip(),
            'dc_rows_json': json.dumps(dc_rows),
            'acdb_pn': request.POST.get('acdb_pn', '').strip(),
            'acdb_ne': request.POST.get('acdb_ne', '').strip(),
            'acdb_pn2': request.POST.get('acdb_pn2', '').strip(),
            'generation_today': request.POST.get('generation_today', '').strip(),
            'generation_yesterday': request.POST.get('generation_yesterday', '').strip(),
            'generation_monthly': request.POST.get('generation_monthly', '').strip(),
            'generation_yearly': request.POST.get('generation_yearly', '').strip(),
            'remarks_text': "\n".join(remark_lines).strip(),
            'import_units': request.POST.get('import_units', '').strip(),
            'export_units': request.POST.get('export_units', '').strip(),
            'meter_generation_units': request.POST.get('meter_generation_units', '').strip(),
            'consumer_sign_name': request.POST.get('consumer_sign_name', '').strip(),
            'engg_sign_name': request.POST.get('engg_sign_name', '').strip(),
            'engg_id': request.POST.get('engg_id', '').strip(),
            'engg_sign_date': request.POST.get('engg_sign_date') or None,
        }
    )

    now = now_ist()
    req.Status = 'Completed'
    req.complete_date = now
    req.UpdationDate = now
    req.save()
    ServiceRequestHistory.objects.create(
        service_request=req,
        status='Completed',
        remark=combined_remark,
        AssignTo=req.AssignTo,
        AssignBy=request.user.id,
    )
    return redirect('firereport-service-completed')


@login_required(login_url='user-login')
def serviceReportPdf(request, pid):
    req = ServiceRequest.objects.filter(pk=pid).first()
    if not req:
        messages.error(request, f"Service request #{pid} not found.")
        return redirect('firereport-service-completed')
    auth_err = _assert_service_staff_access(request, req)
    if auth_err:
        return auth_err
    report = ServiceReport.objects.filter(service_request=req).first()
    if not report:
        messages.error(request, "Service report data not found for this request.")
        return redirect('firereport-service-completed')

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24,
    )
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontName = "Helvetica"
    normal.fontSize = 9
    heading = ParagraphStyle("heading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, alignment=1)
    section = ParagraphStyle("section", parent=normal, fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#1f4e79"))

    elements = []

    company_name = getattr(settings, "COMPANY_NAME", "DB Solar")
    company_address = getattr(settings, "COMPANY_ADDRESS", "Company Address")
    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "db_logo_200.png")

    logo = ""
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=42, height=42)
        except Exception:
            logo = ""

    header_data = [[logo, Paragraph(f"<b>{company_name}</b><br/>{company_address}", normal), Paragraph(f"<b>SRV/{req.id}</b>", normal)]]
    header_table = Table(header_data, colWidths=[52, 395, 90])
    header_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("SERVICE REPORT FORM", heading))
    elements.append(Spacer(1, 8))

    def section_table(title, rows, col_widths=(140, 145, 140, 112)):
        elements.append(Paragraph(title, section))
        data = []
        for r in rows:
            data.append([Paragraph(f"<b>{r[0]}</b>", normal), Paragraph(str(r[1] or "-"), normal),
                         Paragraph(f"<b>{r[2]}</b>", normal), Paragraph(str(r[3] or "-"), normal)])
        t = Table(data, colWidths=list(col_widths))
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 8))

    def section_header_value_table(title, headers, values, col_widths):
        elements.append(Paragraph(title, section))
        table_data = [headers, values]
        t = Table(table_data, colWidths=list(col_widths))
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9ecef")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 8))

    section_table("Consumer Details", [
        ("Consumer Name", req.FullName, "Phone", req.MobileNumber),
        ("Address/Location", req.Location, "Report Date", report.report_date),
        ("Service Message", req.Message, "Report Time", report.report_time),
    ])

    plant_capacity_val = f"{report.plant_capacity} kW" if report.plant_capacity else "-"
    load_sanction_val = f"{report.load_sanction} kW" if report.load_sanction else "-"
    solar_capacity_val = f"{report.solar_module_capacity} kW" if report.solar_module_capacity else "-"
    inverter_capacity_val = f"{report.inverter_capacity} kW" if report.inverter_capacity else "-"
    solar_qty_val = f"{report.solar_module_quantity} Nos." if report.solar_module_quantity else "-"
    inverter_qty_val = f"{report.inverter_quantity} Nos." if report.inverter_quantity else "-"

    section_table("Project Details", [
        ("Plant Capacity", plant_capacity_val, "Load Sanction", load_sanction_val),
        # Solar details shown vertically (one below another) in left column.
        ("Solar Module Make", report.solar_module_make, "Inverter Make", report.inverter_make),
        ("Solar Quantity", solar_qty_val, "Inverter Quantity", inverter_qty_val),
        ("Solar Capacity", solar_capacity_val, "Inverter Capacity", inverter_capacity_val),
    ])

    is_single_phase = (report.phase_type or '').lower() == 'single'
    if is_single_phase:
        ac_voltage_val = report.ac_voltage_rn or '-'
        ac_current_val = report.ac_current_r or '-'
        ac_voltage_label = "Voltage"
        ac_current_label = "Current"
    else:
        ac_voltage_val = f"{report.ac_voltage_rn or '-'} / {report.ac_voltage_yn or '-'} / {report.ac_voltage_bn or '-'}"
        ac_current_val = f"{report.ac_current_r or '-'} / {report.ac_current_y or '-'} / {report.ac_current_b or '-'}"
        ac_voltage_label = "Voltage RN/YN/BN"
        ac_current_label = "Current R/Y/B"

    section_table("AC Side Details", [
        (ac_voltage_label, ac_voltage_val, ac_current_label, ac_current_val),
    ])

    try:
        dc_rows = json.loads(report.dc_rows_json) if report.dc_rows_json else []
    except Exception:
        dc_rows = []
    if not dc_rows:
        dc_rows = [{"mppt": "-", "string": "-", "voltage": "-", "current": "-"}]
    elements.append(Paragraph("DC Side Details", section))
    dc_data = [["MPPT", "String", "Voltage", "Current"]]
    for row in dc_rows:
        dc_data.append([row.get("mppt") or "-", row.get("string") or "-", row.get("voltage") or "-", row.get("current") or "-"])
    dc_table = Table(dc_data, colWidths=[120, 120, 120, 177])
    dc_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9ecef")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(dc_table)
    elements.append(Spacer(1, 8))

    section_header_value_table(
        "ACDB Box",
        ["PN", "NE", "PE"],
        [report.acdb_pn or "-", report.acdb_ne or "-", report.acdb_pn2 or "-"],
        [179, 179, 179],
    )

    section_header_value_table(
        "Generation",
        ["Today", "Yesterday", "Monthly", "Yearly"],
        [
            f"{report.generation_today} Unit" if report.generation_today else "-",
            f"{report.generation_yesterday} Unit" if report.generation_yesterday else "-",
            f"{report.generation_monthly} Unit" if report.generation_monthly else "-",
            f"{report.generation_yearly} Unit" if report.generation_yearly else "-",
        ],
        [134, 134, 134, 134],
    )

    section_header_value_table(
        "Import & Export Details",
        ["Import", "Export", "Generation Meter"],
        [
            f"{report.import_units} Unit" if report.import_units else "-",
            f"{report.export_units} Unit" if report.export_units else "-",
            f"{report.meter_generation_units} Unit" if report.meter_generation_units else "-",
        ],
        [179, 179, 179],
    )

    elements.append(Paragraph("Remarks", section))
    remarks = (report.remarks_text or "").splitlines() or ["-"]
    remarks_data = [[Paragraph("<b>Selected Remarks</b>", normal)]]
    for rem in remarks:
        remarks_data.append([Paragraph(f"- {rem}", normal)])
    remarks_table = Table(remarks_data, colWidths=[537])
    remarks_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9ecef")),
    ]))
    elements.append(remarks_table)
    elements.append(Spacer(1, 8))

    section_table("Signatures", [
        ("Consumer Sign Name", report.consumer_sign_name, "Engineer Sign Name", report.engg_sign_name),
        ("Engineer ID", report.engg_id, "Sign Date", report.engg_sign_date),
    ])

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"service_report_{req.id}.pdf\"'
    return response


@login_required(login_url='user-login')
def serviceViewRequestDetails(request, pid):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    service_request = get_object_or_404(ServiceRequest, pk=pid)
    auth_err = _assert_service_staff_access(request, service_request)
    if auth_err:
        return auth_err

    customer = Customer.objects.filter(phone=service_request.MobileNumber).order_by('-Cust_id').first()
    if not customer:
        customer = Customer.objects.filter(Comp_name__icontains=service_request.FullName).order_by('-Cust_id').first()

    def _capacity_text(qs):
        rows = qs.values('wattage').annotate(total=Count('id')).order_by('wattage')
        parts = []
        for row in rows:
            wattage = (row.get('wattage') or '').strip()
            if not wattage:
                continue
            parts.append(f"{wattage} kW ({row.get('total', 0)} Nos.)")
        return ", ".join(parts)

    def _serial_text(qs):
        serials = []
        seen = set()
        for code in qs.values_list('barcode_data', flat=True):
            code = (code or '').strip()
            if not code:
                continue
            if code in seen:
                continue
            seen.add(code)
            serials.append(code)
        return ", ".join(serials)

    solar_capacity_default = ''
    inverter_capacity_default = ''
    inverter_serial_default = ''
    if customer:
        consumer_user_id = customer.new_customer_id
        company_name = (customer.Comp_name or '').strip()

        if BarcodeImage:
            solar_qs = BarcodeImage.objects.none()
            if consumer_user_id:
                # Primary mapping: User -> Customer(new_customer) -> Barcode(AssignTo)
                solar_qs = BarcodeImage.objects.filter(AssignTo_id=consumer_user_id)
            if not solar_qs.exists() and company_name:
                # Fallback for legacy rows where user linkage might be missing
                solar_qs = BarcodeImage.objects.filter(company_name=company_name)
            # Only solar panel items from BarcodeImage.product_name
            solar_qs = solar_qs.filter(Q(product_name__icontains='solar') | Q(product_name__icontains='panel'))
            solar_capacity_default = _capacity_text(solar_qs)

            inverter_qs = BarcodeImage.objects.none()
            if consumer_user_id:
                inverter_qs = BarcodeImage.objects.filter(AssignTo_id=consumer_user_id)
            if not inverter_qs.exists() and company_name:
                inverter_qs = BarcodeImage.objects.filter(company_name=company_name)
            # Only inverter items from BarcodeImage.product_name
            inverter_qs = inverter_qs.filter(product_name__icontains='inverter')
            inverter_capacity_default = _capacity_text(inverter_qs)
            inverter_serial_default = _serial_text(inverter_qs)

        if not inverter_capacity_default and InverterImage:
            inverter_img_qs = InverterImage.objects.none()
            if consumer_user_id:
                inverter_img_qs = InverterImage.objects.filter(AssignTo_id=consumer_user_id)
            if not inverter_img_qs.exists() and company_name:
                inverter_img_qs = InverterImage.objects.filter(company_name=company_name)
            inverter_capacity_default = _capacity_text(inverter_img_qs)
            inverter_serial_default = _serial_text(inverter_img_qs)

    service_report = ServiceReport.objects.filter(service_request=service_request).first()
    dc_rows = []
    if service_report and service_report.dc_rows_json:
        try:
            dc_rows = json.loads(service_report.dc_rows_json)
        except Exception:
            dc_rows = []
    if not dc_rows:
        dc_rows = [{'mppt': '', 'string': '', 'voltage': '', 'current': ''}]

    if not service_report:
        now_dt = now_ist()
        report_date_default = now_dt.date().isoformat()
        report_time_default = now_dt.strftime('%H:%M')
    else:
        report_date_default = service_report.report_date.isoformat() if service_report.report_date else ''
        report_time_default = service_report.report_time.strftime('%H:%M') if service_report.report_time else ''

    remark_options = ServiceRemarkMaster.objects.filter(is_active=True).order_by('remark')
    service_history = ServiceRequestHistory.objects.filter(service_request=service_request).order_by('-postingDate')
    selected_remark_texts = set()
    if service_report and service_report.remarks_text:
        selected_remark_texts = {x.strip() for x in service_report.remarks_text.splitlines() if x.strip()}

    plant_capacity_default = str(customer.Plant_Capacity) if customer and customer.Plant_Capacity is not None else ''
    load_sanction_default = str(customer.loadsancution) if customer and customer.loadsancution is not None else ''
    solar_make_default = customer.solar_comp if customer and customer.solar_comp else ''
    inverter_make_default = customer.UPSC if customer and customer.UPSC else ''
    solar_qty_default = str(customer.qunt_solar) if customer and customer.qunt_solar is not None else ''
    inverter_qty_default = str(customer.qunt_inv) if customer and customer.qunt_inv is not None else ''

    return render(request, 'admin/service_viewRequestDetails.html', {
        'count1': count1,
        'notification1': notification1,
        'service_request': service_request,
        'service_history': service_history,
        'customer': customer,
        'service_report': service_report,
        'dc_rows': dc_rows,
        'remark_options': remark_options,
        'selected_remark_texts': selected_remark_texts,
        'report_date_default': report_date_default,
        'report_time_default': report_time_default,
        'plant_capacity_default': plant_capacity_default,
        'load_sanction_default': load_sanction_default,
        'solar_make_default': solar_make_default,
        'inverter_make_default': inverter_make_default,
        'solar_capacity_default': solar_capacity_default,
        'inverter_capacity_default': inverter_capacity_default,
        'solar_qty_default': solar_qty_default,
        'inverter_qty_default': inverter_qty_default,
        'inverter_serial_default': inverter_serial_default,
    })


@login_required(login_url='user-login')
def serviceAddRemarkApi(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)
    remark_text = (request.POST.get('remark') or '').strip()
    if not remark_text:
        return JsonResponse({'ok': False, 'error': 'Remark text is required'}, status=400)
    remark_obj, _ = ServiceRemarkMaster.objects.get_or_create(
        remark=remark_text[:250],
        defaults={'is_active': True}
    )
    if not remark_obj.is_active:
        remark_obj.is_active = True
        remark_obj.save(update_fields=['is_active'])
    return JsonResponse({'ok': True, 'id': remark_obj.id, 'remark': remark_obj.remark})


# def get_customer_details(request):
#     if request.method == 'GET':
#         comp_name = request.GET.get('comp_name')
#         if comp_name:
#             customer = Customer.objects.filter(Comp_name=comp_name).first()
#             if customer:
#                 data = {
#                     'phone': customer.phone,
#                     'Address': customer.Address,
#                     'City': customer.City,
#                     'Plant_Capacity': customer.Plant_Capacity,
#                     'new_customer_id': customer.new_customer_id,  # Add the new field here
#                     # Add other fields here
#                 }
#                 return HttpResponse(json.dumps(data), content_type='application/json')
#     return HttpResponse(json.dumps({}), content_type='application/json')
#
from django.http import JsonResponse

def get_customer_details(request):
    if request.method == 'GET':
        comp_name = request.GET.get('comp_name')

        if comp_name:
            customer = Customer.objects.filter(Comp_name=comp_name).first()

            if customer:
                data = {
                    'phone': customer.phone,
                    'Address': customer.Address,
                    'City': customer.City,
                    'Plant_Capacity': float(customer.Plant_Capacity) if customer.Plant_Capacity else 0,
                    'new_customer_id': customer.new_customer_id,
                }

                return JsonResponse(data)

    return JsonResponse({})

def get_profile_data(request):
    user_id = request.POST.get('user_id')
    try:
        profile = Profile.objects.get(customer_id=user_id)
        data = {
            'city': profile.address,
            'phone': profile.phone,
        }
        return JsonResponse(data)
    except Profile.DoesNotExist:
        return JsonResponse({})


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def manageTeam(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    teams = Teams.objects.all()
    return render(request, 'admin/manageTeam.html', locals())


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def editTeam(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    teams = Teams.objects.get(id=pid)
    error =""
    if request.method == "POST":
        teamName = request.POST['teamName']
        teamLeaderName = request.POST['teamLeaderName']
        teamLeadMobno = request.POST['teamLeadMobno']
        teamMembers = request.POST['teamMembers']

        teams.teamName = teamName
        teams.teamLeaderName = teamLeaderName
        teams.teamLeadMobno = teamLeadMobno
        teams.teamMembers = teamMembers

        try:
            teams.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'admin/editTeam.html', locals())


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def deleteTeam(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    teams = Teams.objects.get(id=pid)
    teams.delete()
    return redirect('manageTeam')


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def newRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    # today = now_ist()
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST
    start_date, end_date = None, None


    # Get the start and end date for custom range from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Determine the caption text based on the selected_option
    if filter_option == "All":
        caption_text = "Display All Days View"
        caption_text1 = "Up To Date"
    elif filter_option == "Today":
        # caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Today View"
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        caption_text1 = "Today"
    elif filter_option == "Last7Days":
        start_date = today - timezone.timedelta(days=7)
        end_date = today
        caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 7 Days View"
        caption_text1 = "Last 7 Days"
    elif filter_option == "Last30Days":
        start_date = today - timezone.timedelta(days=30)
        end_date = today
        caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 30 Days View"
        caption_text1 = "Last 30 Days"
    elif filter_option == "ThisMonth":
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display This Month View"
        caption_text1 = "This Month"
    elif filter_option == "Custom":
        # caption_text = "Display Custome Range View  ('start_date')strtime('start_date')"
        caption_text = "Display Custome Range View"
        caption_text1 = "Custome Range"
    else:
        caption_text = "The option is not selected so all Record Show"  # Add a default caption for unknown options
        caption_text1 = ""


    # Define a variable to store the filtered data
    filtered_firereport = Firereport.objects.filter(Q(Status__isnull=True) | Q(Status="Pending"))
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST

    if filter_option == 'Today':
        filtered_firereport = filtered_firereport.filter(Postingdate__date=today.date())
    elif filter_option == 'Last7Days':
        last_week = today - timezone.timedelta(days=7)
        filtered_firereport = filtered_firereport.filter(Postingdate__date__gte=last_week.date())
    elif filter_option == 'Last30Days':
        last_month = today - timezone.timedelta(days=30)
        filtered_firereport = filtered_firereport.filter(Postingdate__date__gte=last_month.date())
    elif filter_option == 'ThisMonth':
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        filtered_firereport = filtered_firereport.filter(Postingdate__date__gte=current_month.date())

    # Handle the custom range filter
    if filter_option == 'Custom' and start_date and end_date:
        filtered_firereport = filtered_firereport.filter(Postingdate__date__range=(start_date, end_date))

    if not request.user.is_superuser:
        filtered_firereport = _firereport_qs_scoped_for_staff(filtered_firereport, request.user)

    # Parse message format to extract Category/Title for display
    import re

    msg_re = re.compile(
        r"^\[Category:\s*(?P<cat>.*?)\]\s*\[Title:\s*(?P<title>.*?)\]\s*(?:\r?\n)?(?P<body>[\s\S]*)$"
    )

    for fr in filtered_firereport:
        raw = fr.Message or ""
        cat = ""
        title = ""
        body = raw
        m = msg_re.match(raw.strip())
        if m:
            cat = (m.group("cat") or "").strip()
            title = (m.group("title") or "").strip()
            body = (m.group("body") or "").strip()
        fr.complaint_category = cat
        fr.complaint_title = title
        fr.complaint_body = body if body else raw

    return render(request, 'admin/newRequest.html',
                  {'filtered_firereport': filtered_firereport, 'filter_option': filter_option, 'count1': count1,
                   'notification1': notification1, 'caption_text': caption_text, 'caption_text1': caption_text1,})


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def assignRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    # today = now_ist()
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST
    start_date, end_date = None, None


    # Get the start and end date for custom range from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Determine the caption text based on the selected_option
    if filter_option == "All":
        caption_text = "Display All Days View"
        caption_text1 = "Up To Date"
    elif filter_option == "Today":
        # caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Today View"
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        caption_text1 = "Today"
    elif filter_option == "Last7Days":
        start_date = today - timezone.timedelta(days=7)
        end_date = today
        caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 7 Days View"
        caption_text1 = "Last 7 Days"
    elif filter_option == "Last30Days":
        start_date = today - timezone.timedelta(days=30)
        end_date = today
        caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 30 Days View"
        caption_text1 = "Last 30 Days"
    elif filter_option == "ThisMonth":
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display This Month View"
        caption_text1 = "This Month"
    elif filter_option == "Custom":
        # caption_text = "Display Custome Range View  ('start_date')strtime('start_date')"
        caption_text = "Display Custome Range View"
        caption_text1 = "Custome Range"
    else:
        caption_text = "The option is not selected so all Record Show"  # Add a default caption for unknown options
        caption_text1 = ""

    # Define a variable to store the filtered data
    filtered_firereport = Firereport.objects.filter(Status='Assigned')
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST

    if filter_option == 'Today':
        filtered_firereport = filtered_firereport.filter(AssignedTime__date=today.date())
    elif filter_option == 'Last7Days':
        last_week = today - timezone.timedelta(days=7)
        filtered_firereport = filtered_firereport.filter(AssignedTime__date__gte=last_week.date())
    elif filter_option == 'Last30Days':
        last_month = today - timezone.timedelta(days=30)
        filtered_firereport = filtered_firereport.filter(AssignedTime__date__gte=last_month.date())
    elif filter_option == 'ThisMonth':
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        filtered_firereport = filtered_firereport.filter(AssignedTime__date__gte=current_month.date())

    # Handle the custom range filter
    if filter_option == 'Custom' and start_date and end_date:
        filtered_firereport = filtered_firereport.filter(AssignedTime__date__range=(start_date, end_date))

    if not request.user.is_superuser:
        filtered_firereport = _firereport_qs_scoped_for_staff(filtered_firereport, request.user)
    filtered_firereport = _dedupe_firereport_rows(filtered_firereport)
    filtered_firereport = sorted(
        filtered_firereport,
        key=lambda r: (
            getattr(r, "Postingdate", None) or getattr(r, "UpdationDate", None),
            getattr(r, "id", 0),
        ),
        reverse=True,
    )

    return render(request, 'admin/assignRequest.html',
                  {'filtered_firereport': filtered_firereport, 'filter_option': filter_option, 'count1': count1,
                   'notification1': notification1, 'caption_text': caption_text, 'caption_text1': caption_text1,})


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def reassignRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    # today = now_ist()
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST
    start_date, end_date = None, None


    # Get the start and end date for custom range from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Determine the caption text based on the selected_option
    if filter_option == "All":
        caption_text = "Display All Days View"
        caption_text1 = "Up To Date"
    elif filter_option == "Today":
        # caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Today View"
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        caption_text1 = "Today"
    elif filter_option == "Last7Days":
        start_date = today - timezone.timedelta(days=7)
        end_date = today
        caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 7 Days View"
        caption_text1 = "Last 7 Days"
    elif filter_option == "Last30Days":
        start_date = today - timezone.timedelta(days=30)
        end_date = today
        caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 30 Days View"
        caption_text1 = "Last 30 Days"
    elif filter_option == "ThisMonth":
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display This Month View"
        caption_text1 = "This Month"
    elif filter_option == "Custom":
        # caption_text = "Display Custome Range View  ('start_date')strtime('start_date')"
        caption_text = "Display Custome Range View"
        caption_text1 = "Custome Range"
    else:
        caption_text = "The option is not selected so all Record Show"  # Add a default caption for unknown options
        caption_text1 = ""


    # Define a variable to store the filtered data
    filtered_firereport = Firereport.objects.filter(Status='Assigned')
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST

    if filter_option == 'Today':
        filtered_firereport = filtered_firereport.filter(AssignedTime__date=today.date())
    elif filter_option == 'Last7Days':
        last_week = today - timezone.timedelta(days=7)
        filtered_firereport = filtered_firereport.filter(AssignedTime__date__gte=last_week.date())
    elif filter_option == 'Last30Days':
        last_month = today - timezone.timedelta(days=30)
        filtered_firereport = filtered_firereport.filter(AssignedTime__date__gte=last_month.date())
    elif filter_option == 'ThisMonth':
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        filtered_firereport = filtered_firereport.filter(AssignedTime__date__gte=current_month.date())

    # Handle the custom range filter
    if filter_option == 'Custom' and start_date and end_date:
        filtered_firereport = filtered_firereport.filter(AssignedTime__date__range=(start_date, end_date))

    if not request.user.is_superuser:
        filtered_firereport = _firereport_qs_scoped_for_staff(filtered_firereport, request.user)

    return render(request, 'admin/re_assignRequest.html',
                  {'filtered_firereport': filtered_firereport, 'filter_option': filter_option, 'count1': count1,
                   'notification1': notification1, 'caption_text': caption_text, 'caption_text1': caption_text1,})


from django.utils import timezone
from datetime import timedelta


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta


from django.utils import timezone

from datetime import datetime
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse

from django.db.models import Q
from django.utils import timezone


@login_required(login_url='user-login')
def teamontheway(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    # today = now_ist()
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST
    start_date, end_date = None, None


    # Get the start and end date for custom range from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Determine the caption text based on the selected_option
    if filter_option == "All":
        caption_text = "Display All Days View"
        caption_text1 = "Up To Date"
    elif filter_option == "Today":
        # caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Today View"
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        caption_text1 = "Today"
    elif filter_option == "Last7Days":
        start_date = today - timezone.timedelta(days=7)
        end_date = today
        caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 7 Days View"
        caption_text1 = "Last 7 Days"
    elif filter_option == "Last30Days":
        start_date = today - timezone.timedelta(days=30)
        end_date = today
        caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 30 Days View"
        caption_text1 = "Last 30 Days"
    elif filter_option == "ThisMonth":
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display This Month View"
        caption_text1 = "This Month"
    elif filter_option == "Custom":
        # caption_text = "Display Custome Range View  ('start_date')strtime('start_date')"
        caption_text = "Display Custome Range View"
        caption_text1 = "Custome Range"
    else:
        caption_text = "The option is not selected so all Record Show"  # Add a default caption for unknown options
        caption_text1 = ""


    # Define a variable to store the filtered data
    filtered_firereport = Firereport.objects.filter(Status='In Progress')
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST

    if filter_option == 'Today':
        filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date=today.date())
    elif filter_option == 'Last7Days':
        last_week = today - timezone.timedelta(days=7)
        filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_week.date())
    elif filter_option == 'Last30Days':
        last_month = today - timezone.timedelta(days=30)
        filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_month.date())
    elif filter_option == 'ThisMonth':
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=current_month.date())

    # Handle the custom range filter
    if filter_option == 'Custom' and start_date and end_date:
        filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__range=(start_date, end_date))

    if not request.user.is_superuser:
        filtered_firereport = _firereport_qs_scoped_for_staff(filtered_firereport, request.user)
    filtered_firereport = _dedupe_firereport_rows(filtered_firereport)
    filtered_firereport = sorted(
        filtered_firereport,
        key=lambda r: (
            getattr(r, "UpdationDate", None) or getattr(r, "Postingdate", None),
            getattr(r, "id", 0),
        ),
        reverse=True,
    )

    return render(request, 'admin/teamontheway.html',
                  {'filtered_firereport': filtered_firereport, 'filter_option': filter_option, 'count1': count1,
                   'notification1': notification1, 'caption_text': caption_text, 'caption_text1': caption_text1,})


@login_required(login_url='user-login')
def workinprogress(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    today = now_ist()
    #today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight
    start_date, end_date = None, None


    # Get the start and end date for custom range from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Determine the caption text based on the selected_option
    if filter_option == "All":
        caption_text = "Display All Days View"
        caption_text1 = "Up To Date"
    elif filter_option == "Today":
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        caption_text1 = "Today"
    elif filter_option == "Last7Days":
        start_date = today - timezone.timedelta(days=7)
        end_date = today
        caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 7 Days View"
        caption_text1 = "Last 7 Days"
    elif filter_option == "Last30Days":
        start_date = today - timezone.timedelta(days=30)
        end_date = today
        caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 30 Days View"
        caption_text1 = "Last 30 Days"
    elif filter_option == "ThisMonth":
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display This Month View"
        caption_text1 = "This Month"
    elif filter_option == "Custom":
        # caption_text = "Display Custome Range View  ('start_date')strtime('start_date')"
        caption_text = "Display Custome Range View"
        caption_text1 = "Custome Range"
    else:
        caption_text = "Not select the Option"  # Add a default caption for unknown options
        caption_text1 = " "

    # Define a variable to store the filtered data
    filtered_firereport = Firereport.objects.filter(Status='Work in Progress')
    #today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

    if filter_option == 'Today':
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date=now_ist().date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date=now_ist().date()) &
            Q(firetequesthistory__status='Work in Progress')
        )
    elif filter_option == 'Last7Days':
        last_week = now_ist() - timezone.timedelta(days=7)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_week.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=last_week.date()) &
            Q(firetequesthistory__status='Work in Progress')
        )
    elif filter_option == 'Last30Days':
        last_month = now_ist() - timezone.timedelta(days=30)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_month.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=last_month.date()) &
            Q(firetequesthistory__status='Work in Progress')
        )
    elif filter_option == 'ThisMonth':
        current_month = now_ist().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=current_month.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=current_month.date()) &
            Q(firetequesthistory__status='Work in Progress')
        )

    # Handle the custom range filter
    if filter_option == 'Custom' and start_date and end_date:
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__range=(start_date, end_date))
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__range=(start_date, end_date)) &
            Q(firetequesthistory__status='Work in Progress')
        )
    if not request.user.is_superuser:
        filtered_firereport = _firereport_qs_scoped_for_staff(filtered_firereport, request.user)
    filtered_firereport = _dedupe_firereport_rows(filtered_firereport)
    filtered_firereport = sorted(
        filtered_firereport,
        key=lambda r: (
            getattr(r, "UpdationDate", None) or getattr(r, "Postingdate", None),
            getattr(r, "id", 0),
        ),
        reverse=True,
    )

    return render(request, 'admin/workinprogress.html',
                  {'filtered_firereport': filtered_firereport, 'filter_option': filter_option, 'count1': count1,
                   'notification1': notification1, 'caption_text': caption_text, 'caption_text1': caption_text1})


@login_required(login_url='user-login')
def completeRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    today = now_ist()
    #today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight
    start_date, end_date = None, None


    # Get the start and end date for custom range from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Determine the caption text based on the selected_option
    if filter_option == "All":
        caption_text = "Display All Days View"
        caption_text1 = "Up To Date"
    elif filter_option == "Today":
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        caption_text1 = "Today"
    elif filter_option == "Last7Days":
        start_date = today - timezone.timedelta(days=7)
        end_date = today
        caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 7 Days View"
        caption_text1 = "Last 7 Days"
    elif filter_option == "Last30Days":
        start_date = today - timezone.timedelta(days=30)
        end_date = today
        caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 30 Days View"
        caption_text1 = "Last 30 Days"
    elif filter_option == "ThisMonth":
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display This Month View"
        caption_text1 = "This Month"
    elif filter_option == "Custom":
        # caption_text = "Display Custome Range View  ('start_date')strtime('start_date')"
        caption_text = "Display Custome Range View"
        caption_text1 = "Custome Range"
    else:
        caption_text = "Not select the Option"  # Add a default caption for unknown options
        caption_text1 = " "

    # Define a variable to store the filtered data
    filtered_firereport = Firereport.objects.filter(Status='Request Completed')
    #today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

    if filter_option == 'Today':
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date=now_ist().date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date=now_ist().date()) &
            Q(firetequesthistory__status='Request Completed')
        )
    elif filter_option == 'Last7Days':
        last_week = now_ist() - timezone.timedelta(days=7)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_week.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=last_week.date()) &
            Q(firetequesthistory__status='Request Completed')
        )
    elif filter_option == 'Last30Days':
        last_month = now_ist() - timezone.timedelta(days=30)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_month.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=last_month.date()) &
            Q(firetequesthistory__status='Request Completed')
        )
    elif filter_option == 'ThisMonth':
        current_month = now_ist().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=current_month.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=current_month.date()) &
            Q(firetequesthistory__status='Request Completed')
        )

    # Handle the custom range filter
    if filter_option == 'Custom' and start_date and end_date:
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__range=(start_date, end_date))
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__range=(start_date, end_date)) &
            Q(firetequesthistory__status='Request Completed')
        )
    if not request.user.is_superuser:
        filtered_firereport = _firereport_qs_scoped_for_staff(filtered_firereport, request.user)
    filtered_firereport = _dedupe_firereport_rows(filtered_firereport)
    filtered_firereport = sorted(
        filtered_firereport,
        key=lambda r: (
            getattr(r, "UpdationDate", None) or getattr(r, "Postingdate", None),
            getattr(r, "id", 0),
        ),
        reverse=True,
    )

    return render(request, 'admin/completeRequest.html',
                  {'filtered_firereport': filtered_firereport, 'filter_option': filter_option, 'count1': count1,
                   'notification1': notification1, 'caption_text': caption_text, 'caption_text1': caption_text1})


@login_required(login_url='user-login')
def allRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    # today = now_ist()
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST
    start_date, end_date = None, None


    # Get the start and end date for custom range from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Determine the caption text based on the selected_option
    if filter_option == "All":
        caption_text = "Display All Days View"
        caption_text1 = "Up To Date"
    elif filter_option == "Today":
        # caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Today View"
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        caption_text1 = "Today"
    elif filter_option == "Last7Days":
        start_date = today - timezone.timedelta(days=7)
        end_date = today
        caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 7 Days View"
        caption_text1 = "Last 7 Days"
    elif filter_option == "Last30Days":
        start_date = today - timezone.timedelta(days=30)
        end_date = today
        caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 30 Days View"
        caption_text1 = "Last 30 Days"
    elif filter_option == "ThisMonth":
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display This Month View"
        caption_text1 = "This Month"
    elif filter_option == "Custom":
        # caption_text = "Display Custome Range View  ('start_date')strtime('start_date')"
        caption_text = "Display Custome Range View"
        caption_text1 = "Custome Range"
    else:
        caption_text = "The option is not selected so all Record Show"  # Add a default caption for unknown options
        caption_text1 = ""


    # Define a variable to store the filtered data
    filtered_firereport = Firereport.objects.all()
    today = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight IST

    if filter_option == 'Today':
        filtered_firereport = filtered_firereport.filter(UpdationDate__date=today.date())
    elif filter_option == 'Last7Days':
        last_week = today - timezone.timedelta(days=7)
        filtered_firereport = filtered_firereport.filter(UpdationDate__date__gte=last_week.date())
    elif filter_option == 'Last30Days':
        last_month = today - timezone.timedelta(days=30)
        filtered_firereport = filtered_firereport.filter(UpdationDate__date__gte=last_month.date())
    elif filter_option == 'ThisMonth':
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        filtered_firereport = filtered_firereport.filter(UpdationDate__date__gte=current_month.date())

    # Handle the custom range filter
    if filter_option == 'Custom' and start_date and end_date:
        filtered_firereport = filtered_firereport.filter(UpdationDate__date__range=(start_date, end_date))

    if not request.user.is_superuser:
        filtered_firereport = _firereport_qs_scoped_for_staff(filtered_firereport, request.user)
    filtered_firereport = _dedupe_firereport_rows(filtered_firereport)
    filtered_firereport = sorted(
        filtered_firereport,
        key=lambda r: (
            getattr(r, "UpdationDate", None) or getattr(r, "Postingdate", None),
            getattr(r, "id", 0),
        ),
        reverse=True,
    )

    return render(request, 'admin/allRequest.html',
                  {'filtered_firereport': filtered_firereport, 'filter_option': filter_option, 'count1': count1,
                   'notification1': notification1, 'caption_text': caption_text, 'caption_text1': caption_text1,})




@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def deleteRequest(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    firereport = Firereport.objects.filter(id=pid).order_by('-Postingdate').first()
    if not firereport:
        messages.error(request, f"Request #{pid} not found.")
        return redirect('firereport-allRequest')
    denied = _assert_firereport_staff_access(request, firereport)
    if denied:
        return denied
    firereport.delete()
    return redirect('allRequest')


@login_required(login_url='user-login')
def viewRequestDetails(request, pid):
    from customer.staff_access import is_associate_staff

    if not request.user.is_authenticated:
        return redirect('user-login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    user = get_user(request)
    if user is None:
        return redirect('user-login')
    firereport = Firereport.objects.filter(id=pid).order_by('-Postingdate').first()
    if not firereport:
        messages.error(request, f"Request #{pid} not found.")
        return redirect('firereport-assignRequest')
    denied = _assert_firereport_staff_access(request, firereport)
    if denied:
        return denied
    # Associates may view linked consumers' complaints but must not assign or change status
    firereport_associate_readonly = is_associate_staff(request.user)
    report1 = Firetequesthistory.objects.filter(firereport=firereport)
    firereportid = firereport.id
    #team = Teams.objects.all()
    # all_users = User.objects.all()
    all_users = User.objects.filter(is_staff=1, is_active=1)
    reportcount = Firetequesthistory.objects.filter(firereport=firereport).count()
    unique_departments = set(user.profile.department for user in all_users)
    error1 = None  # Initialize error1 variable
    error = None

    if request.method == "POST" and firereport_associate_readonly:
        from django.contrib import messages

        messages.warning(request, "Associate users cannot assign or update complaints.")
        return redirect("firereport-viewRequestDetails", pid=pid)

    if request.method == "POST":
        # Check which form was submitted
        if 'AssignTo' in request.POST:
            # Handle "Assign To" form submission
            try:
                Teamid = request.POST['AssignTo']
                Status = "Assigned"
                team1 = User.objects.get(id=Teamid)
                AssignBy = request.user.id
                
                firereport.AssignTo = team1
                firereport.Status = Status
                firereport.AssignBy = AssignBy
                now = now_ist()
                firereport.AssignedTime = now
                firereport.UpdationDate = now
                firereport.save()

                error = "no"
            except Exception as e:
                import traceback
                print(f"Error assigning request: {str(e)}")
                print(traceback.format_exc())
                error = "yes"
        
        elif 'status' in request.POST and 'remark' in request.POST:
            # Handle "Take Action" form submission
            try:
                status = request.POST['status']
                remark = request.POST['remark']
                
                # Truncate remark if it exceeds model's max_length (250)
                if len(remark) > 250:
                    remark = remark[:250]

                firereport.Status = status
                firereport.UpdationDate = now_ist()

                if status == "In Progress":
                    firereport.progress_date = now_ist()
                elif status == "Work in Progress":
                    firereport.working_date = now_ist()
                elif status == "Request Completed":
                    firereport.complete_date = now_ist()

                firereport.save()

                # Prevent accidental double-submit duplicate history rows.
                last_history = Firetequesthistory.objects.filter(
                    firereport=firereport
                ).order_by('-postingDate').first()
                should_create_history = True
                if last_history:
                    if (
                        (last_history.status or '').strip() == status.strip()
                        and (last_history.remark or '').strip() == remark.strip()
                        and last_history.AssignBy == request.user.id
                    ):
                        should_create_history = False

                if should_create_history:
                    Firetequesthistory.objects.create(
                        firereport=firereport,
                        status=status,
                        remark=remark,
                        AssignTo=firereport.AssignTo,
                        AssignBy=request.user.id
                    )

                error1 = "no"
            except Exception as e:
                # Log the error for debugging
                import traceback
                print(f"Error in viewRequestDetails Take Action: {str(e)}")
                print(traceback.format_exc())
                error1 = "yes"
    return render(request, 'admin/viewRequestDetails.html', locals())



@login_required(login_url='user-login')
def reviewRequestDetails(request, pid):
    from customer.staff_access import is_associate_staff

    if not request.user.is_authenticated:
        return redirect('user-login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    user = get_user(request)
    if user is None:
        return redirect('user-login')
    firereport = Firereport.objects.filter(id=pid).order_by('-Postingdate').first()
    if not firereport:
        messages.error(request, f"Request #{pid} not found.")
        return redirect('firereport-reassignRequest')
    denied = _assert_firereport_staff_access(request, firereport)
    if denied:
        return denied
    firereport_associate_readonly = is_associate_staff(request.user)
    if request.method == "POST" and firereport_associate_readonly:
        from django.contrib import messages

        messages.warning(request, "Associate users cannot re-assign or update complaints.")
        return redirect("firereport-reviewRequestDetails", pid=pid)
    report1 = Firetequesthistory.objects.filter(firereport=firereport)
    firereportid = firereport.id
    #team = Teams.objects.all()
    assigned_user = firereport.AssignTo
    # Filter users who are not the currently assigned user
    # all_users = User.objects.exclude(id=assigned_user.id) if assigned_user else User.objects.all()
    if assigned_user:
        all_users = User.objects.exclude(id=assigned_user.id).filter(is_staff=1, is_active=1)
    else:
        all_users = User.objects.filter(is_staff=1, is_active=1)
    #all_users = User.objects.all()
    reportcount = Firetequesthistory.objects.filter(firereport=firereport).count()
    unique_departments = set(user.profile.department for user in all_users)
    try:
        if request.method == "POST":
            Teamid = request.POST['AssignTo']
            Status="Assigned"
            team1 = User.objects.get(id=Teamid)
            AssignBy = request.user.id
            try:
                #user = get_user(request)
                firereport.AssignTo = team1
                firereport.Status = Status
                firereport.AssignBy = AssignBy
                now = now_ist()
                # firereport.AssignedTime = now.strftime("%d/%m/%Y %H:%M:%S")
                firereport.AssignedTime = now
                firereport.UpdationDate = now
                firereport.save()
                # logout(request)
                # login(request, user)

                error = "no"
            except:
                # user = get_user(request)
                # #logout(request)
                # login(request, user)
                error = "yes"
    except:
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
        user = get_user(request)
        unique_departments = set(user.profile.department for user in all_users)
        if user is None:
            return redirect('user-login')
        if request.method == "POST":
            status = request.POST['status']
            remark = request.POST['remark']

            try:
                #user = get_user(request)
                requesttracking = Firetequesthistory.objects.create(
                    firereport=firereport,
                    status=status,
                    remark=remark,
                    AssignTo=firereport.AssignTo,
                    AssignBy=request.user.id
                )
                firereport.Status = status
                firereport.UpdationDate = now_ist()
                firereport.save()
                # logout(request)
                # login(request, user)

                error1 = "no"
            except Exception as e:
                # Log the error for debugging
                import traceback
                print(f"Error in reviewRequestDetails: {str(e)}")
                print(traceback.format_exc())
                #user = get_user(request)
                #logout(request)
                #login(request, user)
                error1 = "yes"
    return render(request, 'admin/re_viewRequestDetails.html', locals())


from django.contrib.auth.models import User

@login_required(login_url='user-login')
def dateReport(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if request.method == 'POST':
        fd = request.POST['fromDate']
        td = request.POST['toDate']
        firereport = Firereport.objects.filter(Q(Postingdate__gte=fd) & Q(Postingdate__lte=td))
        if request.user.is_superuser:
            pass
        elif request.user.is_staff:
            firereport = _firereport_qs_scoped_for_staff(firereport, request.user)
        else:
            firereport = firereport.filter(Account_id=request.user.id)
        return render(request, 'admin/betweendateReportDtls.html', locals())
    return render(request, 'admin/dateReport.html', locals())


@login_required(login_url='user-login')
def search(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    search_by = 'staff'  # Default to 'staff' when the page is loaded for the first time
    staff_list = User.objects.filter(is_staff=True)

    if not request.user.is_superuser:
        staff_list = staff_list.filter(id=request.user.id)  # Filter staff_list based on the logged-in user

    staff_assignee_id = None
    staff_assignee = None  # Initialize staff_assignee as None
    report_filter = 'all'  # Default to 'all' when the page is loaded for the first time
    status_filter = ''  # Default to an empty string for status_filter
    consumer_search_data = None
    firereport = None

    if request.method == 'POST':
        search_by = request.POST.get('search_by', 'staff')  # Get the selected option from the form

        if search_by == 'staff':
            staff_assignee_id = request.POST.get('staff_assignee', '')
            report_filter = request.POST.get('report_filter', 'all')  # Get the selected filter option
            status_filter = request.POST.get('status_filter', '')  # Get the selected status filter option

            firereport = Firereport.objects.all()  # Get all fire reports initially
            if not request.user.is_superuser:
                firereport = _firereport_qs_scoped_for_staff(firereport, request.user)

            if staff_assignee_id and staff_assignee_id != 'all':
                staff_assignee = User.objects.get(pk=staff_assignee_id)
                firereport = firereport.filter(AssignTo_id=staff_assignee_id)

            if report_filter == 'week':
                # Filter reports for the selected staff by week
                start_of_week = now_ist().date() - timezone.timedelta(days=now_ist().date().weekday())
                firereport = firereport.filter(Postingdate__gte=start_of_week)

            elif report_filter == 'month':
                # Filter reports for the selected staff by month
                start_of_month = now_ist().date().replace(day=1)
                firereport = firereport.filter(Postingdate__gte=start_of_month)

            # Apply status_filter based on the selected option
            if status_filter:
                firereport = firereport.filter(Status=status_filter)

        else:
            consumer_search_data = request.POST.get('consumer_search_data', '')
            if consumer_search_data:
                firereport = Firereport.objects.filter(
                    Q(FullName__icontains=consumer_search_data) |
                    Q(MobileNumber__icontains=consumer_search_data) |
                    Q(Location__icontains=consumer_search_data)
                )
                if not request.user.is_superuser:
                    if request.user.is_staff:
                        firereport = _firereport_qs_scoped_for_staff(firereport, request.user)
                    else:
                        firereport = firereport.filter(Account_id=request.user.id)
                # Apply status_filter based on the selected option
                if status_filter:
                    firereport = firereport.filter(Status=status_filter)

    else:
        firereport = None

    context = {
        'search_by': search_by,
        'staff_list': staff_list,
        'firereport': firereport,
        'staff_assignee': staff_assignee,
        'report_filter': report_filter,
        'status_filter': status_filter,  # Add status_filter to the context
        'consumer_search_data': consumer_search_data,
        'notification1':notification1,
        'count1':count1,
    }
    return render(request, 'admin/search.html', context)






@login_required(login_url='user-login')
def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    user = request.user
    if request.method == "POST":
        o = request.POST['oldpassword']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if user.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = 'not'
        except:
            error = "yes"
    return render(request, 'admin/changePassword.html', locals())


@login_required(login_url='user-login')
def Logout(request):
    logout(request)
    return redirect('user-login')


