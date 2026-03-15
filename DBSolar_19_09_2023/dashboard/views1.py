from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from customer.models import Customer
from firereport.models import Firereport
from user.models import Profile
from user.views import profile
from .models import Product, Order, staff_Notification
from .forms import ProductForm, OrderForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
    totalAdmin = Profile.objects.filter(department='Administration').count()
    totalStockist = Profile.objects.filter(department='Stockist').count()
    totalFinance = Profile.objects.filter(department='Finance').count()
    totalEngineers = Profile.objects.filter(department='Engineers').count()
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
def Administration(request):
    customer = User.objects.filter(groups=2, profile__department='Administration')
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    totalAdmin = Profile.objects.filter(department='Administration').count()
    totalStockist = Profile.objects.filter(department='Stockist').count()
    totalFinance = Profile.objects.filter(department='Finance').count()
    totalEngineers = Profile.objects.filter(department='Engineers').count()
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


# @login_required(login_url='user-login')
# def product_detail(request, pk):
#     context = {
#
#     }
#     return render(request, 'dashboard/products_detail.html', context)
#


@login_required(login_url='user-login')
def index1(request):
    customer = User.objects.filter(groups=2, is_staff=True)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    totalAdmin = Profile.objects.filter(department='Administration').count()
    totalStockist = Profile.objects.filter(department='Stockist').count()
    totalFinance = Profile.objects.filter(department='Finance').count()
    totalEngineers = Profile.objects.filter(department='Engineers').count()
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




@login_required(login_url='user-login')
def index(request):
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    customer1 = Customer.objects.all()
    customer1_count = customer1.count()
    firereport = Firereport.objects.all()
    firereport_count = firereport.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    totalfire = Firereport.objects.all().count()
    totalAdmin = User.objects.filter(is_staff=True).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    totalStockist = Customer.objects.all().count()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()

    totalnewrequest11 = Firereport.objects.filter(Status__isnull=True, AssignTo=request.user.id).count()
    totalAssign1 = Firereport.objects.filter(Status='Assigned', AssignTo=request.user.id).count()
    totalontheway1 = Firereport.objects.filter(Status='Team On the Way', AssignTo=request.user.id).count()
    totalworkprocess1 = Firereport.objects.filter(Status='Work in Progress', AssignTo=request.user.id).count()
    totalreqcomplete1 = Firereport.objects.filter(Status='Request Completed', AssignTo=request.user.id).count()
    totalfire1 = Firereport.objects.filter(AssignTo=request.user.id).count()

    totalFinance = (
            Firereport.objects.filter(Status='Assigned').count() +
            Firereport.objects.filter(Status='Team On the Way').count() +
            Firereport.objects.filter(Status='Work in Progress').count() +
            Firereport.objects.filter(Status__isnull=True).count()
    )

    totalEngineers = Profile.objects.filter(department='Engineers').count()

    context = {
        'count1': count1,
        'customer': customer,
        'customer1': customer,
        'profile': profile,
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

        'totalAssign1':totalAssign1,
        'totalontheway1':totalontheway1,
        'totalworkprocess1':totalworkprocess1,
        'totalreqcomplete1':totalreqcomplete1,
        'totalfire1':totalfire1,
    }
    return render(request, 'dashboard/index.html', context)





# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def customers(request):
#     customer = User.objects.filter(groups=2, is_staff=True)
#     customer_count = customer.count()
#     profile = Profile.objects.all()
#     totalAdmin = Profile.objects.filter(department='Administration').count()
#     totalStockist = Profile.objects.filter(department='Stockist').count()
#     totalFinance = Profile.objects.filter(department='Finance').count()
#     totalEngineers = Profile.objects.filter(department='Engineers').count()
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     dept = Profile._meta.get_field('department').choices
#     if request.method == 'POST':
#         name = request.POST.get('name', None)
#         dept = request.POST.get('dept', None)
#
#         if name:
#             customer = customer.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(id__icontains=name) | Q(email__icontains=name) |  Q(first_name__icontains=name.split()[0]) |
#                 Q(last_name__icontains=name.split()[-1]) | Q(profile__phone__icontains=name))
#         if dept:
#              customer = customer.filter(profile__department__icontains=dept)
#
#         context = {
#             'count1': count1,
#             'customer': customer,
#             'profile': profile,
#             'customer_count': customer_count,
#             'totalAdmin': totalAdmin,
#             'totalStockist': totalStockist,
#             'totalFinance': totalFinance,
#             'totalEngineers': totalEngineers,
#             'dept': dept,
#             'notification1': notification1,
#
#         }
#
#
#         return render(request, 'dashboard/customers.html', context)
#     elif request.method == 'GET':
#         customer = User.objects.filter(groups=2, is_staff=True)
#         customer_count = customer.count()
#         profile = Profile.objects.all()
#         dept = Profile._meta.get_field('department').choices
#         totalAdmin = Profile.objects.filter(department='Administration').count()
#         totalStockist = Profile.objects.filter(department='Stockist').count()
#         totalFinance = Profile.objects.filter(department='Finance').count()
#         totalEngineers = Profile.objects.filter(department='Engineers').count()
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#         context = {
#             'count1': count1,
#             'customer': customer,
#             'profile': profile,
#             'customer_count': customer_count,
#             'totalAdmin': totalAdmin,
#             'totalStockist': totalStockist,
#             'totalFinance': totalFinance,
#             'totalEngineers': totalEngineers,
#             'dept': dept,
#             'notification1': notification1,
#         }
#     return render(request, 'dashboard/customers.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def customers(request):
    customer = User.objects.filter(groups=2, is_staff=True)
    customer_count = customer.count()
    profile = Profile.objects.all()
    totalAdmin = Profile.objects.filter(department='Administration').count()
    totalStockist = Profile.objects.filter(department='Stockist').count()
    totalFinance = Profile.objects.filter(department='Finance').count()
    totalEngineers = Profile.objects.filter(department='Engineers').count()
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



# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def customers(request):
#     customer = User.objects.filter(groups=2, is_staff=True)
#     customer_count = customer.count()
#     profile = Profile.objects.all()
#     totalAdmin = Profile.objects.filter(department='Administration').count()
#     totalStockist = Profile.objects.filter(department='Stockist').count()
#     totalFinance = Profile.objects.filter(department='Finance').count()
#     totalEngineers = Profile.objects.filter(department='Engineers').count()
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     dept = Profile._meta.get_field('department').choices
#
#     if request.method == 'POST':
#         search_term = request.POST.get('name', None)
#         dept = request.POST.get('dept', None)
#
#         if search_term:
#             customer = customer.filter(
#                 Q(first_name__icontains=search_term) |
#                 Q(last_name__icontains=search_term) |
#                 Q(id__icontains=search_term) |
#                 Q(email__icontains=search_term) |
#                 Q(profile__phone__icontains=search_term) |
#                 Q(first_name__icontains=search_term.split()[0]) |  # Search first_name separately
#                 Q(last_name__icontains=search_term.split()[-1])    # Search last_name separately
#             )
#
#         if dept:
#             customer = customer.filter(profile__department__icontains=dept)
#
#     # Common code for both GET and POST
#     context = {
#         'count1': count1,
#         'customer': customer,
#         'profile': profile,
#         'customer_count': customer_count,
#         'totalAdmin': totalAdmin,
#         'totalStockist': totalStockist,
#         'totalFinance': totalFinance,
#         'totalEngineers': totalEngineers,
#         'dept': dept,
#         'notification1': notification1,
#     }
#
#     return render(request, 'dashboard/customers.html', context)


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

    return render(request, 'dashboard/dashboard_staff.html', locals())




@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def stockist(request):
    customer = User.objects.filter(groups=2, profile__department='Stockist')

    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    totalAdmin = Profile.objects.filter(department='Administration').count()
    totalStockist = Profile.objects.filter(department='Stockist').count()
    totalFinance = Profile.objects.filter(department='Finance').count()
    totalEngineers = Profile.objects.filter(department='Engineers').count()
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
    customer = User.objects.filter(groups=2, profile__department='Finance')
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    totalAdmin = Profile.objects.filter(department='Administration').count()
    totalStockist = Profile.objects.filter(department='Stockist').count()
    totalFinance = Profile.objects.filter(department='Finance').count()
    totalEngineers = Profile.objects.filter(department='Engineers').count()
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


# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def product_edit(request, pk):
#     item = Product.objects.get(id=pk)
#     if request.method == 'POST':
#         form = ProductForm(request.POST, instance=item)
#         if form.is_valid():
#             form.save()
#             return redirect('dashboard-products')
#     else:
#         form = ProductForm(instance=item)
#     context = {
#         'form': form,
#     }
#     return render(request, 'dashboard/products_edit.html', context)


# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def product_delete(request, pk):
#     item = Product.objects.get(id=pk)
#     if request.method == 'POST':
#         item.delete()
#         return redirect('dashboard-products')
#     context = {
#         'item': item
#     }
#     return render(request, 'dashboard/products_delete.html', context)


@login_required(login_url='user-login')
def engineers(request):
    customer = User.objects.filter(groups=2, profile__department='Engineers')
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    profile = Profile.objects.all()
    totalAdmin = Profile.objects.filter(department='Administration').count()
    totalStockist = Profile.objects.filter(department='Stockist').count()
    totalFinance = Profile.objects.filter(department='Finance').count()
    totalEngineers = Profile.objects.filter(department='Engineers').count()
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
    totalAdmin = Profile.objects.filter(department='Administration').count()
    totalStockist = Profile.objects.filter(department='Stockist').count()
    totalFinance = Profile.objects.filter(department='Finance').count()
    totalEngineers = Profile.objects.filter(department='Engineers').count()
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
    customer = Customer.objects.all()
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


# def save_staff_Notification(request):
#
#     if request.method == "POST":
#         staff_id = request.POST.get('staff_id')
#         message = request.POST.get('message')
#         sender = request.user
#
#         user = User.objects.get(id=staff_id)
#         notification = staff_Notification(
#             staff_id=user,
#             message=message,
#             sender= sender,
#         )
#         notification.save()
#         messages.success(request,'Notification Are Successfully Send')
#         return redirect('dashboard-staff_Send_Notification')
#     else:
#         return HttpResponse("Invalid Request")

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


        # if request.method == 'POST':
        #     message = request.POST['message']
        #     users = User.objects.all()
        #
        #     for user in users:
        #         notification = staff_Notification.objects.create(
        #             user=user,
        #             message=message
        #         )
        #         notification.save()
        #
        #     return render(request, 'success.html')
        #
        # return render(request,'dashboard/allnotification.html', locals())

    # if request.method == "POST":
    #     staff_id = request.POST.get('staff_id')
    #     message = request.POST.get('message')
    #
    #     user = User.objects.all()
    #     notification = staff_Notification(
    #         staff_id=user,
    #         message=message,
    #     )
    #     notification.save()
    #     messages.success(request,'Notification Are Successfully Send')
    #     return redirect('dashboard-staff_Send_Notification')
    # else:
    #     return HttpResponse("Invalid Request")


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
        notification = staff_Notification.objects.filter(staff_id=request.user.id)
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


