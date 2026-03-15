import datetime
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect

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


def now_ist():
    """Return current time in Indian Standard Time (Asia/Kolkata). Use this when saving timestamps."""
    return timezone.localtime(timezone.now())

# Create your views here.

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib import messages


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
    # Consumer portal: show only the logged-in user's complaints
    all_users = request.user.id
    firereport_qs = Firereport.objects.filter(Account_id=all_users).order_by("-id")
    # print(all_users)

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
            firereport_qs = Firereport.objects.filter(Account_id=all_users).order_by("-id")

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
    firereport = Firereport.objects.get(id=pid)
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
    totalnewequest = Firereport.objects.filter(Q(Status__isnull=True) | Q(Status="Pending")).count()
    totalAssign = Firereport.objects.filter(Status='Assigned').count()
    totalontheway = Firereport.objects.filter(Status='In Progress').count()
    totalworkprocess = Firereport.objects.filter(Status='Work in Progress').count()
    totalreqcomplete = Firereport.objects.filter(Status='Request Completed').count()
    totalfire = Firereport.objects.all().count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    return render(request, 'admin/dashboard.html', locals())


@login_required(login_url='user-login')
def dashboard_staff(request):
    totalnewrequest = Firereport.objects.filter(
        Q(Status__isnull=True) | Q(Status="Pending"),
        AssignTo=request.user.id,
    ).count()
    totalAssign = Firereport.objects.filter(Status='Assigned', AssignTo=request.user.id).count()
    totalontheway = Firereport.objects.filter(Status='In Progress', AssignTo=request.user.id).count()
    totalworkprocess = Firereport.objects.filter(Status='Work in Progress', AssignTo=request.user.id).count()
    totalreqcomplete = Firereport.objects.filter(Status='Request Completed', AssignTo=request.user.id).count()
    totalfire = Firereport.objects.filter(AssignTo=request.user.id).count()
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
        filtered_firereport = filtered_firereport.filter(AssignTo=request.user)

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
        filtered_firereport = filtered_firereport.filter(AssignTo=request.user)

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
        filtered_firereport = filtered_firereport.filter(AssignTo=request.user)

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
        filtered_firereport = filtered_firereport.filter(AssignTo=request.user)

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
        filtered_firereport = filtered_firereport.filter(AssignTo=request.user)

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
        filtered_firereport = filtered_firereport.filter(AssignTo=request.user)

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
        filtered_firereport = filtered_firereport.filter(AssignTo=request.user)

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
    firereport = Firereport.objects.get(id=pid)
    firereport.delete()
    return redirect('allRequest')


@login_required(login_url='user-login')
def viewRequestDetails(request, pid):
    if not request.user.is_authenticated:
        return redirect('user-login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    user = get_user(request)
    if user is None:
        return redirect('user-login')
    firereport = Firereport.objects.get(id=pid)
    report1 = Firetequesthistory.objects.filter(firereport=firereport)
    firereportid = firereport.id
    #team = Teams.objects.all()
    # all_users = User.objects.all()
    all_users = User.objects.filter(is_staff=1, is_active=1)
    reportcount = Firetequesthistory.objects.filter(firereport=firereport).count()
    unique_departments = set(user.profile.department for user in all_users)
    error1 = None  # Initialize error1 variable
    
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

                # Create a history record
                requesttracking = Firetequesthistory.objects.create(
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
    if not request.user.is_authenticated:
        return redirect('user-login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    user = get_user(request)
    if user is None:
        return redirect('user-login')
    firereport = Firereport.objects.get(id=pid)
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
        if request.user.is_superuser:
            firereport = Firereport.objects.filter(Q(Postingdate__gte=fd) & Q(Postingdate__lte=td))
        elif request.user.is_staff:
            firereport = Firereport.objects.filter(Q(Postingdate__gte=fd) & Q(Postingdate__lte=td), AssignTo=request.user)
        else:
            firereport = Firereport.objects.filter(Q(Postingdate__gte=fd) & Q(Postingdate__lte=td), Account_id=request.user.id)
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


