# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# #from .models import Product, Order
# #from .forms import ProductForm, OrderForm
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
#from .decorators import auth_users, allowed_users
# Create your views here.
#
#
# @login_required(login_url='user-login')
# def index(request):
#     product = Product.objects.all()
#     product_count = product.count()
#     order = Order.objects.all()
#     order_count = order.count()
#     customer = User.objects.filter(groups=2)
#     customer_count = customer.count()
#
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             obj = form.save(commit=False)
#             obj.customer = request.user
#             obj.save()
#             return redirect('dashboard-index')
#     else:
#         form = OrderForm()
#     context = {
#         'form': form,
#         'order': order,
#         'product': product,
#         'product_count': product_count,
#         'order_count': order_count,
#         'customer_count': customer_count,
#     }
#     return render(request, 'dashboard/index.html', context)
#
#
# @login_required(login_url='user-login')
# def products(request):
#     product = Product.objects.all()
#     product_count = product.count()
#     customer = User.objects.filter(groups=2)
#     customer_count = customer.count()
#     order = Order.objects.all()
#     order_count = order.count()
#     product_quantity = Product.objects.filter(name='')
#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             form.save()
#             product_name = form.cleaned_data.get('name')
#             messages.success(request, f'{product_name} has been added')
#             return redirect('dashboard-products')
#     else:
#         form = ProductForm()
#     context = {
#         'product': product,
#         'form': form,
#         'customer_count': customer_count,
#         'product_count': product_count,
#         'order_count': order_count,
#     }
#     return render(request, 'dashboard/Administration.html', context)
#
#
# @login_required(login_url='user-login')
# def product_detail(request, pk):
#     context = {
#
#     }
#     return render(request, 'dashboard/products_detail.html', context)
#
from io import BytesIO

from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from .models import customer_technical_Details
from django.shortcuts import redirect

#
# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def customers(request):
#     customer = User.objects.filter(groups=2)
#     customer_count = customer.count()
#     product = Product.objects.all()
#     product_count = product.count()
#     order = Order.objects.all()
#     order_count = order.count()
#     context = {
#         'customer': customer,
#         'customer_count': customer_count,
#         'product_count': product_count,
#         'order_count': order_count,
#     }
#     return render(request, 'dashboard/stockist.html', context)
#
#
# @login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
# def customer_detail(request, pk):
#     customer = User.objects.filter(groups=2)
#     customer_count = customer.count()
#     product = Product.objects.all()
#     product_count = product.count()
#     order = Order.objects.all()
#     order_count = order.count()
#     customers = User.objects.get(id=pk)
#     context = {
#         'customers': customers,
#         'customer_count': customer_count,
#         'product_count': product_count,
#         'order_count': order_count,
#     }
#     return render(request, 'dashboard/customers_detail.html', context)
#
#
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
#
#
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
#
#
# @login_required(login_url='user-login')
# def order(request):
#     order = Order.objects.all()
#     order_count = order.count()
#     customer = User.objects.filter(groups=2)
#     customer_count = customer.count()
#     product = Product.objects.all()
#     product_count = product.count()
#
#     context = {
#         'order': order,
#         'customer_count': customer_count,
#         'product_count': product_count,
#         'order_count': order_count,
#     }
#     return render(request, 'dashboard/engineers.html', context)

from django.shortcuts import render, HttpResponse

import user
from dashboard.models import staff_Notification
from user.forms import CreateUserForm, UserUpdateForm
from user.views import profile
from .models import Customer, Role, Department
from django.contrib.auth.models import User, Group
from datetime import datetime
from django.db.models import Q, Max
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
#from .models import Product, Order
#from .forms import ProductForm, OrderForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user, logout, login
from .decorators import auth_users, allowed_users
from django.contrib import messages

