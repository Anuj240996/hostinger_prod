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

# Create your views here.

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

# @login_required(login_url='user-login')
# def reporting(request):
#     error = ""
#     user1 = User.objects.all()
#
#     if request.method == "POST":
#         FullName = request.POST['FullName']
#         Account_id = user1.id
#         MobileNumber = request.POST['MobileNumber']
#         Location = request.POST['Location']
#         Message = request.POST['Message']
#         try:
#             Firereport.objects.create(FullName=FullName, MobileNumber=MobileNumber, Location=Location, Message=Message, Account_id=Account_id)
#             error = "no"
#         except:
#             error = "yes"
#     return render(request, 'reporting.html', locals())

@login_required(login_url='user-login')
def reporting(request):
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    User = get_user_model()
    #user = request.user
    customer = Customer.objects.get(new_customer=request.user)
    if request.method == "POST":
        FullName = request.POST['FullName']
        MobileNumber = request.POST['MobileNumber']
        Location = request.POST['Location']
        Message = request.POST['Message']
        try:
            # Get the current user's id
            Account_id = request.user.id
            # MobileNumber = request.user.profile.phone
            # Location = request.user.profile.city
            # FullName = request.user.first_name + " " + request.user.last_name
            Firereport.objects.create(FullName=FullName, MobileNumber=MobileNumber, Location=Location, Message=Message, Account_id=Account_id)
            error = "no"
        except:
            error = "yes"
    return render(request, 'reporting.html', locals())


