from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from customer.models import Customer, MSEB
from customer.staff_access import customer_queryset_for_request, is_associate_staff
from firereport.models import Firereport
from user.models import Profile
from user.views import profile
from .models import Product, Order, staff_Notification
from .forms import ProductForm, OrderForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .decorators import auth_users, allowed_users
from django.db.models import Q, Max
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone




# Create your views here.


@login_required(login_url='user-login')
def Allstaff(request):
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').count()
    totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').count()
    totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').count()
    totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.customer = request.user
            obj.save()
            return redirect('dashboard-index')
    else:
        form = OrderForm()
    context = {
        'form': form,
        'order': order,
        'profile': profile,
        'product': product,
        'totalAdmin': totalAdmin,
        'totalStockist': totalStockist,
        'totalFinance': totalFinance,
        'totalEngineers': totalEngineers,
        'product_count': product_count,
        'order_count': order_count,
        'customer_count': customer_count,
        'count1': count1,
        'notification1': notification1,
    }
    return render(request, 'dashboard/Allstaff.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def Administration(request):
    # customer = User.objects.filter(groups=2, profile__department='Administration')
    customer = User.objects.filter(groups=2, profile__department='Administration', is_active=True).exclude(Q(first_name='') | Q(last_name=''))
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').exclude(Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').exclude(Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').exclude(Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').exclude(Q(customer__first_name='') | Q(customer__last_name='')).count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    context = {
        'count1': count1,
        'customer': customer,
        'profile': profile,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'totalAdmin': totalAdmin,
        'totalStockist': totalStockist,
        'totalFinance': totalFinance,
        'totalEngineers': totalEngineers,
        'notification1': notification1,
    }
    return render(request, 'dashboard/Administration.html', context)



@login_required(login_url='user-login')
def index1(request):
    if is_associate_staff(request.user) and not request.user.is_superuser:
        return redirect('customer-view_all')
    # customer = User.objects.filter(groups=2, is_staff=True)
    customer = User.objects.filter(groups=2, is_staff=True, is_active=True).exclude(Q(first_name='') | Q(last_name=''))
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    # totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').count()
    # totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').count()
    # totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').count()
    # totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').count()
    totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').exclude(Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').exclude(Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').exclude(Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').exclude(Q(customer__first_name='') | Q(customer__last_name='')).count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    context = {
        'count1': count1,
        'customer': customer,
        'profile': profile,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'totalAdmin': totalAdmin,
        'totalStockist': totalStockist,
        'totalFinance': totalFinance,
        'totalEngineers': totalEngineers,
        'notification1': notification1,
    }
    return render(request, 'dashboard/index1.html', context)


from datetime import datetime, timedelta
from django.db.models import F, ExpressionWrapper, DurationField

from datetime import datetime, timedelta
from datetime import datetime, timedelta, timezone
from django.utils import timezone as dj_timezone
# from .models import MSEB  # Import the MSEB model from your models file
from datetime import timedelta
from django.utils import timezone


@login_required(login_url='user-login')