@login_required(login_url='user-login')
def cust(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    customer = Customer.objects.all()
    context = {
        'count1': count1,
        'customer': customer,
        'notification1': notification1,
    }
    return render(request, 'customer/cust.html', context)


# Create your views here.
@login_required(login_url='user-login')
def index(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    return render(request, 'customer/index.html', locals())

@login_required(login_url='user-login')
def Cust_emp(request):
    Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
    Cust_type = 'Indivisual'
    Emp_id = request.user.id
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if request.method == 'POST':
        # Create a new user first
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = request.POST['email']  # Add email to user object
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()
            # Add the user to the 'Customers' group
            group = Group.objects.get(name='Customers')
            user.groups.add(group)
            #Cust_id = int(request.POST['Cust_id'])
            Comp_name = request.POST['first_name'] + " " + request.POST['last_name']
            Consumer= request.POST['Consumer']
            Bill_unit= request.POST['Bill_unit']
            first_name= request.POST['first_name']
            middle_name= request.POST['middle_name']
            last_name= request.POST['last_name']
            Address= request.POST['Address']
            Plant_Capacity=int(request.POST['Plant_Capacity'])
            Ups_Soft= request.POST['Ups_Soft']
            #Cust_type= request.POST['Cust_type']
            City= request.POST['City']
            email= request.POST['email']
            phone=int(request.POST['phone'])
            Cus_Act_Date=(request.POST['Cus_Act_Date'])
            solar_comp= request.POST['solar_comp']
            UPSC= request.POST['UPSC']
            #Emp_id= int(request.POST['Emp_id'])
            state= request.POST['state']
            Pincode=int(request.POST['Pincode'])
            Gender= request.POST.get('Gender')
            loadsancution = request.POST['loadsancution']

            new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, Bill_unit=Bill_unit, first_name=first_name, middle_name=middle_name, last_name=last_name,
                                Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
                                City=City, email=email, phone=phone, Cus_Act_Date=Cus_Act_Date, solar_comp=solar_comp,
                                UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, Gender=Gender, new_customer=user, loadsancution=loadsancution)
            new_cust.save()
            messages.info(request, 'New Customer enrolled Successfully')

            cust = Customer.objects.all()
            if Cust_id:
                cust = cust.filter(Cust_id=Cust_id)
                context = {
                    'cust': cust,
                    'count1': count1,
                    'notification1': notification1,
                }
                return render(request, 'customer/Cust_emp.html', context)
            return HttpResponseRedirect("customer/Cust_emp")
    else:
        form = UserCreationForm()
        context = {
            'form': form,
            'count1': count1,
            'notification1': notification1,
        }
        return render(request, 'customer/Cust_emp.html', context)


# def Comm_Cust(request):
#     Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     Emp_id = request.user.id
#     Cust_type = 'Commersial'
#     if request.method == 'POST':
#         # Create a new user first
#       form = UserCreationForm(request.POST)
#       if form.is_valid():
#         user = form.save()
#         # Add the user to the 'Customers' group
#         group = Group.objects.get(name='Customers')
#         user.groups.add(group)
#         #Cust_id = int(request.POST['Cust_id'])
#         Comp_name = request.POST['Comp_name']
#         Consumer= request.POST['Consumer']
#         Bill_unit= request.POST['Bill_unit']
#         first_name= request.POST['first_name']
#         middle_name= request.POST['middle_name']
#         last_name= request.POST['last_name']
#         Address= request.POST['Address']
#         Plant_Capacity=int(request.POST['Plant_Capacity'])
#         Ups_Soft= request.POST['Ups_Soft']
#         #Cust_type= request.POST['Cust_type']
#         City= request.POST['City']
#         email= request.POST['email']
#         phone=int(request.POST['phone'])
#         Cus_Act_Date=(request.POST['Cus_Act_Date'])
#         solar_comp= request.POST['solar_comp']
#         UPSC= request.POST['UPSC']
#         #Emp_id= int(request.POST['Emp_id'])
#         state= request.POST['state']
#         Pincode=int(request.POST['Pincode'])
#         Gender= request.POST.get('Gender')
#
#         new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, Bill_unit=Bill_unit, first_name=first_name, middle_name=middle_name, last_name=last_name,
#                                 Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
#                                 City=City, email=email, phone=phone, Cus_Act_Date=Cus_Act_Date, solar_comp=solar_comp,
#                                 UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, Gender=Gender,new_customer=user)
#         new_cust.save()
#         error = "no"
#         messages.info(request, 'New Customer enrolled Successfully')
#         cust = Customer.objects.all()
#         if Cust_id:
#             cust = cust.filter(Cust_id=Cust_id)
#             context = {
#                     'cust': cust,
#                     'count1': count1,
#                     'notification1': notification1,
#             }
#             return render(request, 'customer/Comm_Cust.html', context)
#     else:
#         form = UserCreationForm()
#         context = {
#             'form': form,
#             'count1': count1,
#             'notification1': notification1,
#         }
#         return render(request, 'customer/Comm_Cust.html', context)


from django.db import transaction


@login_required(login_url='user-login')
def Comm_Cust(request):
    Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    Emp_id = request.user.id
    Cust_type = 'Commersial'
    if request.method == 'POST':
        # Create a new user first
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = request.POST['email']  # Add email to user object
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']

            user.save()
            # Add the user to the 'Customers' group
            group = Group.objects.get(name='Customers')
            user.groups.add(group)
            # Create a new customer first
            Comp_name = request.POST['Comp_name']
            Consumer = request.POST['Consumer']
            Bill_unit = request.POST['Bill_unit']
            first_name = request.POST['first_name']
            middle_name = request.POST['middle_name']
            last_name = request.POST['last_name']
            Address = request.POST['Address']
            Plant_Capacity = int(request.POST['Plant_Capacity'])
            Ups_Soft = request.POST['Ups_Soft']
            # Cust_type= request.POST['Cust_type']
            City = request.POST['City']
            phone = int(request.POST['phone'])
            Cus_Act_Date = request.POST['Cus_Act_Date']
            solar_comp = request.POST['solar_comp']
            UPSC = request.POST['UPSC']
            # Emp_id= int(request.POST['Emp_id'])
            state = request.POST['state']
            Pincode = int(request.POST['Pincode'])
            Gender = request.POST.get('Gender')
            loadsancution = request.POST['loadsancution']

            new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, Bill_unit=Bill_unit, first_name=first_name,
                                middle_name=middle_name, last_name=last_name, Address=Address, Plant_Capacity=Plant_Capacity,
                                Ups_Soft=Ups_Soft, Cust_type=Cust_type, City=City, email=user.email, phone=phone,
                                Cus_Act_Date=Cus_Act_Date, solar_comp=solar_comp, UPSC=UPSC, Emp_id=Emp_id, state=state,
                                Pincode=Pincode, Gender=Gender, new_customer=user, loadsancution=loadsancution)
            new_cust.save()
            error = "no"
            messages.info(request, 'New Customer enrolled Successfully')
            cust = Customer.objects.all()
            if Cust_id:
                cust = cust.filter(Cust_id=Cust_id)
                context = {
                    'cust': cust,
                    'count1': count1,
                    'notification1': notification1,
                }
                return render(request, 'customer/Comm_Cust.html', context)
    else:
        form = UserCreationForm()
        context = {
            'form': form,
            'count1': count1,
            'notification1': notification1,
        }
        return render(request, 'customer/Comm_Cust.html', context)