@login_required(login_url='user-login')
def viewStatus(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if not request.user.is_authenticated:
        return redirect('admin_login')
    User = get_user_model()
    firereport = Firereport.objects.all()
    all_users = request.user.id
    print(all_users)

    sd = None
    if request.method == 'POST':
        sd = request.POST['searchdata']
        try:
            firereport = Firereport.objects.filter(Q(FullName__icontains=sd) | Q(MobileNumber=sd) | Q(Location__icontains=sd) | Q(id=sd))
        except:
            user = get_user(request)
            logout(request)
            login(request, user)
            firereport = ""
    return render(request, 'viewStatus.html', locals())


@login_required(login_url='user-login')
def viewStatusDetails(request,pid):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    firereport = Firereport.objects.get(id=pid)
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
    totalnewequest = Firereport.objects.filter(Status__isnull=True).count()
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
    totalnewrequest = Firereport.objects.filter(Status__isnull=True, AssignTo=request.user.id).count()
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


# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def task(request):
#     error = ""
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     #firereport = Firereport.objects.all()
#     User = get_user_model()
#     # all_users = User.objects.all()
#     all_users = User.objects.filter(is_staff=True)
#     #consumerlist = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
#     customer = Customer.objects.all()
#     all_profiles = Profile.objects.all()
#     all_users = User.objects.all()
#     departments = Profile._meta.get_field('department').choices
#     companies = Customer.objects.values('Comp_name').distinct()
#     if request.method == "POST":
#             # retrieve the selected department from the form
#             # department = request.POST.get('department')
#
#             # # retrieve the corresponding profiles
#             # profiles = Profile.objects.filter(department=department)
#
#             # retrieve the corresponding usernames
#             # usernames = [profile.user.username for profile in profiles]
#
#             Teamid = request.POST['AssignTo']
#             Status = "Assigned"
#             team1 = User.objects.get(id=Teamid)
#             FullName = request.POST['comp_name']
#             MobileNumber = request.POST['phone']
#             Location = request.POST['City']
#             Message = request.POST['Message']
#             Account_id = request.user.id
#             now = datetime.now()
#             AssignedTime = now.strftime("%m/%d/%Y %H:%M:%S")
#             firereport = Firereport.objects.all()
#
#             try:
#                 Firereport.objects.create(FullName=FullName, MobileNumber=MobileNumber, Location=Location,
#                                           Message=Message, AssignTo=team1, Status=Status, AssignedTime=AssignedTime, Account_id=Account_id)
#                 error = "no"
#             except:
#                 error = "yes"
#                 return render(request, 'admin/task.html', locals())
#
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
#                     # Add other fields here
#                 }
#                 return HttpResponse(json.dumps(data), content_type='application/json')
#     return HttpResponse(json.dumps({}), content_type='application/json')


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

        # if Teamid and Teamid.isdigit():
        #     try:
        #         team1 = User.objects.get(id=int(Teamid))
        #     except User.DoesNotExist:
        #         error = f"Invalid user ID: {Teamid}"
        #         return render(request, 'admin/task.html', {'error': error})
        # elif AssignTo:
        #     try:
        #         team1 = User.objects.get(first_name=AssignTo)
        #     except User.DoesNotExist:
        #         error = f"Invalid username: {AssignTo}"
        #         return render(request, 'admin/task.html', {'error': error})
        # else:
        #     error = "No AssignTo value provided."
        #     return render(request, 'admin/task.html', {'error': error})
        # #
        # Teamid = request.POST['AssignToID']
        # Status = "Assigned"
        # #team1 = User.objects.get(id=int(Teamid))
        # team1 = User.objects.get(id=Teamid)
        # # try:
        # #     team1 = User.objects.get(id=int(Teamid))
        # #     team1 = User.objects.get(id=Teamid)
        # # except User.DoesNotExist:
        # #     error = f"Invalid user ID: {Teamid}"
        # #     return render(request, 'admin/task.html', {'error': error})

        FullName = request.POST['comp_name']
        MobileNumber = request.POST['phone']
        Location = request.POST['city']
        Message = request.POST['Message']
        Account_id = request.POST['new_customer_id']
        AssignBy = request.user.id
        now = datetime.now()
        # AssignedTime = now.strftime("%d/%m/%Y %H:%M:%S")
        AssignedTime = datetime.now()
        UpdationDate = datetime.now()

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


#
# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def task(request):
#     error = ""
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     User = get_user_model()
#     all_users = User.objects.filter(is_staff=True)
#     customer = Customer.objects.all()
#     all_profiles = Profile.objects.all()
#     departments = Profile._meta.get_field('department').choices
#     companies = Customer.objects.values('Comp_name').distinct()
#
#     if request.method == "POST":
#         Teamid = request.POST['AssignTo']
#         Status = "Assigned"
#         team1 = User.objects.get(id=Teamid)
#         FullName = request.POST['comp_name']
#         MobileNumber = request.POST['phone']
#         Location = request.POST['City']
#         Message = request.POST['Message']
#         Account_id = request.user.id
#         now = datetime.now()
#         AssignedTime = now.strftime("%m/%d/%Y %H:%M:%S")
#
#         try:
#             Firereport.objects.create(FullName=FullName, MobileNumber=MobileNumber, Location=Location,
#                                       Message=Message, AssignTo=team1, Status=Status, AssignedTime=AssignedTime,
#                                       Account_id=Account_id)
#             error = "no"
#         except Exception as e:
#             error = "yes"
#             return render(request, 'admin/task.html', {'error': error})
#
#     return render(request, 'admin/task.html', {
#         'error': error,
#         'count1': count1,
#         'notification1': notification1,
#         'all_users': all_users,
#         'customer': customer,
#         'all_profiles': all_profiles,
#         'departments': departments,
#         'companies': companies,
#     })


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
                    'Plant_Capacity': customer.Plant_Capacity,
                    'new_customer_id': customer.new_customer_id,  # Add the new field here
                    # Add other fields here
                }
                return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse(json.dumps({}), content_type='application/json')


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


# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def newRequest(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     firereport = Firereport.objects.filter(Status__isnull=True)
#     return render(request, 'admin/newRequest.html', locals())


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def newRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    # today = timezone.now()
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight
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
    filtered_firereport = Firereport.objects.filter(Status__isnull=True)
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

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

    return render(request, 'admin/newRequest.html',
                  {'filtered_firereport': filtered_firereport, 'filter_option': filter_option, 'count1': count1,
                   'notification1': notification1, 'caption_text': caption_text, 'caption_text1': caption_text1,})




# @login_required(login_url='user-login')
# def assignRequest(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     firereport = Firereport.objects.filter(Status='Assigned')
#     if request.user.is_superuser:
#         firereport = Firereport.objects.filter(Status='Assigned')
#     else:
#         firereport = Firereport.objects.filter(Status='Assigned',AssignTo=request.user)
#     return render(request, 'admin/assignRequest.html', locals())


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def assignRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    # today = timezone.now()
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight
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
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

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



# @login_required(login_url='user-login')
# def reassignRequest(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     firereport = Firereport.objects.filter(Status='Assigned')
#     if request.user.is_superuser:
#         firereport = Firereport.objects.filter(Status='Assigned')
#     else:
#         firereport = Firereport.objects.filter(Status='Assigned',AssignTo=request.user)
#     return render(request, 'admin/re_assignRequest.html', locals())



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def reassignRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    # today = timezone.now()
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight
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
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

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


#
# @login_required(login_url='user-login')
# def teamontheway(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     #firereport = Firereport.objects.filter(Status='Team On the Way')
#     if request.user.is_superuser:
#         firereport = Firereport.objects.filter(Status='Team On the Way')
#     else:
#         firereport = Firereport.objects.filter(Status='Team On the Way',AssignTo=request.user)
#     return render(request, 'admin/teamontheway.html', locals())


from django.utils import timezone
from datetime import timedelta

# @login_required(login_url='user-login')
# def teamontheway(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#     # Get the filter option from the request (e.g., query parameter)
#     filter_option = request.GET.get('filter_option')
#
#     # Define date ranges based on the filter options
#     today = timezone.now().date()
#     seven_days_ago = today - timedelta(days=7)
#     thirty_days_ago = today - timedelta(days=30)
#     first_day_of_month = today.replace(day=1)
#
#     if request.user.is_superuser:
#         if filter_option == '7':
#             firereport = Firereport.objects.filter(Status='Team On the Way', Postingdate__gte=seven_days_ago)
#         elif filter_option == '30':
#             firereport = Firereport.objects.filter(Status='Team On the Way', Postingdate__gte=thirty_days_ago)
#         elif filter_option == 'month':
#             firereport = Firereport.objects.filter(Status='Team On the Way', Postingdate__gte=first_day_of_month)
#         elif filter_option == 'today':
#             firereport = Firereport.objects.filter(Status='Team On the Way', Postingdate=today)
#         else:
#             firereport = Firereport.objects.filter(Status='Team On the Way')
#     else:
#         if filter_option == '7':
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user, Postingdate__gte=seven_days_ago)
#         elif filter_option == '30':
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user, Postingdate__gte=thirty_days_ago)
#         elif filter_option == 'month':
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user, Postingdate__gte=first_day_of_month)
#         elif filter_option == 'today':
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user, Postingdate=today)
#         else:
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user)
#
#     return render(request, 'admin/teamontheway.html', locals())
#

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

