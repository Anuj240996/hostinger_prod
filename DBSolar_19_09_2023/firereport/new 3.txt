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
    totalontheway = Firereport.objects.filter(Status='Team On the Way').count()
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
    totalontheway = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user.id).count()
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
    all_users = User.objects.filter(is_staff=True)
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
        AssignedTime = now.strftime("%m/%d/%Y %H:%M:%S")

        try:
            Firereport.objects.create(FullName=FullName, MobileNumber=MobileNumber, Location=Location,
                                      Message=Message, AssignTo=team1, Status=Status, AssignedTime=AssignedTime,
                                      Account_id=Account_id, AssignBy=AssignBy)
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


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def newRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    firereport = Firereport.objects.filter(Status__isnull=True)
    return render(request, 'admin/newRequest.html', locals())


@login_required(login_url='user-login')
def assignRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    firereport = Firereport.objects.filter(Status='Assigned')
    if request.user.is_superuser:
        firereport = Firereport.objects.filter(Status='Assigned')
    else:
        firereport = Firereport.objects.filter(Status='Assigned',AssignTo=request.user)
    return render(request, 'admin/assignRequest.html', locals())


@login_required(login_url='user-login')
def teamontheway(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    #firereport = Firereport.objects.filter(Status='Team On the Way')
    if request.user.is_superuser:
        firereport = Firereport.objects.filter(Status='Team On the Way')
    else:
        firereport = Firereport.objects.filter(Status='Team On the Way',AssignTo=request.user)
    return render(request, 'admin/teamontheway.html', locals())


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def workinprogress(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    #firereport = Firereport.objects.filter(Status='Work in Progress')
    if request.user.is_superuser:
        firereport = Firereport.objects.filter(Status='Work in Progress')
    else:
        firereport = Firereport.objects.filter(Status='Work in Progress',AssignTo=request.user)

    return render(request, 'admin/workinprogress.html', locals())


@login_required(login_url='user-login')
def completeRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    #firereport = Firereport.objects.filter(Status='Request Completed')
    if request.user.is_superuser:
        firereport = Firereport.objects.filter(Status='Request Completed')
    else:
        firereport = Firereport.objects.filter(Status='Request Completed',AssignTo=request.user)

    return render(request, 'admin/completeRequest.html', locals())


@login_required(login_url='user-login')
def allRequest(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    firereport = Firereport.objects.all()
    if request.user.is_superuser:
        firereport = Firereport.objects.all()
    elif request.user.is_staff:
        firereport = Firereport.objects.filter(AssignTo=request.user)
    return render(request, 'admin/allRequest.html', locals())


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
    all_users = User.objects.all()
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
                firereport.AssignedTime = now.strftime("%m/%d/%Y %H:%M:%S")
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
                firereport.save()
                firereport.UpdationDate = date.today()
                # logout(request)
                # login(request, user)

                error1 = "no"
            except:
                #user = get_user(request)
                #logout(request)
                #login(request, user)
                error1 = "yes"
    return render(request, 'admin/viewRequestDetails.html', locals())



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



@login_required(login_url='user-login')
def search(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    sd = None
    if request.method == 'POST':
        sd = request.POST['searchdata']
        try:
            # firereport = Firereport.objects.filter(Q(FullName__icontains=sd) | Q(MobileNumber=sd) | Q(Location__icontains=sd))

            if request.user.is_superuser:
                firereport = Firereport.objects.filter(Q(FullName__icontains=sd) | Q(MobileNumber=sd) | Q(Location__icontains=sd))
            elif request.user.is_staff:
                firereport = Firereport.objects.filter(Q(FullName__icontains=sd) | Q(MobileNumber=sd) | Q(Location__icontains=sd),
                                                       AssignTo=request.user)
            else:
                firereport = Firereport.objects.filter(Q(FullName__icontains=sd) | Q(MobileNumber=sd) | Q(Location__icontains=sd),
                                                       Account_id=request.user.id)
        except:
            firereport = ""
    return render(request, 'admin/search.html', locals())


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