# def Comm_Cust(request):
#     Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     Emp_id = request.user.id
#     Cust_type = 'Commersial'
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             group = Group.objects.get(name='Customers')
#             user.groups.add(group)
#             Comp_name = request.POST['Comp_name']
#             Consumer = request.POST['Consumer']
#             Bill_unit = request.POST['Bill_unit']
#             first_name = request.POST['first_name']
#             middle_name = request.POST['middle_name']
#             last_name = request.POST['last_name']
#             Address = request.POST['Address']
#             Plant_Capacity = int(request.POST['Plant_Capacity'])
#             Ups_Soft = request.POST['Ups_Soft']
#             City = request.POST['City']
#             email = request.POST['email']
#             phone = int(request.POST['phone'])
#             Cus_Act_Date = request.POST['Cus_Act_Date']
#             solar_comp = request.POST['solar_comp']
#             UPSC = request.POST['UPSC']
#             state = request.POST['state']
#             Pincode = int(request.POST['Pincode'])
#             Gender = request.POST.get('Gender')
#
#             new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, Bill_unit=Bill_unit,
#                                 first_name=first_name, middle_name=middle_name, last_name=last_name,
#                                 Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
#                                 City=City, email=email, phone=phone, Cus_Act_Date=Cus_Act_Date, solar_comp=solar_comp,
#                                 UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, Gender=Gender, new_customer=user)
#             new_cust.save()
#             messages.success(request, 'New customer enrolled successfully')
#             return redirect('customer-Comm_Cust')
#         else:
#             messages.error(request, 'Please correct the errors below')
#     else:
#         form = UserCreationForm()
#     context = {
#         'form': form,
#         'count1': count1,
#         'notification1': notification1,
#     }
#     return render(request, 'customer/Comm_Cust.html', context)

@login_required(login_url='user-login')
def Comp_Cust(request):
    Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    Emp_id = request.user.id
    Cust_type = 'Company'
    if request.method == 'POST':
        # Create a new user first
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = request.POST['email']  # Add email to user object
            user.save()
            # Add the user to the 'Customers' group
            group = Group.objects.get(name='Customers')
            user.groups.add(group)
            #Cust_id = int(request.POST['Cust_id'])
            Comp_name = request.POST['Comp_name']
            Consumer= request.POST['Consumer']
            Bill_unit= request.POST['Bill_unit']
            Address= request.POST['Address']
            Plant_Capacity=int(request.POST['Plant_Capacity'])
            Ups_Soft= request.POST['Ups_Soft']
            #Cust_type= request.POST['Cust_type']
            City= request.POST['City']
            email= request.POST['email']
            phone=int(request.POST['phone'])
            Cus_Act_Date=(request.POST['Cus_Act_Date'])
            solar_comp= request.POST['solar_comp']
            UPSC= request.POST['UPSC']
            #Emp_id= int(request.POST['Emp_id'])
            state= request.POST['state']
            Pincode=int(request.POST['Pincode'])
            loadsancution = request.POST['loadsancution']

            new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, Bill_unit=Bill_unit,
                                Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
                                City=City, email=email, phone=phone, Cus_Act_Date=Cus_Act_Date, solar_comp=solar_comp,
                                UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user, loadsancution=loadsancution)
            new_cust.save()
            messages.info(request, 'New Customer enrolled Successfully')
            cust = Customer.objects.all()
            if Cust_id:
                cust = cust.filter(Cust_id=Cust_id)
                context = {
                    'count1': count1,
                    'cust': cust,
                    'notification1': notification1,
                }
                return render(request, 'customer/Comp_Cust.html', context)
    else:
        form = UserCreationForm()
        context = {
             'form': form,
             'count1': count1,
              'notification1': notification1,
        }
        return render(request, 'customer/Comp_Cust.html', context)