#
# @login_required(login_url='user-login')
# def teamontheway(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#     filter_option = request.GET.get('filter_option')
#
#     today = timezone.now().date()
#     seven_days_ago = today - timedelta(days=7)
#     thirty_days_ago = today - timedelta(days=30)
#     first_day_of_month = today.replace(day=1)
#
#     if request.user.is_superuser:
#         if filter_option == '7':
#             firereport = Firereport.objects.filter(Status='Team On the Way', Postingdate__gte=seven_days_ago)
#         elif filter_option == '30':
#             firereport = Firereport.objects.filter(Status='Team On the Way', Postingdate__gte=thirty_days_ago)
#         elif filter_option == 'month':
#             firereport = Firereport.objects.filter(Status='Team On the Way', Postingdate__gte=first_day_of_month)
#         elif filter_option == 'today':
#             firereport = Firereport.objects.filter(Status='Team On the Way', Postingdate=today)
#         else:
#             firereport = Firereport.objects.filter(Status='Team On the Way')
#     else:
#         if filter_option == '7':
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user,
#                                                    Postingdate__gte=seven_days_ago)
#         elif filter_option == '30':
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user,
#                                                    Postingdate__gte=thirty_days_ago)
#         elif filter_option == 'month':
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user,
#                                                    Postingdate__gte=first_day_of_month)
#         elif filter_option == 'today':
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user, Postingdate=today)
#         else:
#             firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user)
#
#     return render(request, 'admin/teamontheway.html', locals())


from django.utils import timezone

from datetime import datetime
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
#
# @login_required(login_url='user-login')
# def teamontheway(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#     # firereport = Firereport.objects.all()
#     # report1 = Firetequesthistory.objects.filter(firereport=firereport)
#
#     filter_option = request.GET.get('filter_option', 'all')
#     today = timezone.now()
#     start_date, end_date = None, None
#
#     if filter_option == 'today':
#         today = timezone.now()
#         start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
#         end_date = today
#     elif filter_option == 'last7days':
#         start_date = today - timezone.timedelta(days=7)
#         end_date = today
#     elif filter_option == 'last30days':
#         start_date = today - timezone.timedelta(days=30)
#         end_date = today
#     elif filter_option == 'thismonth':
#         start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         end_date = today
#     elif filter_option == 'all':
#         # Show all records (no date filter)
#         pass
#     if request.GET.get("filter_option") == "custom":
#         start_date_str = request.GET.get('start_date', '')
#         end_date_str = request.GET.get('end_date', '')
#         if start_date_str and end_date_str:
#             try:
#                 start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(
#                     tzinfo=timezone.get_current_timezone())
#                 end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())
#             except ValueError:
#                 start_date, end_date = None, None
#
    # # Determine the caption text based on the selected_option
    # if filter_option == "all":
    #     caption_text = f"Display All Days View"
    #     caption_text1 = "Up To Date"
    # elif filter_option == "today":
    #     caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
    #     caption_text1 = "Today"
    # elif filter_option == "last7days":
    #     caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
    #     caption_text1 = "Last 7 Days"
    # elif filter_option == "last30days":
    #     caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
    #     caption_text1 = "Last 30 Days"
    # elif filter_option == "thismonth":
    #     caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
    #     caption_text1 = "This Month"
    # elif filter_option == "custom":
    #     caption_text = f"Display Custome Range View  {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
    #     caption_text1 = "Custome Range"
    # else:
    #     caption_text = "Not select the Option"  # Add a default caption for unknown options

    # if request.user.is_superuser:
    #     if filter_option == 'all':
    #         firereport = Firereport.objects.filter(Status='Team On the Way')
    #
    #     else:
    #         # firereport = Firetequesthistory.objects.filter(status='Team On the Way', postingDate__range=(start_date, end_date))
    #         firereport = Firereport.objects.filter(Status='Team On the Way',  firetequesthistory__postingDate__range=(start_date, end_date))
    # else:
    #     if filter_option == 'all':
    #         firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user)
    #     else:
    #         firereport = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user,
    #                                                firetequesthistory__postingDate__range=(start_date, end_date))
    #
    # return render(request, 'admin/teamontheway.html', locals())

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
    # today = timezone.now()
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight
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
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

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

    # if request.user.is_superuser:
    #     if filter_option == 'all':
    #         filtered_firereport = filtered_firereport.filter(Status='Team On the Way')
    #
    #     else:
    #         # firereport = Firetequesthistory.objects.filter(status='Team On the Way', postingDate__range=(start_date, end_date))
    #         filtered_firereport = filtered_firereport.filter(Status='Team On the Way',
    #                                                firetequesthistory__postingDate__range=(start_date, end_date))
    # else:
    #     if filter_option == 'all':
    #         filtered_firereport = filtered_firereport.filter(Status='Team On the Way', AssignTo=request.user)
    #     else:
    #         filtered_firereport = filtered_firereport.filter(Status='Team On the Way', AssignTo=request.user,
    #                                                firetequesthistory__postingDate__range=(start_date, end_date))
    #
    # return render(request, 'admin/teamontheway.html', {'filtered_firereport': filtered_firereport, 'filter_option': filter_option, 'count1': count1,
    #                'notification1': notification1})



# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def workinprogress(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     #firereport = Firereport.objects.filter(Status='Work in Progress')
#     if request.user.is_superuser:
#         firereport = Firereport.objects.filter(Status='Work in Progress')
#     else:
#         firereport = Firereport.objects.filter(Status='Work in Progress',AssignTo=request.user)
#
#     return render(request, 'admin/workinprogress.html', locals())

@login_required(login_url='user-login')
def workinprogress(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    today = timezone.now()
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
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date=timezone.now().date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date=timezone.now().date()) &
            Q(firetequesthistory__status='Work in Progress')
        )
    elif filter_option == 'Last7Days':
        last_week = timezone.now() - timezone.timedelta(days=7)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_week.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=last_week.date()) &
            Q(firetequesthistory__status='Work in Progress')
        )
    elif filter_option == 'Last30Days':
        last_month = timezone.now() - timezone.timedelta(days=30)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_month.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=last_month.date()) &
            Q(firetequesthistory__status='Work in Progress')
        )
    elif filter_option == 'ThisMonth':
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
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


# @login_required(login_url='user-login')
# def completeRequest(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     #firereport = Firereport.objects.filter(Status='Request Completed')
#     if request.user.is_superuser:
#         firereport = Firereport.objects.filter(Status='Request Completed')
#     else:
#         firereport = Firereport.objects.filter(Status='Request Completed',AssignTo=request.user)
#
#     return render(request, 'admin/completeRequest.html', locals())



@login_required(login_url='user-login')
def completeRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    today = timezone.now()
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
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date=timezone.now().date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date=timezone.now().date()) &
            Q(firetequesthistory__status='Request Completed')
        )
    elif filter_option == 'Last7Days':
        last_week = timezone.now() - timezone.timedelta(days=7)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_week.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=last_week.date()) &
            Q(firetequesthistory__status='Request Completed')
        )
    elif filter_option == 'Last30Days':
        last_month = timezone.now() - timezone.timedelta(days=30)
        # filtered_firereport = filtered_firereport.filter(firetequesthistory__postingDate__date__gte=last_month.date())
        filtered_firereport = filtered_firereport.filter(
            Q(firetequesthistory__postingDate__date__gte=last_month.date()) &
            Q(firetequesthistory__status='Request Completed')
        )
    elif filter_option == 'ThisMonth':
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
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


#
# @login_required(login_url='user-login')
# def allRequest(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     firereport = Firereport.objects.all()
#     if request.user.is_superuser:
#         firereport = Firereport.objects.all()
#     elif request.user.is_staff:
#         firereport = Firereport.objects.filter(AssignTo=request.user)
#     return render(request, 'admin/allRequest.html', locals())