@login_required(login_url='user-login')
def index(request):
    if is_associate_staff(request.user) and not request.user.is_superuser:
        return redirect('customer-view_all')
    error = None  # Initialize the error variable
    customers = User.objects.filter(groups__id=2)
    customer_count = customers.count()
    customer_list = customer_queryset_for_request(request.user)
    customer1_count = customer_list.count()
    firereports = Firereport.objects.all()
    firereport_count = firereports.count()
    products = Product.objects.all()
    product_count = products.count()
    orders = Order.objects.all()
    order_count = orders.count()
    profiles = Profile.objects.all()
    totalfire = firereports.count()
    totalAdmin = User.objects.filter(is_staff=True, is_active=True).exclude(Q(first_name='') | Q(last_name='')).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    totalStockist = customer_list.count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()

    totalnewrequest11 = Firereport.objects.filter(Status__isnull=True, AssignTo=request.user.id).count()
    totalAssign1 = Firereport.objects.filter(Status='Assigned', AssignTo=request.user.id).count()
    totalontheway1 = Firereport.objects.filter(Status='In Progress', AssignTo=request.user.id).count()
    totalworkprocess1 = Firereport.objects.filter(Status='Work in Progress', AssignTo=request.user.id).count()
    totalreqcomplete1 = Firereport.objects.filter(Status='Request Completed', AssignTo=request.user.id).count()
    totalfire1 = Firereport.objects.filter(AssignTo=request.user.id).count()
    totalFinance = (
        Firereport.objects.filter(Status='Assigned').count() +
        Firereport.objects.filter(Status='In Progress').count() +
        Firereport.objects.filter(Status='Work in Progress').count() +
        Firereport.objects.filter(Status__isnull=True).count()
    )
    # Add this part to check the password condition
    password_check = request.user.check_password('admin@123')
    totalEngineers = Profile.objects.filter(department='Engineers').count()
    user = request.user

    now = dj_timezone.now().date()

    # Initialize total warranty count
    total_warranty_quantity = 0

    # Warranty counts only for customers this user may see (same scope as customer_list)
    customers = customer_list

    for customer in customers:
        # Retrieve corresponding MSEB data for each customer
        mseb_data = MSEB.objects.filter(customer=customer).first()
        if mseb_data:
            installation_date = mseb_data.installation_date_date
            if installation_date:
                com_warranty_years = customer.com_warranty
                if com_warranty_years:
                    # Count this customer in the total warranty count
                    total_warranty_quantity += 1

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

    context = {
        'count1': count1,
        'customers': customers,
        'customer_list': customer_list,
        'profiles': profiles,
        'customer_count': customer_count,
        'customer1_count': customer1_count,
        'firereport_count': firereport_count,
        'product_count': product_count,
        'order_count': order_count,
        'totalfire': totalfire,
        'totalAdmin': totalAdmin,
        'totalStockist': totalStockist,
        'totalFinance': totalFinance,
        'totalEngineers': totalEngineers,
        'notification1': notification1,

        'totalAssign1': totalAssign1,
        'totalontheway1': totalontheway1,
        'totalworkprocess1': totalworkprocess1,
        'totalreqcomplete1': totalreqcomplete1,
        'totalfire1': totalfire1,
        'error': error,
        'password_check': password_check,

        # Additional context for warranty calculations
        'total_warranty_quantity': total_warranty_quantity,
    }
    return render(request, 'dashboard/index.html', context)