@login_required(login_url='user-login')
def Govt_Cust(request):
    Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    Emp_id = request.user.id
    Cust_type = 'Goverment'
    if request.method == 'POST':
        # Create a new user first
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = request.POST['email']  # Add email to user object
            #user.set_password('admin@123')  # Set password to 'admin@123'
            user.save()
            # Add the user to the 'Customers' group
            group = Group.objects.get(name='Customers')
            user.groups.add(group)
            #Cust_id = int(request.POST['Cust_id'])
            Comp_name = request.POST['Comp_name']
            Consumer= request.POST['Consumer']
            Bill_unit= request.POST['Bill_unit']
            Address= request.POST['Address']
            Plant_Capacity=int(request.POST['Plant_Capacity'])
            Ups_Soft= request.POST['Ups_Soft']
            #Cust_type= request.POST['Cust_type']
            City= request.POST['City']
            email= request.POST['email']
            phone=int(request.POST['phone'])
            Cus_Act_Date=(request.POST['Cus_Act_Date'])
            solar_comp= request.POST['solar_comp']
            UPSC= request.POST['UPSC']
            #Emp_id= int(request.POST['Emp_id'])
            state= request.POST['state']
            Pincode=int(request.POST['Pincode'])
            Gender= request.POST.get('Gender')
            loadsancution = request.POST['loadsancution']

            new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, Bill_unit=Bill_unit,
                                Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
                                City=City, email=email, phone=phone, Cus_Act_Date=Cus_Act_Date, solar_comp=solar_comp,
                                UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user, loadsancution=loadsancution)
            new_cust.save()

            messages.info(request, 'New Consumer enrolled Successfully')
            cust = Customer.objects.all()
            if Cust_id:
                cust = cust.filter(Cust_id=Cust_id)
                context = {
                    'count1': count1,
                    'cust': cust,
                    'notification1': notification1,
                }
                return render(request, 'customer/Govt_Cust.html', context)
           # return HttpResponseRedirect(request, 'customer/Govt_Cust.html', context)
    else:
        form = UserCreationForm()
        context = {
            'form': form,
            'count1': count1,
            'notification1': notification1,
        }
        return render(request, 'customer/Govt_Cust.html', context)


    # # Get the latest customer ID and increment it by 1
    # Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
    # count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    # notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    # Emp_id = request.user.id
    # Cust_type = 'Goverment'
    #
    # if request.method == 'POST':
    #     # Create a new user first
    #     form = UserCreationForm(request.POST)
    #     if form.is_valid():
    #         user = form.save()
    #         # Add the user to the 'Customers' group
    #         group = Group.objects.get(name='Customers')
    #         user.groups.add(group)
    #         # Get the form data for creating a new customer
    #         Comp_name = request.POST['Comp_name']
    #         Consumer= request.POST['Consumer']
    #         Bill_unit= request.POST['Bill_unit']
    #         Address= request.POST['Address']
    #         Plant_Capacity=int(request.POST['Plant_Capacity'])
    #         Ups_Soft= request.POST['Ups_Soft']
    #         #Cust_type= request.POST['Cust_type']
    #         City= request.POST['City']
    #         email= request.POST['email']
    #         phone=int(request.POST['phone'])
    #         Cus_Act_Date=(request.POST['Cus_Act_Date'])
    #         solar_comp= request.POST['solar_comp']
    #         UPSC= request.POST['UPSC']
    #         #Emp_id= int(request.POST['Emp_id'])
    #         state= request.POST['state']
    #         Pincode=int(request.POST['Pincode'])
    #         Gender= request.POST.get('Gender')
    #
    #         try:
    #             # Create a new customer with the user ID
    #             new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, Bill_unit=Bill_unit,
    #                                 Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft,
    #                                 Cust_type=Cust_type, City=City, email=email, phone=phone, Cus_Act_Date=Cus_Act_Date,
    #                                 solar_comp=solar_comp, UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode,
    #                                 user=user)
    #             new_cust.save()
    #             messages.info(request, 'New Customer enrolled Successfully')
    #             cust = Customer.objects.all()
    #             if Cust_id:
    #                 cust = cust.filter(Cust_id=Cust_id)
    #                 context = {
    #                     'count1': count1,
    #                     'cust': cust,
    #                     'notification1': notification1,
    #                 }
    #                 return render(request, 'customer/Govt_Cust.html', context)
    #                 return HttpResponseRedirect("customer/Govt_Cust")
    #         except:
    #             return HttpResponse("Please Enter Data")
    # else:
    #     form = UserCreationForm()
    # context = {
    #     'form': form,
    #     'count1': count1,
    #     'notification1': notification1,
    # }
    # return render(request, 'customer/Govt_Cust.html', context)