@login_required(login_url='user-login')
def allRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
    # today = timezone.now()
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight
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
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

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
                now = datetime.now()
                # firereport.AssignedTime = now.strftime("%d/%m/%Y %H:%M:%S")
                firereport.AssignedTime = datetime.now()
                firereport.UpdationDate = datetime.now()
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
                # #user = get_user(request)
                # requesttracking = Firetequesthistory.objects.create(firereport=firereport,status=status, remark=remark)
                # firereport.Status = status
                # firereport.save()
                # firereport.UpdationDate = date.today()
                # # logout(request)
                # # login(request, user)

                firereport.Status = status
                firereport.UpdationDate = datetime.now()

                if status == "In Progress":
                    firereport.progress_date = datetime.now()
                elif status == "Work in Progress":
                    firereport.working_date = datetime.now()
                elif status == "Request Completed":
                    firereport.complete_date = datetime.now()  # You may need to adjust this based on your model definition

                firereport.save()

                # Create a history record
                requesttracking = Firetequesthistory.objects.create(
                    firereport=firereport,
                    status=status,
                    remark=remark
                )

                error1 = "no"
            except:
                #user = get_user(request)
                #logout(request)
                #login(request, user)
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
                now = datetime.now()
                # firereport.AssignedTime = now.strftime("%d/%m/%Y %H:%M:%S")
                firereport.AssignedTime = datetime.now()
                firereport.UpdationDate = datetime.now()
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
                requesttracking = Firetequesthistory.objects.create(firereport=firereport,status=status, remark=remark)
                firereport.Status = status
                firereport.UpdationDate = date.today()
                firereport.save()
                # logout(request)
                # login(request, user)

                error1 = "no"
            except:
                #user = get_user(request)
                #logout(request)
                #login(request, user)
                error1 = "yes"
    return render(request, 'admin/re_viewRequestDetails.html', locals())


# @login_required(login_url='user-login')
# def dateReport(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     error = ""
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     if request.method == 'POST':
#         fd = request.POST['fromDate']
#         td = request.POST['toDate']
#         if request.user.is_superuser:
#             firereport = Firereport.objects.filter(Q(Postingdate__gte=fd) & Q(Postingdate__lte=td))
#         else:
#             firereport = Firereport.objects.filter(Q(Postingdate__gte=fd) & Q(Postingdate__lte=td), AssignTo=request.user)
#         return render(request, 'admin/betweendateReportDtls.html', locals())
#     return render(request, 'admin/dateReport.html', locals())

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



# @login_required(login_url='user-login')
# def search(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     sd = None
#     if request.method == 'POST':
#         sd = request.POST['searchdata']
#         try:
#             # firereport = Firereport.objects.filter(Q(FullName__icontains=sd) | Q(MobileNumber=sd) | Q(Location__icontains=sd))
#
#             if request.user.is_superuser:
#                 firereport = Firereport.objects.filter(Q(FullName__icontains=sd) | Q(MobileNumber=sd) | Q(Location__icontains=sd))
#             elif request.user.is_staff:
#                 firereport = Firereport.objects.filter(Q(FullName__icontains=sd) | Q(MobileNumber=sd) | Q(Location__icontains=sd),
#                                                        AssignTo=request.user)
#             else:
#                 firereport = Firereport.objects.filter(Q(FullName__icontains=sd) | Q(MobileNumber=sd) | Q(Location__icontains=sd),
#                                                        Account_id=request.user.id)
#         except:
#             firereport = ""
#     return render(request, 'admin/search.html', locals())


# @login_required(login_url='user-login')
# def search(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#     search_by = 'staff'  # Default to 'staff' when the page is loaded for the first time
#     staff_list = User.objects.filter(is_staff=True)
#
#     if request.method == 'POST':
#         search_by = request.POST.get('search_by', 'staff')  # Get the selected option from the form
#
#         if search_by == 'staff':
#             staff_assignee_id = request.POST.get('staff_assignee', '')
#             if staff_assignee_id:
#                 firereport = Firereport.objects.filter(AssignTo_id=staff_assignee_id)
#             else:
#                 firereport = None
#         else:
#             consumer_search_data = request.POST.get('consumer_search_data', '')
#             if consumer_search_data:
#                 firereport = Firereport.objects.filter(
#                     Q(FullName__icontains=consumer_search_data) |
#                     Q(MobileNumber__icontains=consumer_search_data) |
#                     Q(Location__icontains=consumer_search_data)
#                 )
#             else:
#                 firereport = None
#     else:
#         firereport = None
#
#     context = {
#         'search_by': search_by,
#         'staff_list': staff_list,
#         'firereport': firereport,
#     }
#
#     return render(request, 'admin/search.html', locals())