from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
@permission_required('auth.change_user', raise_exception=True)
def customers(request):
    # customer = User.objects.filter(groups=2, is_staff=True)
    customer = User.objects.filter(groups=2, is_staff=True).exclude(Q(first_name='') | Q(last_name=''))
    customer_count = customer.count()
    profile = Profile.objects.all()
    totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').count()
    totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').count()
    totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').count()
    totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    dept = Profile._meta.get_field('department').choices

    if request.method == 'POST':
        search_term = request.POST.get('name', None)
        dept = request.POST.get('dept', None)

        if search_term:
            # Check if the search term is an integer (ID search)
            try:
                search_term_int = int(search_term.replace(" ", ""))  # Remove spaces for ID search
                customer = customer.filter(id__exact=search_term_int)
            except ValueError:
                # If the search term is not an integer, search in name and phone fields
                customer = customer.filter(
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(email__icontains=search_term) |
                    Q(profile__phone__icontains=search_term) |
                    Q(first_name__icontains=search_term.split()[0]) |  # Search first_name separately
                    Q(last_name__icontains=search_term.split()[-1])    # Search last_name separately
                )

        if dept:
            customer = customer.filter(profile__department__icontains=dept)

    # Common code for both GET and POST
    context = {
        'count1': count1,
        'customer': customer,
        'profile': profile,
        'customer_count': customer_count,
        'totalAdmin': totalAdmin,
        'totalStockist': totalStockist,
        'totalFinance': totalFinance,
        'totalEngineers': totalEngineers,
        'dept': dept,
        'notification1': notification1,
    }

    return render(request, 'dashboard/customers.html', context)


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

    return render(request, 'dashboard/dashboard_staff.html', locals())


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def stockist(request):
    customer = User.objects.filter(groups=2, profile__department='Stockist', is_active=True)

    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    # totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').count()
    # totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').count()
    # totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').count()
    # totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').count()

    totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    context = {
        'count1': count1,
        'customer': customer,
        'profile': profile,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'totalAdmin': totalAdmin,
        'totalStockist': totalStockist,
        'totalFinance': totalFinance,
        'totalEngineers': totalEngineers,
        'notification1': notification1,
    }
    return render(request, 'dashboard/stockist.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def finance(request):
    customer = User.objects.filter(groups=2, profile__department='Finance', is_active=True)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    # totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').count()
    # totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').count()
    # totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').count()
    # totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').count()

    totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    context = {
        'count1': count1,
        'customer': customer,
        'profile': profile,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'totalAdmin': totalAdmin,
        'totalStockist': totalStockist,
        'totalFinance': totalFinance,
        'totalEngineers': totalEngineers,
        'notification1': notification1,
    }
    return render(request, 'dashboard/finance.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def engineers(request):
    customer = User.objects.filter(groups=2, profile__department='Engineers', is_active=True)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    # totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').count()
    # totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').count()
    # totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').count()
    # totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').count()
    totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()
    totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').exclude(
        Q(customer__first_name='') | Q(customer__last_name='')).count()

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    context = {
        'count1': count1,
        'customer': customer,
        'profile': profile,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'totalAdmin': totalAdmin,
        'totalStockist': totalStockist,
        'totalFinance': totalFinance,
        'totalEngineers': totalEngineers,
        'notification1': notification1,
    }
    return render(request, 'dashboard/engineers.html', context)

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def customer_detail(request, pk):
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    customers = User.objects.get(id=pk)
    totalAdmin = Profile.objects.filter(customer__is_active=True, department='Administration').count()
    totalStockist = Profile.objects.filter(customer__is_active=True, department='Stockist').count()
    totalFinance = Profile.objects.filter(customer__is_active=True, department='Finance').count()
    totalEngineers = Profile.objects.filter(customer__is_active=True, department='Engineers').count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    context = {
        'count1': count1,
        'customers': customers,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'totalAdmin': totalAdmin,
        'totalStockist': totalStockist,
        'totalFinance': totalFinance,
        'totalEngineers': totalEngineers,
        'notification1': notification1,
    }
    return render(request, 'dashboard/customers_detail.html', context)

def staff_Send_Notification(request):
    staff = User.objects.filter(is_staff=True)
    profile = Profile.objects.all()
    see_notification = staff_Notification.objects.filter(staff_id_id__is_staff=True).order_by('-is_current', '-created_at')
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    context = {
        'count1': count1,
        'staff': staff,
        'profile': profile,
        'see_notification': see_notification,
        'notification1': notification1,
    }
    return render(request,'dashboard/sendstaff_Notification.html', context)

def consumer_Send_Notification(request):
    staff = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
    customer = customer_queryset_for_request(request.user)
    profile = Profile.objects.all()
    see_notification = staff_Notification.objects.filter(staff_id_id__is_active=True, staff_id_id__is_staff=False).order_by('-is_current', '-created_at')[:10]
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    context = {
        'count1': count1,
        'staff': staff,
        'profile': profile,
        'customer': customer,
        'see_notification': see_notification,
        'notification1': notification1,
    }
    return render(request,'dashboard/sendconsumer_Notification.html', context)



def save_staff_Notification(request):
    if request.method == "POST":
        staff_id = request.POST.get('staff_id')
        message = request.POST.get('message')
        sender = request.user

        user = User.objects.get(id=staff_id)

        # Check if the user is staff and active
        if user.is_staff and user.is_active:
            notification = staff_Notification(
                staff_id=user,
                message=message,
                sender=sender,
            )
            notification.save()
            messages.success(request, 'Notification Are Successfully Send')
            return redirect('dashboard-staff_Send_Notification')
        elif user.is_active:  # Check if the user is just active (consumer)
            notification = staff_Notification(
                staff_id=user,
                message=message,
                sender=sender,
            )
            notification.save()
            messages.success(request, 'Notification Are Successfully Send')
            return redirect('dashboard-consumer_Send_Notification')
        else:
            return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")


def allnotification(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    if request.method == 'POST':
        message = request.POST['message']
        #users = User.objects.filter(is_staff=True, is_superuser=True)
        users = User.objects.filter(is_staff=True)
        for user in users:
            notification = staff_Notification.objects.create(message=message, staff_id=user, sender=request.user)
            notification.save()
        return redirect('dashboard-staff_Send_Notification')
    else:
        return render(request, 'dashboard/allnotification.html', locals())



def allconsumernotification(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if request.method == 'POST':
        message = request.POST['message']
        #users = User.objects.filter(is_staff=True, is_superuser=True)
        users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
        for user in users:
            notification = staff_Notification.objects.create(message=message, staff_id=user, sender=request.user)
            notification.save()
        return redirect('dashboard-consumer_Send_Notification')
    else:
        return render(request, 'dashboard/allconsumernotification.html', locals())


def Notification(request):

    staff = User.objects.filter(id = request.user.id)
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # for notification2 in notification1:
    #     notification2.duration = timezone.now() - notification2.created_at
    for i in staff:
        staff_id = i.id
        total = staff_Notification.objects.filter(status =0)
        notification = staff_Notification.objects.filter(staff_id=request.user.id).order_by(
            '-created_at')  # This sorts the notifications in descending order of created_at

        count1 = staff_Notification.objects.filter(staff_id=staff_id, status=False).count()
        # for notification in notification:
        #     notification.duration = timezone.now() - notification.generated_time
        context = {
            'notification':notification,
            'total':total,
            'notification1': notification1,
            'count1': count1,
            #'notification2': notification2,

        }
    return render(request,'dashboard/Notification.html', context)

def notification_count(request):
    # global count1
    # staff = User.objects.filter(id=request.user.id)
    # for i in staff:
    #     staff_id = i.id
    #     total = staff_Notification.objects.filter(status=0).count()
    #     notification_count = staff_Notification.objects.filter(staff_id=staff_id, status=False).count()
    #
    #
    #     print(count1)
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    context = {'count1': count1,
               'notfication1': notification1,
             # 'total': total,
             # 'notification_count': notification_count,
            }
    # context ={
    #         'count1':count1,
    #         'total':total,
    #     }
    return render(request,'dashboard/Notification_count.html', context)


def Staff_Notification_Mark_Done(request,status):
    if not status:
        logout(request)
        return redirect('login')  # replace 'login' with the name of your login page URL

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    notification = staff_Notification.objects.get(id = status)
    notification.status = 1
    notification.save()
    return redirect('dashboard-notification')


from django.http import JsonResponse
@permission_required('auth.change_user', raise_exception=True)
def delete_user(request, user_id):
    try:
        # Assuming you have a User model with a profile
        user = User.objects.get(id=user_id)
        user.profile.delete()  # Delete the related profile
        user.delete()          # Delete the user
        return JsonResponse({}, status=204)  # Return a success response
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from django.http import JsonResponse
from django.views.decorators.http import require_POST

import json
from django.http import JsonResponse



import json
from django.http import JsonResponse


@require_POST
def toggle_status(request, user_id, action):
    user = get_object_or_404(User, id=user_id)

    if action == 'activate':
        user.is_active = True
        # Fetch JSON data from the request for reactivation
        data = json.loads(request.body.decode('utf-8'))
        rejoin_reason = data.get('rejoinReason', '')
        rejoin_date = data.get('rejoinDate', None)

        # Save data to the profile for reactivation
        user.profile.rejoin_reason = rejoin_reason
        user.profile.rejoin_date = rejoin_date
        user.profile.save()

    elif action == 'deactivate':
        user.is_active = False
        # Fetch JSON data from the request
        data = json.loads(request.body.decode('utf-8'))
        resign_reason = data.get('resignReason', '')
        resign_date = data.get('resignDate', None)
        resign_type = data.get('resignType', '')

        # Save data to the profile
        user.profile.resign_reason = resign_reason
        user.profile.resign_date = resign_date
        user.profile.resign_type = resign_type
        user.profile.save()


    user.save()

    return JsonResponse({'status': 'success'})