@login_required(login_url='user-login')
def showresults(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if request.method == "POST":
        #name = request.POST('name')
        fromdate = request.POST.get('fromdate')
        Todate = request.POST.get('Todate')
        City = request.POST.get('City')
        Cust_type = request.POST.get('Cust_type')
        searchresult = Customer.objects.raw('select Cust_id,first_name,last_name,City,state,phone,Plant_Capacity,Cus_Act_Date,Cust_type from emp_app_customer where City ="'+City+'" or City="" and Cust_type ="'+Cust_type+'" or Cust_type="" and Cus_Act_Date between"'+fromdate+'" and "'+Todate+'"')
        return render(request, 'customer/Cust_Search.html', {"data": searchresult, "count1": count1})
    else:
        displaydata = Customer.objects.all()
        return render(request, 'customer/Cust_Search.html', {"data": displaydata, "count1": count1, "notification1": notification1})

    # elif request.method == 'GET':
    #     displaydata = Customer.objects.all()
    #     return render(request, 'Cust_Search.html', {"data": displaydata})
    #
    # # else:
    # #     return HttpResponse('An Exception Occurred')



@login_required(login_url='user-login')
def view_all_cust(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if request.method == 'POST':
        # name = request.POST['name']
        # dept = request.POST['dept']
        name = request.POST.get('name', None)
        dept = request.POST.get('dept', None)

        emps = Customer.objects.all()
        if name:
             emps = emps.filter(Q(Comp_name__icontains=name)| Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(phone__icontains=name) | Q(state__icontains=name) | Q(City__icontains=name) | Q(Cust_id__icontains=name))
        if dept:
            emps = emps.filter(Q(Cust_type__icontains=dept))
        context = {
            'emps': emps,
            'count1': count1,
            'notification1': notification1,
        }
        #print(dept)
        return render(request, 'customer/view_all_cust.html', context)
    elif request.method == 'GET':
        emps = Customer.objects.all()
        context = {
                'emps': emps,
            'count1': count1,
            'notification1': notification1,
            }
        return render(request, 'customer/view_all_cust.html', context)
    else:
        return HttpResponse('An Exception Occurred')

    # else:
    #     emps = Customer.objects.all()
    #     context = {
    #         'emps': emps
    #     }
    #     return render(request, 'customer/view_all_cust.html', context)

@login_required(login_url='user-login')
def view_all(request):

        totalIndividual = Customer.objects.filter(Cust_type='Indivisual').count()
        totalComersial = Customer.objects.filter(Cust_type='Commersial').count()
        totalCompany = Customer.objects.filter(Cust_type='Company').count()
        totalGoverment = Customer.objects.filter(Cust_type='Goverment').count()
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

        customer_type = request.GET.get('Cust_type')

        customers = Customer.objects.all()

        if customer_type:
            customers = Customer.objects.filter(Cust_type=customer_type)


        return render(request, 'customer/index.html', locals())



    # elif request.method == 'GET':
    #     customers = Customer.objects.all()
    #     context = {
    #             'customers': customers
    #         }
    #     return render(request, 'customer/view_all_cust.html', context)
    # else:
    #     return HttpResponse('An Exception Occurred')

    # else:
    #     emps = Customer.objects.all()
    #     context = {
    #         'emps': emps
    #     }
    #     return render(request, 'customer/view_all_cust.html', context)




@login_required(login_url='user-login')
def customer_update(request, Cust_id):

    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    customer = Customer.objects.get(Cust_id=Cust_id)

    # form = UserCreationForm(request.POST)
    # if form.is_valid():
    #     user = form.save(commit=False)
    #     user.email = request.POST['email']  # Add email to user object
    #     # user.set_password('admin@123')  # Set password to 'admin@123'
    #     user.save()

    if 'firstname' in request.POST:
        firstname = request.POST['firstname']
    else:
        firstname = None

    if 'lastname' in request.POST:
        lastname = request.POST['lastname']
    else:
        lastname = None

    if 'gender' in request.POST:
        gender = request.POST['gender']
    else:
        gender = None

    if 'compname' in request.POST:
        compname = request.POST['compname']
    else:
        compname = None

    if 'email' in request.POST:
        email = request.POST['email']
    else:
        email = None

    if request.method == "POST":
        ct = request.POST['custtype']
        cid = request.POST['custid']
        pc = request.POST['plantcapacity']
        sc = request.POST['solarcomp']
        upsc = request.POST['UPSC']
        phase = request.POST['phase']
        cad = request.POST['Cusactdate']
        ph = request.POST['phone']
        email = request.POST['email']
        add = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pin = request.POST['pincode']
        con = request.POST['consumer']
        bu = request.POST['billunit']
        ls = request.POST['loadsancution']
        us = request.POST['upssoft']

        customer.Comp_name = compname
        customer.Ups_Soft = us
        customer.first_name = firstname
        customer.last_name = lastname
        customer.Gender = gender
        customer.Cust_type = ct
        customer.Cust_id = cid
        customer.Plant_Capacity = pc
        customer.solar_comp = sc
        customer.UPSC = upsc
        customer.phone = ph
        customer.phase = phase
        customer.email = email
        customer.Address = add
        customer.City = city
        customer.state = state
        customer.Pincode = pin
        customer.Consumer = con
        customer.Bill_unit = bu
        customer.loadsancution = ls

        if cad:
            customer.Cus_Act_Date = cad


        try:

            # user.set_password('admin@123')  # Set password to 'admin@123'

            customer.save()
            # user = User.objects.get(email=email)
            # user.email = email
            # user.save()
            # print(customer.Gender, customer.phase, customer.loadsancution, customer.Cus_Act_Date, customer.Bill_unit,
            #       customer.Consumer, customer.Pincode, customer.state, customer.City, customer.email, customer.phone,
            #       customer.UPSC, customer.solar_comp, customer.Comp_name, customer.Cust_id, customer.Cust_type,
            #       customer.last_name, customer.first_name)
            error="no"
        except:
            error="yes"
    return render(request, 'customer/customer_update.html', locals())


@login_required(login_url='user-login')
def customer_updatepage(request, Cust_id):
    #customer = get_object_or_404(Customer, Cust_id=Cust_id)
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    customer = Customer.objects.get(Cust_id=Cust_id)
    #id = customer.Emp_id
    # context = {
    #     'customer': customer,
    #     'user1': user1,
    # }

    return render(request, 'customer/customer_updatepage.html', locals())


# def Site_Technical_Details(request):
#     companies = Customer.objects.all()
#     if request.method == 'POST':
#         # Process the form data here
#         # Retrieve the form data using request.POST.get() method
#
#         # Example:
#         company_name = request.POST.get('comp_name')
#         solar_panel_no = request.POST.get('solar_panel_no')
#         detected_barcode = request.POST.get('detected_barcode')
#         detected_inverter = request.POST.get('detected_inverter')
#         meter_image = request.FILES.get('meter_image')
#         netmeter_image = request.FILES.get('netmeter_image')
#         abt_meter_image = request.FILES.get('abt_meter_image')
#         ct_cubic_image = request.FILES.get('ct_cubic_image')
#         new_customer_id = request.POST.get('new_customer_id')
#
#         if new_customer_id.isdigit():
#             assign_to_user = User.objects.get(id=new_customer_id)
#         else:
#             assign_to_user = None
#
#         print(meter_image)
#         from django.db import IntegrityError
#
#         new_customer_technical_details = customer_technical_Details.objects.create(
#                 company_name=company_name,
#                 # solar_panel_no=solar_panel_no,
#                 #detected_barcode=detected_barcode,
#                 #detected_inverter=detected_inverter,
#                 meter_image=meter_image,
#                 netmeter_image=netmeter_image,
#                 abt_meter_image=abt_meter_image,
#                 ct_cubic_image=ct_cubic_image,
#                 AssignTo=assign_to_user,
#                 AssignBy=request.user
#             )
#
#
#         # Perform further processing or save the data as required
#
#     # return render(request, 'customer/Site_Technical_Details.html')
#     return render(request, 'customer/Site_Technical_Details.html', locals())
#


@login_required(login_url='user-login')
def Site_Technical_Details(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    companies = Customer.objects.all()

    if request.method == 'POST':
        # Process the form data here
        # Retrieve the form data using request.POST.get() method

        # Example:
        company_name = request.POST.get('comp_name')
        solar_panel_no = request.POST.get('solar_panel_no')
        detected_barcode = request.POST.get('detected_barcode')
        detected_inverter = request.POST.get('detected_inverter')
        meter_image = request.FILES.get('meter_image')
        netmeter_image = request.FILES.get('netmeter_image')
        abt_meter_image = request.FILES.get('abt_meter_image')
        ct_cubic_image = request.FILES.get('ct_cubic_image')
        new_customer_id = request.POST.get('new_customer_id')

        if new_customer_id.isdigit():
            assign_to_user = User.objects.get(id=new_customer_id)
        else:
            assign_to_user = None
        from django.db import IntegrityError

        try:
            new_customer_technical_details = customer_technical_Details.objects.create(
                company_name=company_name,
                # solar_panel_no=solar_panel_no,
                # detected_barcode=detected_barcode,
                # detected_inverter=detected_inverter,
                meter_image=meter_image,
                netmeter_image=netmeter_image,
                abt_meter_image=abt_meter_image,
                ct_cubic_image=ct_cubic_image,
                AssignTo=assign_to_user,
                AssignBy=request.user
            )

            # Perform further processing or save the data as required

            messages.success(request, 'Data saved successfully.')  # Add success message

            return redirect('customer-Site_Technical_Details')  # Redirect to a success page after saving the record

        except IntegrityError as e:
            # Handle any IntegrityError exceptions, such as unique constraint violations
            print(f"Error saving customer technical details: {str(e)}")
            messages.error(request, 'An error occurred while saving the data.')  # Add error message

    return render(request, 'customer/Site_Technical_Details.html', locals())


# ================== genrate consumer list pdf ==================

from .forms import consumerGenerationForm


@login_required(login_url='user-login')
def consumer_pdf(request):
    if request.method == 'POST':
        form = consumerGenerationForm(request.POST)
        if form.is_valid():
            customer_type_filter = request.POST.get('userType')

            # Define the base queryset
            base_queryset = Customer.objects.all()

            # Apply filters based on the selected user type
            if customer_type_filter == 'Residential':
                base_queryset = base_queryset.filter(Cust_type='Indivisual')
            elif customer_type_filter == 'Commersial':
                base_queryset = base_queryset.filter(Cust_type='Commersial')
            elif customer_type_filter == 'Industrial':
                base_queryset = base_queryset.filter(Cust_type='Company')
            elif customer_type_filter == 'Goverment':
                base_queryset = base_queryset.filter(Cust_type='Goverment')

            selected_customer_fields = form.cleaned_data['customer_fields']
            #selected_profile_fields = form.cleaned_data['profile_fields']

            # Check if at least one field from either User or Profile is selected
            if not (selected_customer_fields):
                return HttpResponse("Please select at least one field from User or Profile to generate the PDF.")

            # Fetch the filtered users based on the selected user type
            users = base_queryset

            # Define custom field names
            field_display_names = {
                'Comp_name': 'Company Name',
                'username': 'Username',
                'first_name': 'First Name',  # Map 'id' field to 'ID'
                'phone': 'Contact No',
                'Plant_Capacity': 'Plant Capacity',
                'Ups_Soft': 'Inverter Software Used',
                'City': 'City',
                'email': 'Email ID',
                'Address': 'Address',
                'city': 'City',
                'Cus_Act_Date': 'Installation Date',
                'solar_comp': 'Solar Plate Company',
                'UPSC': 'Inverter Company',
                'state': 'State',
                'Pincode': 'Pincode',
                'phase': 'Phase',
                'loadsancution': 'Sancution Load',
                'Cust_id': 'ID',
                'new_customer': 'Username',
                'Cust_type': 'Consumer Type',

                # Add more mappings as needed
            }

            custom_customer_fields = ['Full Name'] if 'full_name' in selected_customer_fields else []

            for field in selected_customer_fields:
                if field in field_display_names and field != 'full_name':
                    custom_customer_fields.append(field_display_names[field])

           # custom_profile_fields = [field_display_names.get(field, field) for field in selected_profile_fields]

            data = []
            for customer in users:
                customer_profile = customer.profile if hasattr(customer, 'profile') else None
                print(f'User ID: {customer.Cust_id}, Customer ID: {customer_profile.customer_id if customer_profile else "N/A"}')

                customer_profile = customer.profile if hasattr(customer, 'profile') else None
                full_name = f"{customer.first_name} {customer.last_name}" if 'full_name' in selected_customer_fields else ""
                customer_fields_data = {
                    # 'Cust_id': customer_profile.Cust_id if customer_profile else '',  # Access 'customer_id' from profile
                    'Cust_id': customer.Cust_id,
                    'Full Name': full_name,
                }
                customer_fields_data.update({field_display_names.get(field, field): getattr(customer, field, "") for field in selected_customer_fields if field != 'full_name'})
              #  profile_fields_data = {field_display_names.get(field, field): getattr(user_profile, field, "") for field in selected_profile_fields} if user_profile else {}
                customer_data = {
                    'customer_fields': customer_fields_data,
                   # 'profile_fields': profile_fields_data,
                }
                data.append(customer_data)
            logo_path = "media/static/images/dblogo2001.png"  # Replace with the actual path to your logo image
            top_margin_height = 0.25  # Adjust this value as needed

            # Call the PDF generation function with the data
            return consumer_print(request, custom_customer_fields, data, logo_path, top_margin_height, customer_type_filter)
    else:
        form = consumerGenerationForm()

    return render(request, 'customer/consumer_list.html', {'form': form})




from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Spacer, Paragraph
from datetime import datetime

@login_required(login_url='user-login')
def consumer_print(request, customer_fields, data, logo_path, top_margin_height=0.25, customer_type_filter=""):
    buffer = BytesIO()

    # Determine the page size based on the number of fields
    if len(customer_fields) > 3:
        page_size = landscape(letter)
    else:
        page_size = portrait(letter)

    # pdf = SimpleDocTemplate(buffer, pagesize=page_size, topMargin=top_margin_height * inch)

    # Define top and bottom margins
    top_margin_height = 0.25  # Top margin in inches
    bottom_margin_height = 0.25  # Bottom margin in inches
    page_height = page_size[1]  # Get the page height
    remaining_height = page_height - (top_margin_height + bottom_margin_height)

    pdf = SimpleDocTemplate(buffer, pagesize=page_size, topMargin=top_margin_height * inch, bottomMargin=bottom_margin_height * inch )

    elements = []

    # Create a custom style for the caption
    caption_style = ParagraphStyle(
        name='CaptionStyle',
        fontSize=14,  # Adjust the font size as needed
        fontName='Helvetica-Bold',  # Use a bold font
        spaceAfter=12,  # Add space after the caption
        alignment=1,  # Center-align the caption text
    )

    # Determine the caption text based on the selected_option
    if customer_type_filter == "all":
        caption_text = "List Type: All Consumer List"
    elif customer_type_filter == "Residential":
        caption_text = "List Type: Residential Consumer List"
    elif customer_type_filter == "Commersial":
        caption_text = "List Type: Commersial Consumer List"
    elif customer_type_filter == "Industrial":
        caption_text = "List Type: Industrial Consumer List"
    elif customer_type_filter == "Goverment":
        caption_text = "List Type: Goverment Consumer List"
    else:
        caption_text = "Unknown List"  # Add a default caption for unknown options

    caption = Paragraph(caption_text, caption_style)

    # Create table data for all user data
    table_data = [['Sr No', 'Cons.ID'] + customer_fields]  # Change 'ID' to 'Cust ID'

    for index, customer_data in enumerate(data, start=1):
        row = [index, customer_data['customer_fields'].get('Cust_id')]  # Change 'ID' to 'Cust_id'

        for field in customer_fields:
            if field == 'Installation Date':
                # Format the "Installation Date" to 'dd-mm-yy'
                installation_date = customer_data['customer_fields'].get(field, "")
                if installation_date:
                    installation_date = installation_date.strftime('%d-%m-%y')
                row.append(installation_date)
            elif field == 'Plant Capacity':
                # Add "Kw" label to the "Plant Capacity" field
                plant_capacity = customer_data['customer_fields'].get(field, "")
                row.append(f"{plant_capacity}  Kw")
            else:
                row.append(customer_data['customer_fields'].get(field, ""))

        # row.extend([customer_data['customer_fields'].get(field, "") for field in customer_fields if
        #             field != 'Cust_id'])  # Exclude 'Cust_id'
        # # row.extend([user_data['profile_fields'].get(field, "") for field in profile_fields if field != 'customer_id'])
        table_data.append(row)

    table = Table(table_data)
    style = TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center-align the first row
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Add a background color to the first row
                        ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # Center-align the Sr No and Emp ID columns
                        ])
    table.setStyle(style)

    # Add the company logo at the top of the page
    logo = Image(logo_path, width=5.5 * inch, height=0.70 * inch)
    logo.hAlign = 'CENTER'

    # Create a Spacer for spacing between elements
    spacer = Spacer(1, 0.25 * inch)

    # Create a Paragraph for the current date
    current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    current_date_style = ParagraphStyle(
        name='CurrentDateStyle',
        fontSize=10,
        fontName='Helvetica',
        alignment=1,  # Center-align the current date
    )
    current_date_paragraph = Paragraph(current_date, current_date_style)

    # Add elements to the content
    elements.extend([logo, caption, current_date_paragraph, spacer, table])

    pdf.build(elements)

    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
    # Construct the filename based on the user_type_filter
    response['Content-Disposition'] = f'attachment; filename ={customer_type_filter}_pdf.pdf'


    response.write(buffer.getvalue())
    buffer.close()

    return response



# =========== adjust the column width of Address and Comp_name field ===========

# from reportlab.lib.pagesizes import letter, landscape, portrait
# from reportlab.lib import colors
# from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Spacer, Paragraph
# from datetime import datetime
#
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.pagesizes import letter, landscape, portrait
# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Image, Table, TableStyle
# from reportlab.lib.styles import ParagraphStyle
# from datetime import datetime
# from io import BytesIO
# from django.http import HttpResponse

# def consumer_print(request, customer_fields, data, logo_path, top_margin_height=0.25, customer_type_filter=""):
#     buffer = BytesIO()
#
#     # Determine the page size based on the number of fields
#     if len(customer_fields) > 3:
#         page_size = landscape(letter)
#     else:
#         page_size = portrait(letter)
#
#     # Define top and bottom margins
#     top_margin_height = 0.25  # Top margin in inches
#     bottom_margin_height = 0.25  # Bottom margin in inches
#     page_height = page_size[1]  # Get the page height
#     remaining_height = page_height - (top_margin_height + bottom_margin_height)
#
#     pdf = SimpleDocTemplate(buffer, pagesize=page_size, topMargin=top_margin_height * inch, bottomMargin=bottom_margin_height * inch )
#
#     elements = []
#
#     # Create a custom style for the caption
#     caption_style = ParagraphStyle(
#         name='CaptionStyle',
#         fontSize=14,  # Adjust the font size as needed
#         fontName='Helvetica-Bold',  # Use a bold font
#         spaceAfter=12,  # Add space after the caption
#         alignment=1,  # Center-align the caption text
#     )
#
#     # Determine the caption text based on the selected_option
#     if customer_type_filter == "all":
#         caption_text = "List Type: All Consumer List"
#     elif customer_type_filter == "Residential":
#         caption_text = "List Type: Residential Consumer List"
#     elif customer_type_filter == "Commersial":
#         caption_text = "List Type: Commercial Consumer List"
#     elif customer_type_filter == "Industrial":
#         caption_text = "List Type: Industrial Consumer List"
#     elif customer_type_filter == "Government":
#         caption_text = "List Type: Government Consumer List"
#     else:
#         caption_text = "Unknown List"  # Add a default caption for unknown options
#
#     caption = Paragraph(caption_text, caption_style)
#
#     # Create table data for all user data
#     table_data = [['Sr No', 'Cons.ID'] + customer_fields]  # Change 'ID' to 'Cust ID'
#
#     # Define the column widths for specific fields (adjust as needed)
#     sr_no_width = 0.5 * inch
#     cons_id_width = 0.75 * inch
#
#     # Add fixed column widths for Comp_name and Address (adjust as needed)
#     comp_name_width = 1.5 * inch
#     address_width = 1.5 * inch
#
#     # Calculate the remaining width for the other columns
#     remaining_width = page_size[0] - (sr_no_width + cons_id_width + comp_name_width + address_width)
#     num_other_columns = len(customer_fields) - 2  # Subtract Sr No and Cons.ID
#     other_column_width = remaining_width / num_other_columns
#
#     # Update the column widths list with the fixed widths
#     column_widths = [sr_no_width, cons_id_width, comp_name_width, address_width]
#     for _ in range(num_other_columns):
#         column_widths.append(other_column_width)
#
#     for index, customer_data in enumerate(data, start=1):
#         row = [index, customer_data['customer_fields'].get('Cust_id')]  # Change 'ID' to 'Cust_id'
#
#         for field in customer_fields:
#             if field == 'Installation Date':
#                 # Format the "Installation Date" to 'dd-mm-yy'
#                 installation_date = customer_data['customer_fields'].get(field, "")
#                 if installation_date:
#                     installation_date = installation_date.strftime('%d-%m-%y')
#                 row.append(installation_date)
#             elif field == 'Plant Capacity':
#                 # Add "Kw" label to the "Plant Capacity" field
#                 plant_capacity = customer_data['customer_fields'].get(field, "")
#                 row.append(f"{plant_capacity} Kw")
#             elif field in ['Comp_name', 'Address']:
#                 # Set nowrap for Comp_name and Address fields
#                 style = getSampleStyleSheet()["Normal"]
#                 style.wordWrap = 'nowrap'
#                 cell_content = customer_data['customer_fields'].get(field, "")
#                 p = Paragraph(cell_content, style)
#                 row.append(p)
#             else:
#                 row.append(customer_data['customer_fields'].get(field, ""))
#
#         table_data.append(row)
#
#     table = Table(table_data, colWidths=column_widths)
#     style = TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#                         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
#                         ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center-align the first row
#                         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Add a background color to the first row
#                         ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # Center-align the Sr No and Cons ID columns
#                         ])
#     table.setStyle(style)
#
#     # Add the company logo at the top of the page
#     logo = Image(logo_path, width=6.5 * inch, height=1.0 * inch)
#     logo.hAlign = 'CENTER'
#
#     # Create a Spacer for spacing between elements
#     spacer = Spacer(1, 0.25 * inch)
#
#     # Create a Paragraph for the current date
#     current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
#     current_date_style = ParagraphStyle(
#         name='CurrentDateStyle',
#         fontSize=10,
#         fontName='Helvetica',
#         alignment=1,  # Center-align the current date
#     )
#     current_date_paragraph = Paragraph(current_date, current_date_style)
#
#     # Add elements to the content
#     elements.extend([logo, caption, current_date_paragraph, spacer, table])
#
#     pdf.build(elements)
#
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
#     response.write(buffer.getvalue())
#     buffer.close()
#
#     return response