#
# @login_required(login_url='user-login')
# def search(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#     search_by = 'staff'  # Default to 'staff' when the page is loaded for the first time
#     staff_list = User.objects.filter(is_staff=True)
#
#     if not request.user.is_superuser:
#         staff_list = staff_list.filter(id=request.user.id)  # Filter staff_list based on the logged-in user
#
#     staff_assignee_id = None
#     staff_assignee = None  # Initialize staff_assignee as None
#
#     if request.method == 'POST':
#         search_by = request.POST.get('search_by', 'staff')  # Get the selected option from the form
#
#         if search_by == 'staff':
#             staff_assignee_id = request.POST.get('staff_assignee', '')
#             if staff_assignee_id:
#                 staff_assignee = User.objects.get(pk=staff_assignee_id)
#                 firereport = Firereport.objects.filter(AssignTo_id=staff_assignee_id)
#             else:
#                 firereport = None
#         else:
#             consumer_search_data = request.POST.get('consumer_search_data', '')
#             if consumer_search_data:
#                 firereport = Firereport.objects.filter(
#                     Q(FullName__icontains=consumer_search_data) |
#                     Q(MobileNumber__icontains=consumer_search_data) |
#                     Q(Location__icontains=consumer_search_data)
#                 )
#             else:
#                 firereport = None
#     else:
#         firereport = None
#
#     context = {
#         'search_by': search_by,
#         'staff_list': staff_list,
#         'firereport': firereport,
#         'staff_assignee':staff_assignee,
#     }
#     return render(request, 'admin/search.html', locals())



# @login_required(login_url='user-login')
# def search(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#     search_by = 'staff'  # Default to 'staff' when the page is loaded for the first time
#     staff_list = User.objects.filter(is_staff=True)
#
#     if not request.user.is_superuser:
#         staff_list = staff_list.filter(id=request.user.id)  # Filter staff_list based on the logged-in user
#
#     staff_assignee_id = None
#     staff_assignee = None  # Initialize staff_assignee as None
#     report_filter = 'all'  # Default to 'all' when the page is loaded for the first time
#     consumer_search_data = None
#
#     if request.method == 'POST':
#         search_by = request.POST.get('search_by', 'staff')  # Get the selected option from the form
#
#         if search_by == 'staff':
#             staff_assignee_id = request.POST.get('staff_assignee', '')
#             report_filter = request.POST.get('report_filter', 'all')  # Get the selected filter option
#
#             if staff_assignee_id:
#                 staff_assignee = User.objects.get(pk=staff_assignee_id)
#
#                 # Apply the filter based on the selected option
#                 if report_filter == 'week':
#                     # Filter reports for the selected staff by week
#                     start_of_week = timezone.now().date() - timezone.timedelta(days=timezone.now().date().weekday())
#                     firereport = Firereport.objects.filter(
#                         AssignTo_id=staff_assignee_id,
#                         Postingdate__gte=start_of_week
#                     )
#                 elif report_filter == 'month':
#                     # Filter reports for the selected staff by month
#                     start_of_month = timezone.now().date().replace(day=1)
#                     firereport = Firereport.objects.filter(
#                         AssignTo_id=staff_assignee_id,
#                         Postingdate__gte=start_of_month
#                     )
#                 else:
#                     # If "all" selected, fetch all reports for the selected staff
#                     firereport = Firereport.objects.filter(AssignTo_id=staff_assignee_id)
#             else:
#                 firereport = None
#         else:
#             consumer_search_data = request.POST.get('consumer_search_data', '')
#             if consumer_search_data:
#                 firereport = Firereport.objects.filter(
#                     Q(FullName__icontains=consumer_search_data) |
#                     Q(MobileNumber__icontains=consumer_search_data) |
#                     Q(Location__icontains=consumer_search_data)
#                 )
#             else:
#                 firereport = None
#     else:
#         firereport = None
#
#     context = {
#         'search_by': search_by,
#         'staff_list': staff_list,
#         'firereport': firereport,
#         'staff_assignee': staff_assignee,
#         'report_filter': report_filter,  # Add report_filter to the context
#         'consumer_search_data':consumer_search_data,
#     }
#     return render(request, 'admin/search.html', context)

# @login_required(login_url='user-login')
# def search(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#     search_by = 'staff'  # Default to 'staff' when the page is loaded for the first time
#     staff_list = User.objects.filter(is_staff=True)
#
#     if not request.user.is_superuser:
#         staff_list = staff_list.filter(id=request.user.id)  # Filter staff_list based on the logged-in user
#
#     staff_assignee_id = None
#     staff_assignee = None  # Initialize staff_assignee as None
#     report_filter = 'all'  # Default to 'all' when the page is loaded for the first time
#     status_filter = ''  # Default to an empty string for status_filter
#     consumer_search_data = None
#
#     if request.method == 'POST':
#         search_by = request.POST.get('search_by', 'staff')  # Get the selected option from the form
#
#         if search_by == 'staff':
#             staff_assignee_id = request.POST.get('staff_assignee', '')
#             report_filter = request.POST.get('report_filter', 'all')  # Get the selected filter option
#             status_filter = request.POST.get('status_filter', '')  # Get the selected status filter option
#
#             if staff_assignee_id:
#                 staff_assignee = User.objects.get(pk=staff_assignee_id)
#
#                 # Apply the filter based on the selected options
#                 firereport = Firereport.objects.filter(AssignTo_id=staff_assignee_id)
#
#                 if report_filter == 'week':
#                     # Filter reports for the selected staff by week
#                     start_of_week = timezone.now().date() - timezone.timedelta(days=timezone.now().date().weekday())
#                     firereport = firereport.filter(Postingdate__gte=start_of_week)
#
#                 elif report_filter == 'month':
#                     # Filter reports for the selected staff by month
#                     start_of_month = timezone.now().date().replace(day=1)
#                     firereport = firereport.filter(Postingdate__gte=start_of_month)
#
#                 # Apply status_filter based on the selected option
#                 if status_filter:
#                     firereport = firereport.filter(Status=status_filter)
#
#             else:
#                 firereport = None
#
#         else:
#             consumer_search_data = request.POST.get('consumer_search_data', '')
#             if consumer_search_data:
#                 firereport = Firereport.objects.filter(
#                     Q(FullName__icontains=consumer_search_data) |
#                     Q(MobileNumber__icontains=consumer_search_data) |
#                     Q(Location__icontains=consumer_search_data)
#                 )
#                 # Apply status_filter based on the selected option
#                 if status_filter:
#                     firereport = firereport.filter(Status=status_filter)
#             else:
#                 firereport = None
#     else:
#         firereport = None
#
#     context = {
#         'search_by': search_by,
#         'staff_list': staff_list,
#         'firereport': firereport,
#         'staff_assignee': staff_assignee,
#         'report_filter': report_filter,
#         'status_filter': status_filter,  # Add status_filter to the context
#         'consumer_search_data': consumer_search_data,
#     }
#     return render(request, 'admin/search.html', context)

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
                start_of_week = timezone.now().date() - timezone.timedelta(days=timezone.now().date().weekday())
                firereport = firereport.filter(Postingdate__gte=start_of_week)

            elif report_filter == 'month':
                # Filter reports for the selected staff by month
                start_of_month = timezone.now().date().replace(day=1)
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


