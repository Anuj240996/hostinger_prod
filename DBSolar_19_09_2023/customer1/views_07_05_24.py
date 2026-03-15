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
import uuid
from io import BytesIO

from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from detect_barcodes.models import BarcodeImage
from user.models import Profile
from .models import customer_technical_Details, Meter, Meters, GenerationMeter, GenerationCT
from django.shortcuts import redirect
from .models import MSEB

from datetime import datetime, timedelta
import datetime
from datetime import datetime


from django.shortcuts import render
from django.http import JsonResponse
from .models import Customer
#from urllib.parse import quote as urlquote


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
from django.db.models import Q, Max, Count
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
    Cust_type = 'Residential'
    # Emp_id = request.user.id
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    # engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers')
    engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')
    # cities = Customer.objects.values_list('City', flat=True).distinct()
    cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')

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
            current_load= request.POST['Bill_unit']
            first_name= request.POST['first_name']
            middle_name= request.POST['middle_name']
            last_name= request.POST['last_name']
            Address= request.POST['Address']
            Plant_Capacity=int(request.POST['Plant_Capacity'])
            Ups_Soft= request.POST['Ups_Soft']
            #Cust_type= request.POST['Cust_type']
            #City= request.POST['City']
            email= request.POST['email']
            phone=int(request.POST['phone'])
            # Cus_Act_Date=(request.POST['Cus_Act_Date'])
            solar_comp= request.POST['solar_comp']
            UPSC= request.POST['UPSC']
            #Emp_id= int(request.POST['Emp_id'])
            state= request.POST['state']
            Pincode=int(request.POST['Pincode'])
            # Gender= request.POST.get('Gender')
            loadsancution = request.POST['loadsancution']
            po_date = (request.POST['po_date'])
            po_order = request.POST['po_order']
            qunt_solar = request.POST['qunt_solar']
            qunt_inv = request.POST['qunt_inv']
            Teamid = request.POST['Engineer_Assigned']
            city_name = request.POST.get('city_name')
            new_city_name = request.POST.get('new_city_name')
            Emp_id = request.user
            sol_warranty = request.POST['sol_warranty']
            inv_warranty = request.POST['inv_warranty']
            com_warranty = request.POST['com_warranty']
            if city_name == "Other" and new_city_name:
                # Check if the new city already exists in the database
                existing_city = Customer.objects.filter(City=new_city_name).first()
                if not existing_city:
                    city_name = new_city_name
                else:
                    city_name = new_city_name

            if Teamid:
                team1 = User.objects.get(id=Teamid)
            else:
                team1 = 1

            new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load, first_name=first_name, middle_name=middle_name, last_name=last_name,
                                Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
                                City=city_name, email=email, phone=phone, solar_comp=solar_comp,
                                UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user, loadsancution=loadsancution, po_date=po_date, po_order=po_order,
                                Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty, inv_warranty=inv_warranty, com_warranty=com_warranty)
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
        return HttpResponse("Form is not valid")  # Add this line
    else:
        form = UserCreationForm()
        context = {
            'form': form,
            'count1': count1,
            'notification1': notification1,
            'engineers': engineers,
            'cities': cities,
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
    # Emp_id = request.user.id
    # #Engineers = Profile.objects.filter(department='Engineer').values_list('customer_id', flat=True),
    # #engineers = Profile.objects.filter(department='Engineer').values_list('name', flat=True).distinct()
    # engineers = Profile.objects.filter(department='Engineers').values_list('customer_id__first_name',
    #                                                                          'customer_id__last_name').distinct()
    # # Fetch unique first_name and last_name values from the 'user' ForeignKey in the Profile table
    # engineer_names = [f"{first_name} {last_name}" for first_name, last_name in engineers]

    # engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers')
    engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')
    # cities = Customer.objects.values_list('City', flat=True).distinct()
    cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')

    Cust_type = 'Commersial'
    if request.method == 'POST':
        # Create a new user first
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # username = request.POST['username']  # Get the entered username
            # # Check if the username already exists
            # if User.objects.filter(username=username).exists():
            #     messages.error(request, 'Username is already taken. Please choose a different one.')
            # else:
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
            current_load = request.POST['Bill_unit']
            first_name = request.POST['first_name']
            middle_name = request.POST['middle_name']
            last_name = request.POST['last_name']
            Address = request.POST['Address']
            Plant_Capacity = int(request.POST['Plant_Capacity'])
            Ups_Soft = request.POST['Ups_Soft']
            # Cust_type= request.POST['Cust_type']
           # City = request.POST['City']
            phone = int(request.POST['phone'])
            # Cus_Act_Date = request.POST['Cus_Act_Date']
            solar_comp = request.POST['solar_comp']
            UPSC = request.POST['UPSC']
            # Emp_id= int(request.POST['Emp_id'])
            state = request.POST['state']
            Pincode = int(request.POST['Pincode'])
            #Gender = request.POST.get('Gender')
            loadsancution = request.POST['loadsancution']
            po_date = (request.POST['po_date'])
            po_order = request.POST['po_order']
            qunt_solar = request.POST['qunt_solar']
            qunt_inv = request.POST['qunt_inv']
            Teamid = request.POST['Engineer_Assigned']
            city_name = request.POST.get('city_name')
            new_city_name = request.POST.get('new_city_name')
            Emp_id = request.user

            sol_warranty = request.POST['sol_warranty']
            inv_warranty = request.POST['inv_warranty']
            com_warranty = request.POST['com_warranty']

            if city_name == "Other" and new_city_name:
                # Check if the new city already exists in the database
                existing_city = Customer.objects.filter(City=new_city_name).first()
                if not existing_city:
                    city_name = new_city_name
                else:
                    city_name = new_city_name

            # print(Teamid)
            # team1 = User.objects.get(id=Teamid)

            if Teamid:
                team1 = User.objects.get(id=Teamid)
            else:
                # Set a default value for "Unknown" (you can choose an appropriate value)
                #team1 = User.objects.get(id=1)  # Assuming 1 represents "Unknown"
                team1 = 1

            new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load, first_name=first_name,
                                middle_name=middle_name, last_name=last_name, Address=Address, Plant_Capacity=Plant_Capacity,
                                Ups_Soft=Ups_Soft, Cust_type=Cust_type, City=city_name, email=user.email, phone=phone,
                                solar_comp=solar_comp, UPSC=UPSC, Emp_id=Emp_id, state=state,
                                Pincode=Pincode, new_customer=user, loadsancution=loadsancution, po_order=po_order, po_date=po_date,
                                Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty, inv_warranty=inv_warranty, com_warranty=com_warranty)
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
            return HttpResponse("Form is not valid")  # Add this line

    else:
        form = UserCreationForm()
        context = {
            'form': form,
            'count1': count1,
            'notification1': notification1,
            'engineers': engineers,
            'cities': cities,
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
    # Emp_id = request.user.id
    Cust_type = 'Industrial'
    # engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers')
    engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')
    #cities = Customer.objects.filter(City__isnull=False).distinct()
    # cities = Customer.objects.values_list('City', flat=True).distinct()
    cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')

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
            current_load= request.POST['Bill_unit']
            Address= request.POST['Address']
            Plant_Capacity=int(request.POST['Plant_Capacity'])
            Ups_Soft= request.POST['Ups_Soft']
            #Cust_type= request.POST['Cust_type']
            #City= request.POST['City']
            email= request.POST['email']
            phone=int(request.POST['phone'])
            # Cus_Act_Date=(request.POST['Cus_Act_Date'])
            solar_comp= request.POST['solar_comp']
            UPSC= request.POST['UPSC']
            #Emp_id= int(request.POST['Emp_id'])
            state= request.POST['state']
            Pincode=int(request.POST['Pincode'])
            loadsancution = request.POST['loadsancution']
            po_date = (request.POST['po_date'])
            po_order = request.POST['po_order']
            qunt_solar = request.POST['qunt_solar']
            qunt_inv = request.POST['qunt_inv']
            Teamid = request.POST['Engineer_Assigned']
            city_name = request.POST.get('city_name')
            new_city_name = request.POST.get('new_city_name')
            Emp_id = request.user

            sol_warranty = request.POST['sol_warranty']
            inv_warranty = request.POST['inv_warranty']
            com_warranty = request.POST['com_warranty']

            if city_name == "Other" and new_city_name:
                # Check if the new city already exists in the database
                existing_city = Customer.objects.filter(City=new_city_name).first()
                if not existing_city:
                 city_name = new_city_name
                else:
                  city_name = new_city_name

            if Teamid:
                team1 = User.objects.get(id=Teamid)
            else:
                team1 = 1

            new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load,
                                Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
                                City=city_name, email=email, phone=phone, solar_comp=solar_comp,
                                UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user, loadsancution=loadsancution, po_date=po_date, po_order=po_order,
                                Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty, inv_warranty=inv_warranty, com_warranty=com_warranty)
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
            return HttpResponse("Form is not valid")  # Add this line
    else:
        form = UserCreationForm()
        context = {
             'form': form,
             'count1': count1,
             'notification1': notification1,
             'engineers': engineers,
             'cities': cities,
        }
        return render(request, 'customer/Comp_Cust.html', context)


@login_required(login_url='user-login')
def Govt_Cust(request):
    Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    # Emp_id1 = request.user.username
    Cust_type = 'Goverment'
    # engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers')
    engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')
    # cities = Customer.objects.values_list('City', flat=True).distinct()
    cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')

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
            current_load= request.POST['Bill_unit']
            Address= request.POST['Address']
            Plant_Capacity=int(request.POST['Plant_Capacity'])
            Ups_Soft= request.POST['Ups_Soft']
            #Cust_type= request.POST['Cust_type']
            #City= request.POST['City']
            email= request.POST['email']
            phone=int(request.POST['phone'])
            # Cus_Act_Date=(request.POST['Cus_Act_Date'])
            solar_comp= request.POST['solar_comp']
            UPSC= request.POST['UPSC']
            #Emp_id= int(request.POST['Emp_id'])
            state= request.POST['state']
            Pincode=int(request.POST['Pincode'])
            Gender= request.POST.get('Gender')
            loadsancution = request.POST['loadsancution']
            po_date = (request.POST['po_date'])
            po_order = request.POST['po_order']
            qunt_solar = request.POST['qunt_solar']
            qunt_inv = request.POST['qunt_inv']
            Teamid = request.POST['Engineer_Assigned']
            city_name = request.POST.get('city_name')
            new_city_name = request.POST.get('new_city_name')
            Emp_id = request.user

            sol_warranty = request.POST['sol_warranty']
            inv_warranty = request.POST['inv_warranty']
            com_warranty = request.POST['com_warranty']

            if city_name == "Other" and new_city_name:
                # Check if the new city already exists in the database
                existing_city = Customer.objects.filter(City=new_city_name).first()
                if not existing_city:
                    city_name = new_city_name
                else:
                    city_name = new_city_name

            if Teamid:
                team1 = User.objects.get(id=Teamid)
            else:
                team1 = 1

            new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load,
                                Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
                                City=city_name, email=email, phone=phone, solar_comp=solar_comp,
                                UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user, loadsancution=loadsancution, po_date=po_date, po_order=po_order,
                                Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty, inv_warranty=inv_warranty, com_warranty=com_warranty)
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
            return HttpResponse("Form is not valid")  # Add this line
           # return HttpResponseRedirect(request, 'customer/Govt_Cust.html', context)
    else:
        form = UserCreationForm()
        context = {
            'form': form,
            'count1': count1,
            'notification1': notification1,
            'engineers': engineers,
            'cities': cities,
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



# @login_required(login_url='user-login')
# def view_all_cust(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     if request.method == 'POST':
#         # name = request.POST['name']
#         # dept = request.POST['dept']
#         name = request.POST.get('name', None)
#         dept = request.POST.get('dept', None)
#
#         emps = Customer.objects.all()
#         if name:
#              emps = emps.filter(Q(Comp_name__icontains=name)| Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(phone__icontains=name) | Q(state__icontains=name) | Q(City__icontains=name) | Q(Cust_id__icontains=name))
#         if dept:
#             emps = emps.filter(Q(Cust_type__icontains=dept))
#         context = {
#             'emps': emps,
#             'count1': count1,
#             'notification1': notification1,
#         }
#         #print(dept)
#         return render(request, 'customer/view_all_cust.html', context)
#     elif request.method == 'GET':
#         emps = Customer.objects.all()
#         context = {
#                 'emps': emps,
#             'count1': count1,
#             'notification1': notification1,
#             }
#         return render(request, 'customer/view_all_cust.html', context)
#     else:
#         return HttpResponse('An Exception Occurred')



    # else:
    #     emps = Customer.objects.all()
    #     context = {
    #         'emps': emps
    #     }
    #     return render(request, 'customer/view_all_cust.html', context)

from django.db.models import Q
from django.utils import timezone


@login_required(login_url='user-login')
def view_all_cust(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    mseb = MSEB.objects.all()

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
    emps = Customer.objects.all()
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

    if filter_option == 'Today':
        emps = emps.filter(po_date=today.date())
    elif filter_option == 'Last7Days':
        last_week = today - timezone.timedelta(days=7)
        emps = emps.filter(po_date__gte=last_week.date())
    elif filter_option == 'Last30Days':
        last_month = today - timezone.timedelta(days=30)
        emps = emps.filter(po_date__gte=last_month.date())
    elif filter_option == 'ThisMonth':
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        emps = emps.filter(po_date__gte=current_month.date())

    # Handle the custom range filter
    if filter_option == 'Custom' and start_date and end_date:
        emps = emps.filter(po_date__range=(start_date, end_date))

    if not request.user.is_superuser:
        emps = emps.filter(Engg_Assign_id=request.user)

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
        # if filter_option:
        #     emps = emps.filter(Q(po_date__icontains=filter_option))

        # Check if filter_option is not "Custom" before applying the filter
        if filter_option != 'Custom':
            today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

            if filter_option == 'Today':
                emps = emps.filter(po_date=today.date())
            elif filter_option == 'Last7Days':
                last_week = today - timezone.timedelta(days=7)
                emps = emps.filter(po_date__gte=last_week.date())
            elif filter_option == 'Last30Days':
                last_month = today - timezone.timedelta(days=30)
                emps = emps.filter(po_date__gte=last_month.date())
            elif filter_option == 'ThisMonth':
                current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                emps = emps.filter(po_date__gte=current_month.date())

        if not request.user.is_superuser:
            emps = emps.filter(Engg_Assign_id=request.user)

        context = {
            'emps': emps,
            'count1': count1,
            'notification1': notification1,
            'caption_text': caption_text,
            'caption_text1': caption_text1,
        }
        #print(dept)
        return render(request, 'customer/view_all_cust.html', context)
    elif request.method == 'GET':
        # emps = Customer.objects.all()

        context = {
            'mseb_record': mseb,
            'emps': emps,
            'count1': count1,
            'notification1': notification1,
            'caption_text': caption_text,
            'caption_text1': caption_text1,
            }
        return render(request, 'customer/view_all_cust.html', context)
    else:
        return HttpResponse('An Exception Occurred')






@login_required(login_url='user-login')
def view_all(request):

        totalIndividual = Customer.objects.filter(Cust_type='Residential').count()
        totalComersial = Customer.objects.filter(Cust_type='Commersial').count()
        totalCompany = Customer.objects.filter(Cust_type='Industrial').count()
        totalGoverment = Customer.objects.filter(Cust_type='Goverment').count()
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

        customer_type = request.GET.get('Cust_type')

        customers = Customer.objects.all()

        if customer_type:
            customers = Customer.objects.filter(Cust_type=customer_type)


        return render(request, 'customer/index.html', locals())


# @login_required(login_url='user-login')
# def view_all(request):
#
#         totalIndividual = Customer.objects.filter(Cust_type='Residential').count()
#         totalComersial = Customer.objects.filter(Cust_type='Commersial').count()
#         totalCompany = Customer.objects.filter(Cust_type='Industrial').count()
#         totalGoverment = Customer.objects.filter(Cust_type='Goverment').count()
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#
#
#         customers = Customer.objects.all()
#
#
#         # Get the filter option from the GET request
#         filter_option = request.GET.get('filter', 'All')
#         # today = timezone.now()
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight
#         start_date, end_date = None, None
#
#         # Get the start and end date for custom range from the GET request
#         start_date = request.GET.get('start_date')
#         end_date = request.GET.get('end_date')
#
#         # Determine the caption text based on the selected_option
#         if filter_option == "All":
#             caption_text = "Display All Days View"
#             caption_text1 = "Up To Date"
#             customer_type = request.GET.get('Cust_type')
#         elif filter_option == "Today":
#             # caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
#             # caption_text = "Display Today View"
#             start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = today
#             caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Today"
#             customer_type = request.GET.get('Cust_type')
#         elif filter_option == "Last7Days":
#             start_date = today - timezone.timedelta(days=7)
#             end_date = today
#             caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             # caption_text = "Display Last 7 Days View"
#             caption_text1 = "Last 7 Days"
#             customer_type = request.GET.get('Cust_type')
#         elif filter_option == "Last30Days":
#             start_date = today - timezone.timedelta(days=30)
#             end_date = today
#             caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             # caption_text = "Display Last 30 Days View"
#             caption_text1 = "Last 30 Days"
#             customer_type = request.GET.get('Cust_type')
#         elif filter_option == "ThisMonth":
#             start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#             end_date = today
#             caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             # caption_text = "Display This Month View"
#             caption_text1 = "This Month"
#             customer_type = request.GET.get('Cust_type')
#         elif filter_option == "Custom":
#             # caption_text = "Display Custome Range View  ('start_date')strtime('start_date')"
#             caption_text = "Display Custome Range View"
#             caption_text1 = "Custome Range"
#             customer_type = request.GET.get('Cust_type')
#         else:
#             caption_text = "The option is not selected so all Record Show"  # Add a default caption for unknown options
#             caption_text1 = ""
#
#
#         # Define a variable to store the filtered data
#         if customer_type:
#             customers = Customer.objects.filter(Cust_type=customer_type)
#         else:
#             customers = Customer.objects.all()
#
#
#         # customers = Customer.objects.filter(Cust_type=customer_type)
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight
#
#         if filter_option == 'Today':
#             # customers = customers.filter(po_date=today.date())
#             customers = customers.filter(
#                 Q(po_date__date=timezone.now().date()) &
#                 Q(Cust_type=customer_type)
#             )
#         elif filter_option == 'Last7Days':
#             last_week = today - timezone.timedelta(days=7)
#             # customers = customers.filter(po_date__gte=last_week.date())
#             customers = customers.filter(
#                 Q(po_date__gte=last_week.date()) &
#                 Q(Cust_type=customer_type)
#             )
#
#         elif filter_option == 'Last30Days':
#             last_month = today - timezone.timedelta(days=30)
#             # customers = customers.filter(po_date__gte=last_month.date())
#             customers = customers.filter(
#                 Q(po_date__gte=last_month.date()) &
#                 Q(Cust_type=customer_type)
#             )
#
#         elif filter_option == 'ThisMonth':
#             current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#             # customers = customers.filter(po_date__gte=current_month.date())
#             customers = customers.filter(
#                 Q(po_date__gte=current_month.date()) &
#                 Q(Cust_type=customer_type)
#             )
#
#         # Handle the custom range filter
#         if filter_option == 'Custom' and start_date and end_date:
#             # customers = customers.filter(po_date__range=(start_date, end_date))
#             customers = customers.filter(
#                 Q(po_date__date__range=(start_date, end_date)) &
#                 Q(Cust_type=customer_type)
#             )
#
#         if not request.user.is_superuser:
#             customers = customers.filter(Engg_Assign_id=request.user)
#
#
#
#         return render(request, 'customer/index.html', locals())
#




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
    # engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers')
    # Get all engineers
    # engineers = User.objects.filter(profile__department__isnull=False, profile__department='Engineers')
    engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')

    # If there's an assigned engineer, remove them from the list
    assigned_user = customer.Engg_Assign
    if assigned_user:
        # assigned_user = engineers.exclude(id=assigned_engineer.id)
        engineers = engineers.exclude(id=assigned_user.id) if assigned_user else User.objects.all()


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

    if 'Cusactdate' in request.POST:
        po_date = request.POST['Cusactdate']
    else:
        po_date = None

    # if 'Engineer_Assigned' in request.POST:
    #     Teamid = request.POST['Engineer_Assigned']
    # else:
    #     Teamid = None


    # Teamid = request.POST['Engineer_Assigned']

    if request.method == "POST":
        ct = request.POST['custtype']
        cid = request.POST['custid']
        pc = request.POST['plantcapacity']
        sc = request.POST['solarcomp']
        upsc = request.POST['UPSC']
        # phase = request.POST['phase']
        cad = request.POST['Cusactdate']
        ph = request.POST['phone']
        email = request.POST['email']
        add = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pin = request.POST['pincode']
        con = request.POST['consumer']
        # bu = request.POST['billunit']
        ls = request.POST['loadsancution']
        us = request.POST['upssoft']
        qunt_solar = request.POST['qunt_solar']
        qunt_inv = request.POST['qunt_inv']
        current_load = request.POST['current_load']
        Teamid = request.POST['Engineer_Assigned']
        sol_warranty = request.POST['sol_warranty']
        inv_warranty = request.POST['inv_warranty']
        com_warranty = request.POST['com_warranty']


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
        # customer.phase = phase
        customer.email = email
        customer.Address = add
        customer.City = city
        customer.state = state
        customer.Pincode = pin
        customer.Consumer = con
        # customer.Bill_unit = bu
        customer.loadsancution = ls
        customer.qunt_solar = qunt_solar
        customer.qunt_inv = qunt_inv
        customer.current_load = current_load
        customer.sol_warranty =sol_warranty
        customer.inv_warranty = inv_warranty
        customer.com_warranty = com_warranty

        if po_date:
            customer.po_date = po_date


        if cad:
            customer.Cus_Act_Date = cad

        if Teamid:
            team1 = User.objects.get(id=Teamid)
            customer.Engg_Assign = team1
        else:
            customer.Engg_Assign = 1

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


# @login_required(login_url='user-login')
# def customer_updatepage(request, Cust_id):
#     #customer = get_object_or_404(Customer, Cust_id=Cust_id)
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     customer = Customer.objects.get(Cust_id=Cust_id)
#     #id = customer.Emp_id
#     # context = {
#     #     'customer': customer,
#     #     'user1': user1,
#     # }
#     def get_employee_user(customer):
#         try:
#             return User.objects.get(id=customer.Emp_id)
#         except User.DoesNotExist:
#             return None
#     return render(request, 'customer/customer_updatepage.html', locals())




@login_required(login_url='user-login')
def customer_updatepage(request, Cust_id):
    #customer = get_object_or_404(Customer, Cust_id=Cust_id)
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    customer = Customer.objects.get(Cust_id=Cust_id)

    # code for display product
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
    product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
    items1 = BarcodeImage.objects.all()
    progress_warranty = {}
    # solar Panel ,Inverter, Replace Code
    # Inside the view function
    current_date = datetime.now().date()
    remaining_days_inv_warranty = None  # Initialize with None
    remaining_days_sol_warranty = None
    remaining_days_com_warranty = None
    installation_date1 = None  # Initialize with None

    items = []
    solar_items = []
    inverter_items = []
    replace_items = []
    solar_panel_total_quantity = 0
    solar_panel_quantity_by_wattage = []
    unique_wattages = []
    inverter_wattages = []
    inverter_panel_quantity_by_wattage = []
    inverter_panel_total_quantity = 0
    replace_wattages = []
    replace_panel_quantity_by_wattage = []
    replace_panel_total_quantity = 0
    user_record = Customer.objects.get(Cust_id=Cust_id)
    selected_company = user_record.Comp_name
    items = BarcodeImage.objects.filter(company=selected_company)
    solar_items = items.filter(product_name='SolarPanel')
    inverter_items = items.filter(product_name='Inverter')
    replace_items = items.filter(product_name='Replace')
    solar_panel_total_quantity = solar_items.count()
    solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
    inverter_panel_total_quantity = inverter_items.count()
    inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
    replace_panel_total_quantity = replace_items.count()
    replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))


    unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
    inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
    replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}

    # Generation Meter Details
    user_record = Customer.objects.get(Cust_id=Cust_id)
    selected_comp_name = user_record.Comp_name
    print(selected_comp_name)

    meters_records = Meters.objects.filter(comp_name=selected_comp_name)
    generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
    generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)

    # CODE FOr MSEB Status
    customer = get_object_or_404(Customer, Cust_id=Cust_id)
    # customer = Customer.objects.filter(new_customer_id=request.user.id)
    mseb_data = MSEB.objects.filter(customer=customer).first()
    records = MSEB.objects.filter(customer=customer).first()
    progress_data = None
    # CODE FOR MSEB Status
    customer = get_object_or_404(Customer, Cust_id=Cust_id)
    mseb_data = MSEB.objects.filter(customer=customer).first()


    # installation_date1 = mseb_data.installation_date  # Assuming installation_date is the field name
    # print(installation_date1)
    if mseb_data is not None:
        installation_date1 = mseb_data.installation_date  # Assuming installation_date is the field name
        records = mseb_data
        progress_data = {}
        current_load = int(customer.current_load)  # Parse to integer
        loadsancution = int(customer.loadsancution)  # Parse to integer


        # Check if both values are equal
        if current_load == loadsancution:
            field_mapping = {
                'net_meter': 'Net Metering',
                'flexibility': 'Technical Feasibility',
                'approval': 'Approval',
                'meter_testing': 'Meter Testing',
                'agreement': 'NetMeter Agreement.',
                'release': 'Meter Release',
                'installation_date': 'Meter Installation Date',
            }
        else:
            field_mapping = {
                'load_extension': 'Load Extension',
                'flisibility': 'Off-Line Feasibility',
                'quotation': 'Firm Quotation Gen.',
                'sent_to_bill': 'Sent to Bill',
                'net_meter': 'Net Metering',
                'flexibility': 'Technical Feasibility',
                'approval': 'Approval',
                'meter_testing': 'Meter Testing',
                'agreement': 'NetMeter Agreement.',
                'release': 'Meter Release',
                'installation_date': 'Meter Installation Date',
            }

        # Constructing progress data with display names
        for field, value in mseb_data.__dict__.items():
            if field in field_mapping:
                progress_data[field_mapping[field]] = {
                    'value': value,
                    'date': getattr(mseb_data, f"{field}_date") if f"{field}_date" in mseb_data.__dict__ else None
                }
                # Calculate warranty end dates
                installation_date = mseb_data.installation_date_date
                if installation_date:
                    inv_warranty_years = customer.inv_warranty
                    sol_warranty_years = customer.sol_warranty
                    com_warranty_years = customer.com_warranty


                    if sol_warranty_years:
                        installation_date_date = mseb_data.installation_date_date.date()  # Convert to datetime.date
                        sol_warranty_end_date = installation_date_date + timedelta(
                            days=365 * sol_warranty_years) - timedelta(days=1)
                        remaining_days_sol_warranty = (sol_warranty_end_date - current_date).days
                        progress_warranty['Solar Module Warranty'] = {
                            'value': True,
                            'date': sol_warranty_end_date,
                            'remaining_days': remaining_days_sol_warranty
                        }



                    if inv_warranty_years:
                        installation_date_date = mseb_data.installation_date_date.date()  # Convert to datetime.date
                        inv_warranty_end_date = installation_date_date + timedelta(
                            days=365 * inv_warranty_years) - timedelta(days=1)
                        remaining_days_inv_warranty = (inv_warranty_end_date - current_date).days
                        progress_warranty['Inverter Warranty'] = {
                            'value': True,
                            'date': inv_warranty_end_date,
                            'remaining_days': remaining_days_inv_warranty
                        }



                    if com_warranty_years:
                        installation_date_date = mseb_data.installation_date_date.date()  # Convert to datetime.date
                        com_warranty_end_date = installation_date_date + timedelta(
                            days=365 * com_warranty_years) - timedelta(days=1)
                        remaining_days_com_warranty = (com_warranty_end_date - current_date).days + 1
                        progress_warranty['O & M Warranty'] = {
                            'value': True,
                            'date': com_warranty_end_date,
                            'remaining_days': remaining_days_com_warranty
                        }

    else:
        records = None
        progress_data = {}


    # def get_employee_user(customer):
    #     try:
    #         return User.objects.get(id=customer.Emp_id)
    #     except User.DoesNotExist:
    #         return None

    return render(request, 'customer/customer_updatepage.html',
                  {'companies': companies, 'product_names': product_names, 'items': items,
                   'solar_items': solar_items, 'inverter_items': inverter_items, 'replace_items': replace_items,
                   'solar_panel_total_quantity': solar_panel_total_quantity, 'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
                   'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
                   'inverter_panel_total_quantity': inverter_panel_total_quantity,
                   'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,
                   'replace_panel_total_quantity': replace_panel_total_quantity,
                   'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
                   'replace_wattages': replace_wattages,
                   'notification1': notification1,
                   'count1': count1,
                   'user_record': user_record,
                   'meters_records': meters_records,
                   'generation_meter_records': generation_meter_records,
                   'generation_ct_records': generation_ct_records,
                   'selected_comp_name': selected_comp_name,
                   'customer': customer, 'progress_data': progress_data, 'records': records,
                   'progress_warranty': progress_warranty,
                   'mseb_installation_date': installation_date1,
                   'remaining_days_inv_warranty': remaining_days_inv_warranty,

                   })






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

# all record filter without add dropdownlist of fieldselect and valueselect
# @login_required(login_url='user-login')
# def consumer_pdf(request):
#     if request.method == 'POST':
#         form = consumerGenerationForm(request.POST)
#         if form.is_valid():
#             customer_type_filter = request.POST.get('userType')
#
#             # Define the base queryset
#             base_queryset = Customer.objects.all()
#
#             # Apply filters based on the selected user type
#             if customer_type_filter == 'Residential':
#                 base_queryset = base_queryset.filter(Cust_type='Residential')
#             elif customer_type_filter == 'Commersial':
#                 base_queryset = base_queryset.filter(Cust_type='Commersial')
#             elif customer_type_filter == 'Industrial':
#                 base_queryset = base_queryset.filter(Cust_type='Industrial')
#             elif customer_type_filter == 'Goverment':
#                 base_queryset = base_queryset.filter(Cust_type='Goverment')
#
#             selected_customer_fields = form.cleaned_data['customer_fields']
#             #selected_profile_fields = form.cleaned_data['profile_fields']
#
#             # Check if at least one field from either User or Profile is selected
#             if not (selected_customer_fields):
#                 return HttpResponse("Please select at least one field from User or Profile to generate the PDF.")
#
#             # Fetch the filtered users based on the selected user type
#             users = base_queryset
#
#             # Define custom field names
#             field_display_names = {
#                 'Comp_name': 'Consumer Name',
#                 'username': 'Username',
#                 'first_name': 'First Name',  # Map 'id' field to 'ID'
#                 'phone': 'Contact No',
#                 'Plant_Capacity': 'Plant Capacity',
#                 'Ups_Soft': 'Inverter Software Used',
#                 'City': 'City',
#                 'email': 'Email ID',
#                 'Address': 'Address',
#                 'city': 'City',
#                 'po_date': 'PO Date',
#                 'solar_comp': 'Solar Plate Company',
#                 'UPSC': 'Inverter Company',
#                 'state': 'State',
#                 'Pincode': 'Pincode',
#                 'phase': 'Phase',
#                 'loadsancution': 'Additional Load',
#                 'current_load': 'Previous Load',
#                 'Cust_id': 'ID',
#                 'new_customer': 'Username',
#                 'Cust_type': 'Consumer Type',
#                 'po_order': 'Purchase Order',
#
#                 # Add more mappings as needed
#             }
#
#             custom_customer_fields = ['Full Name'] if 'full_name' in selected_customer_fields else []
#
#             for field in selected_customer_fields:
#                 if field in field_display_names and field != 'full_name':
#                     custom_customer_fields.append(field_display_names[field])
#
#            # custom_profile_fields = [field_display_names.get(field, field) for field in selected_profile_fields]
#
#             data = []
#             for customer in users:
#                 customer_profile = customer.profile if hasattr(customer, 'profile') else None
#                 print(f'User ID: {customer.Cust_id}, Customer ID: {customer_profile.customer_id if customer_profile else "N/A"}')
#
#                 customer_profile = customer.profile if hasattr(customer, 'profile') else None
#                 full_name = f"{customer.first_name} {customer.last_name}" if 'full_name' in selected_customer_fields else ""
#                 customer_fields_data = {
#                     # 'Cust_id': customer_profile.Cust_id if customer_profile else '',  # Access 'customer_id' from profile
#                     'Cust_id': customer.Cust_id,
#                     'Full Name': full_name,
#                 }
#                 customer_fields_data.update({field_display_names.get(field, field): getattr(customer, field, "") for field in selected_customer_fields if field != 'full_name'})
#               #  profile_fields_data = {field_display_names.get(field, field): getattr(user_profile, field, "") for field in selected_profile_fields} if user_profile else {}
#                 customer_data = {
#                     'customer_fields': customer_fields_data,
#                    # 'profile_fields': profile_fields_data,
#                 }
#                 data.append(customer_data)
#             logo_path = "media/static/images/dblogo2001.png"  # Replace with the actual path to your logo image
#             top_margin_height = 0.25  # Adjust this value as needed
#
#             # Call the PDF generation function with the data
#             return consumer_print(request, custom_customer_fields, data, logo_path, top_margin_height, customer_type_filter)
#     else:
#         form = consumerGenerationForm()
#
#     return render(request, 'customer/consumer_list.html', {'form': form})


@login_required(login_url='user-login')
def consumer_pdf(request):
    if request.method == 'POST':
        form = consumerGenerationForm(request.POST)
        if form.is_valid():
            customer_type_filter = request.POST.get('userType')
            selected_field = request.POST.get('selectedField')  # Get the selected field from the hidden input
            selected_value = request.POST.get('selectedValue')  # Get the selected value from the hidden input

            # Define the base queryset
            base_queryset = Customer.objects.all()

            # Apply filters based on the selected user type
            if customer_type_filter == 'Residential':
                base_queryset = base_queryset.filter(Cust_type='Residential')
            elif customer_type_filter == 'Commersial':
                base_queryset = base_queryset.filter(Cust_type='Commersial')
            elif customer_type_filter == 'Industrial':
                base_queryset = base_queryset.filter(Cust_type='Industrial')
            elif customer_type_filter == 'Goverment':
                base_queryset = base_queryset.filter(Cust_type='Goverment')

            # Apply additional filters based on the selected field and value
            if selected_field != 'all' and selected_value:
                # # Assuming 'selected_field' corresponds to a field in the Customer model
                # filter_kwargs = {selected_field: selected_value}
                # base_queryset = base_queryset.filter(**filter_kwargs)
                # Handle the "All" case for the "loadsancution" field
                if selected_field == 'loadsancution' and selected_value == 'All':
                    selected_value = ''  # Set it to an empty string or None to fetch all values
                elif selected_field == 'Plant_Capacity' and selected_value == 'All':
                    selected_value = ''  # Set it to an empty string or None to fetch all values
                else:
                    # Handle other fields and values
                    filter_kwargs = {selected_field: selected_value}
                    base_queryset = base_queryset.filter(**filter_kwargs)

            selected_customer_fields = form.cleaned_data['customer_fields']

            # Check if at least one field from either User or Profile is selected
            if not (selected_customer_fields):
                return HttpResponse("Please select at least one field from User or Profile to generate the PDF.")

            # Fetch the filtered users based on the selected user type and additional filters
            users = base_queryset

            # Define custom field names
            field_display_names = {
                                'Comp_name': 'Consumer Name',
                                'username': 'Username',
                                'first_name': 'First Name',  # Map 'id' field to 'ID'
                                'phone': 'Contact No',
                                'Plant_Capacity': 'Plant Capacity',
                                'Ups_Soft': 'Inverter Software Used',
                                'City': 'City',
                                'email': 'Email ID',
                                'Address': 'Address',
                                'city': 'City',
                                'po_date': 'PO Date',
                                'solar_comp': 'Solar Plate Company',
                                'UPSC': 'Inverter Company',
                                'state': 'State',
                                'Pincode': 'Pincode',
                                'phase': 'Phase',
                                'loadsancution': 'Final Load',
                                'current_load': 'Previous Load',
                                'Cust_id': 'ID',
                                'new_customer': 'Username',
                                'Cust_type': 'Consumer Type',
                                'po_order': 'Purchase Order',

            }

            custom_customer_fields = ['Full Name'] if 'full_name' in selected_customer_fields else []

            for field in selected_customer_fields:
                if field in field_display_names and field != 'full_name':
                    custom_customer_fields.append(field_display_names[field])
            # without dislay Cust_id value
            # data = []
            # for customer in users:
            #     # Assuming 'selected_customer_fields' corresponds to the fields you want to display in the PDF
            #     customer_fields_data = {
            #         field_display_names.get(field, field): getattr(customer, field, "") for field in selected_customer_fields
            #     }
            #     customer_data = {
            #         'customer_fields': customer_fields_data,
            #     }
            #     data.append(customer_data)
            data = []
            for customer in users:
                customer_profile = customer.profile if hasattr(customer, 'profile') else None
                print(
                    f'User ID: {customer.Cust_id}, Customer ID: {customer_profile.customer_id if customer_profile else "N/A"}')

                customer_profile = customer.profile if hasattr(customer, 'profile') else None
                full_name = f"{customer.first_name} {customer.last_name}" if 'full_name' in selected_customer_fields else ""
                customer_fields_data = {
                    # 'Cust_id': customer_profile.Cust_id if customer_profile else '',  # Access 'customer_id' from profile
                    'Cust_id': customer.Cust_id,
                    'Full Name': full_name,
                }
                customer_fields_data.update(
                    {field_display_names.get(field, field): getattr(customer, field, "") for field in
                     selected_customer_fields if field != 'full_name'})
                #  profile_fields_data = {field_display_names.get(field, field): getattr(user_profile, field, "") for field in selected_profile_fields} if user_profile else {}
                customer_data = {
                    'customer_fields': customer_fields_data,
                    # 'profile_fields': profile_fields_data,
                }
                data.append(customer_data)

            logo_path = "media/static/images/dblogo2001.png"  # Replace with the actual path to your logo image
            top_margin_height = 0.25  # Adjust this value as needed

            selected_field_name = field_display_names.get(selected_field, selected_field)
            # Check if the selected field requires "Kw" to be added
            add_kw_to_value = selected_field in ['loadsancution', 'Plant_Capacity']

            # Call the PDF generation function with the data
            return consumer_print(request, custom_customer_fields, data, logo_path, top_margin_height, customer_type_filter, selected_field_name, selected_value, add_kw_to_value)
    else:
        form = consumerGenerationForm()

    return render(request, 'customer/consumer_list.html', {'form': form})





#  Value of customer_list html page dropdown value
def get_values_for_field(request):
    selected_field = request.GET.get('field', None)
    if selected_field is None or selected_field == 'all':
        # Return all unique values for the selected field
        values = Customer.objects.values(selected_field).distinct().order_by(selected_field)
    else:
        # Return unique values for the selected field
        values = Customer.objects.values(selected_field).distinct().order_by(selected_field)

    # Extract the values from the QuerySet
    values_list = [item[selected_field] for item in values if item[selected_field] is not None]

    # Add 'All' option to the values list
    values_list.insert(0, 'All')

    return JsonResponse({'values': values_list})




from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Spacer, Paragraph


# @login_required(login_url='user-login')
# def consumer_print(request, customer_fields, data, logo_path, top_margin_height=0.25, customer_type_filter=""):
#     buffer = BytesIO()
#
#     # Determine the page size based on the number of fields
#     if len(customer_fields) > 3:
#         page_size = landscape(letter)
#     else:
#         page_size = portrait(letter)
#
#     # pdf = SimpleDocTemplate(buffer, pagesize=page_size, topMargin=top_margin_height * inch)
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
#         caption_text = "List Type: Commersial Consumer List"
#     elif customer_type_filter == "Industrial":
#         caption_text = "List Type: Industrial Consumer List"
#     elif customer_type_filter == "Goverment":
#         caption_text = "List Type: Goverment Consumer List"
#     else:
#         caption_text = "Unknown List"  # Add a default caption for unknown options
#
#     # Add the selected field and value to the caption
#     selected_field = request.POST.get('selectedField')
#     selected_value = request.POST.get('selectedValue')
#     if selected_field and selected_value:
#         caption_text += f" | {selected_field} -{selected_value}"
#
#     caption = Paragraph(caption_text, caption_style)
#
#     # Create table data for all user data
#     table_data = [['Sr No', 'Cons.ID'] + customer_fields]  # Change 'ID' to 'Cust ID'
#
#     for index, customer_data in enumerate(data, start=1):
#         row = [index, customer_data['customer_fields'].get('Cust_id')]  # Change 'ID' to 'Cust_id'
#
#         for field in customer_fields:
#             if field == 'PO Date':
#                 # Format the "Installation Date" to 'dd-mm-yy'
#                 installation_date = customer_data['customer_fields'].get(field, "")
#                 if installation_date:
#                     installation_date = installation_date.strftime('%d-%m-%Y')
#                 row.append(installation_date)
#             elif field == 'Previous Load':
#                 # Add "Kw" label to the "Plant Capacity" field
#                 loadsancution = customer_data['customer_fields'].get(field, "")
#                 row.append(f"{loadsancution}  Kw")
#             elif field == 'Additional Load':
#                 # Add "Kw" label to the "Plant Capacity" field
#                 current_load = customer_data['customer_fields'].get(field, "")
#                 row.append(f"{current_load}  Kw")
#             elif field == 'Plant Capacity':
#                 # Add "Kw" label to the "Plant Capacity" field
#                 plant_capacity = customer_data['customer_fields'].get(field, "")
#                 row.append(f"{plant_capacity}  Kw")
#             else:
#                 row.append(customer_data['customer_fields'].get(field, ""))
#
#         # row.extend([customer_data['customer_fields'].get(field, "") for field in customer_fields if
#         #             field != 'Cust_id'])  # Exclude 'Cust_id'
#         # # row.extend([user_data['profile_fields'].get(field, "") for field in profile_fields if field != 'customer_id'])
#         table_data.append(row)
#
#     table = Table(table_data)
#     style = TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#                         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
#                         ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center-align the first row
#                         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Add a background color to the first row
#                         ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # Center-align the Sr No and Emp ID columns
#                         ])
#     table.setStyle(style)
#
#     # Add the company logo at the top of the page
#     logo = Image(logo_path, width=5.5 * inch, height=0.70 * inch)
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
#     #response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
#     # Construct the filename based on the user_type_filter
#     response['Content-Disposition'] = f'attachment; filename ={customer_type_filter}_pdf.pdf'
#
#
#     response.write(buffer.getvalue())
#     buffer.close()
#
#     return response

from django.utils.http import urlquote
#
# @login_required(login_url='user-login')
# def consumer_print(request, customer_fields, data, logo_path, top_margin_height=0.25, customer_type_filter="", selected_field_name="", selected_value="", add_kw_to_value=False):
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
#     elif customer_type_filter == "Goverment":
#         caption_text = "List Type: Government Consumer List"
#     else:
#         caption_text = "Unknown List"  # Add a default caption for unknown options
#
#     if selected_field_name and selected_value:
#         if add_kw_to_value:
#             # Append "Kw" to the value when add_kw_to_value is True
#             caption_text += f" | {selected_field_name}: {selected_value} Kw"
#         else:
#             caption_text += f" | {selected_field_name}: {selected_value}"
#
#     # if selected_field_name and selected_value:
#     #     caption_text += f" | {selected_field_name} -{selected_value}"
#
#     caption = Paragraph(caption_text, caption_style)
#
#     # Create table data for all user data
#     table_data = [['Sr No', 'Cons.ID'] + customer_fields]  # Change 'ID' to 'Cust ID'
#
#     for index, customer_data in enumerate(data, start=1):
#         row = [index, customer_data['customer_fields'].get('Cust_id')]  # Change 'ID' to 'Cust_id'
#
#         for field in customer_fields:
#             if field == 'PO Date':
#                 # Format the "Installation Date" to 'dd-mm-yy'
#                 installation_date = customer_data['customer_fields'].get(field, "")
#                 if installation_date:
#                     installation_date = installation_date.strftime('%d-%m-%Y')
#                 row.append(installation_date)
#             elif field in ['Additional Load', 'Previous Load', 'Plant Capacity']:
#                 # Add "Kw" label to specific fields
#                 field_value = customer_data['customer_fields'].get(field, "")
#                 row.append(f"{field_value} Kw")
#             else:
#                 row.append(customer_data['customer_fields'].get(field, ""))
#
#         table_data.append(row)
#
#     table = Table(table_data)
#     style = TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#                         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
#                         ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center-align the first row
#                         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Add a background color to the first row
#                         ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # Center-align the Sr No and Emp ID columns
#                         ])
#     table.setStyle(style)
#
#     # Add the company logo at the top of the page
#     logo = Image(logo_path, width=5.5 * inch, height=0.70 * inch)
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
#     # Below code Create PDF direct Download
#
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename ={customer_type_filter}_pdf.pdf'
#
#     # Below code Create PDF balnk page
#     # response = HttpResponse(content_type='application/pdf')
#     # filename = f'{customer_type_filter}_pdf.pdf'
#     # response['Content-Disposition'] = f'inline; filename="{urlquote(filename)}"'
#
#     response.write(buffer.getvalue())
#     buffer.close()
#
#     return response




@login_required(login_url='user-login')
def consumer_print(request, customer_fields, data, logo_path, top_margin_height=0.25, customer_type_filter="", selected_field_name="", selected_value="", add_kw_to_value=False):
    buffer = BytesIO()

    # Determine the page size based on the number of fields
    if len(customer_fields) > 3:
        page_size = landscape(letter)
    else:
        page_size = portrait(letter)

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
        caption_text = "List Type: Commercial Consumer List"
    elif customer_type_filter == "Industrial":
        caption_text = "List Type: Industrial Consumer List"
    elif customer_type_filter == "Goverment":
        caption_text = "List Type: Government Consumer List"
    else:
        caption_text = "Unknown List"  # Add a default caption for unknown options

    if selected_field_name and selected_value:
        if add_kw_to_value:
            # Append "Kw" to the value when add_kw_to_value is True
            caption_text += f" | {selected_field_name}: {selected_value} Kw"
        else:
            caption_text += f" | {selected_field_name}: {selected_value}"

    # if selected_field_name and selected_value:
    #     caption_text += f" | {selected_field_name} -{selected_value}"

    caption = Paragraph(caption_text, caption_style)

    # Create table data for all user data
    table_data = [['Sr No', 'Cons.ID'] + customer_fields]  # Change 'ID' to 'Cust ID'

    for index, customer_data in enumerate(data, start=1):
        row = [index, customer_data['customer_fields'].get('Cust_id')]  # Change 'ID' to 'Cust_id'

        for field in customer_fields:
            if field == 'PO Date':
                # Format the "Installation Date" to 'dd-mm-yy'
                installation_date = customer_data['customer_fields'].get(field, "")
                if installation_date:
                    installation_date = installation_date.strftime('%d-%m-%Y')
                row.append(installation_date)
            elif field in ['Additional Load', 'Previous Load', 'Plant Capacity']:
                # Add "Kw" label to specific fields
                field_value = customer_data['customer_fields'].get(field, "")
                row.append(f"{field_value} Kw")
            else:
                row.append(customer_data['customer_fields'].get(field, ""))

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

    # Below code Create PDF direct Download

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename ={customer_type_filter}_pdf.pdf'

    # Below code Create PDF balnk page
    # response = HttpResponse(content_type='application/pdf')
    # filename = f'{customer_type_filter}_pdf.pdf'
    # response['Content-Disposition'] = f'inline; filename="{urlquote(filename)}"'

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



#
# from django.shortcuts import render, redirect
# from .models import Customer
#
# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)  # Get company names from Customer table
#     if request.method == 'POST':
#         comp_name = request.POST.get('Comp_name')
#         meters = request.POST.get('meters')
#         meters_make = request.POST.get('meters_make')
#         meters_capacity = request.POST.get('meters_capacity')
#         meters_serial = request.POST.get('meters_serial')
#         meter_type = request.POST.get('meter_type')
#         meter_make = request.POST.get('meter_make')
#         meter_capacity = request.POST.get('meter_capacity')
#         meter_serial = request.POST.get('meter_serial')
#         #generation_meter = request.POST.get('generation_meter')
#         generation_meter_make = request.POST.get('generation_meter_make')
#         generation_meter_capacity = request.POST.get('generation_meter_capacity')
#         generation_meter_serial = request.POST.get('generation_meter_serial')
#         generation_ct = request.POST.get('generation_ct')
#         generation_ct_make = request.POST.get('generation_ct_make')
#         generation_ct_capacity = request.POST.get('generation_ct_capacity')
#         generation_ct_serial = request.POST.get('generation_ct_serial')
#
#         customer = Customer(
#             Comp_name=comp_name,
#             meters=meters,
#             meters_make=meters_make,
#             meters_capacity=meters_capacity,
#             meters_serial=meters_serial,
#             meter_type=meter_type,
#             meter_make=meter_make,
#             meter_capacity=meter_capacity,
#             meter_serial=meter_serial,
#             #generation_meter=generation_meter,
#             generation_meter_make=generation_meter_make,
#             generation_meter_capacity=generation_meter_capacity,
#             generation_meter_serial=generation_meter_serial,
#             generation_ct=generation_ct,
#             generation_ct_make=generation_ct_make,
#             generation_ct_capacity=generation_ct_capacity,
#             generation_ct_serial=generation_ct_serial
#         )
#         customer.save()
#
#         return redirect('success')  # Redirect to a success page
#
#     return render(request, 'customer/add_meter.html', {'comp_names': comp_names})

# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)  # Get company names from Customer table
#     if request.method == 'POST':
#         customer = Meter(
#             Comp_name=request.POST['Comp_name'],
#             meters=request.POST['meters'],
#             m_meters_make=request.POST['m_meters_make'],
#             meters_capacity=request.POST['meters_capacity'],
#             meters_serial=request.POST['meters_serial'],
#             meter_type=request.POST['meter_type'],
#             meter_make=request.POST['meter_make'],
#             meter_capacity=request.POST['meter_capacity'],
#             meter_serial=request.POST['meter_serial'],
#             generation_meter_make=request.POST['generation_meter_make'],
#             generation_meter_capacity=request.POST['generation_meter_capacity'],
#             generation_meter_serial=request.POST['generation_meter_serial'],
#             generation_ct=request.POST['generation_ct'],
#             generation_ct_make=request.POST['generation_ct_make'],
#             generation_ct_capacity=request.POST['generation_ct_capacity'],
#             generation_ct_serial=request.POST['generation_ct_serial']
#         )
#         customer.save()
#         return HttpResponse("Data saved successfully.")
#
#     return render(request, 'customer/add_meter.html', {'comp_names': comp_names})

#
# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)  # Get company names from Customer table

    # if request.method == 'POST':
    #     # Loop through the form fields and create a new record for each set of data
    #     for i in range(len(request.POST.getlist('Comp_name'))):
    #         customer = Meter(
    #             Comp_name=request.POST.getlist('Comp_name')[i],
    #             meters=request.POST.getlist('meters_0')[i],
    #             m_meters_make=request.POST.getlist('m_meters_make')[i],
    #             meters_capacity=request.POST.getlist('meters_capacity')[i],
    #             meters_serial=request.POST.getlist('meters_serial')[i],
    #             meter_type=request.POST.getlist('meter_type')[i],
    #             meter_make=request.POST.getlist('meter_make')[i],
    #             meter_capacity=request.POST.getlist('meter_capacity')[i],
    #             meter_serial=request.POST.getlist('meter_serial')[i],
    #             generation_meter_make=request.POST.getlist('generation_meter_make')[i],
    #             generation_meter_capacity=request.POST.getlist('generation_meter_capacity')[i],
    #             generation_meter_serial=request.POST.getlist('generation_meter_serial')[i],
    #             generation_ct=request.POST.getlist('generation_ct')[i],
    #             generation_ct_make=request.POST.getlist('generation_ct_make')[i],
    #             generation_ct_capacity=request.POST.getlist('generation_ct_capacity')[i],
    #             generation_ct_serial=request.POST.getlist('generation_ct_serial')[i]
    #         )
    #         customer.save()
    #
    #     return HttpResponse("Data saved successfully.")
    #
    # return render(request, 'customer/add_meter.html', {'comp_names': comp_names})

#
# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)
#
#     if request.method == 'POST':
#         comp_name = request.POST['Comp_name']
#
#         for key in request.POST.keys():
#             if key.startswith('m_meters_make'):
#                 index = key.split('_')[-1]
#                 print(index)
#                 customer = Meter(
#                     Comp_name=comp_name,
#                     meters=request.POST.get(f'meters',''),
#                     if index == 'make':
#                          m_meters_make=request.POST.get(f'm_meters_make', ''),
#                          meters_capacity=request.POST.get(f'm_meters_capacity', ''),
#                          meters_serial=request.POST.get(f'm_meters_serial', ''),
#                     else:
#                         m_meters_make = request.POST.get(f'm_meters_make_{index}', ''),
#                         meters_capacity = request.POST.get(f'm_meters_capacity_{index}', ''),
#                         meters_serial = request.POST.get(f'm_meters_serial_{index}', ''),
#                         meter_type=request.POST.get(f'meter_type', ''),  # Get the selected value (default: 'CT')
#                         meter_make=request.POST.get(f'meter_make', ''),
#                         meter_capacity=request.POST.get(f'meter_capacity', ''),
#                         meter_serial=request.POST.get(f'meter_serial', ''),
#                         generation_meter_make=request.POST.get(f'generation_meter_make', ''),
#                         generation_meter_capacity=request.POST.get(f'generation_meter_capacity', ''),
#                         generation_meter_serial=request.POST.get(f'generation_meter_serial', ''),
#                         generation_ct=request.POST.get(f'generation_ct', 'Required'),  # Get the selected value (default: 'Required')
#                         generation_ct_make=request.POST.get(f'generation_ct_make', ''),
#                         generation_ct_capacity=request.POST.get(f'generation_ct_capacity', ''),
#                         generation_ct_serial=request.POST.get(f'generation_ct_serial', ''),
#                 )
#                 customer.save()
#
#         return HttpResponse("Data saved successfully.")
#
#     return render(request, 'customer/add_meter.html', {'comp_names': comp_names})
#
#
# # # ------------------------------------------------------------------
# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)
#
#     if request.method == 'POST':
#         comp_name = request.POST['Comp_name']
#
#         for key in request.POST.keys():
#             if key.startswith('m_meters_make_1'):
#                 index = key.split('_')[-1]
#                 print(f'm_meters_make:{index}')
#             if key.startswith('meter_make_1'):
#                 index = key.split('_')[-1]
#                 print(f'meter_make:{index}')
#             if key.startswith('generation_meter_make_1'):
#                 index = key.split('_')[-1]
#                 print(f'generation_meter_make:{index}')
#             if key.startswith('generation_ct_make_1'):
#                 index = key.split('_')[-1]
#                 print(f'generation_ct_make:{index}')
#             elif key.startswith('m_meters_make'):
#                 index = key.split('_')[-1]
#                 print(f'{key}:{index}')
#             elif key.startswith('m_meters_make'):
#                 index = key.split('_')[-1]
#                 print(f'{key}:{index}')
#             elif key.startswith('generation_meter_make'):
#                 index = key.split('_')[-1]
#                 print(f'{key}:{index}')
#             elif key.startswith('generation_ct_make'):
#                 index = key.split('_')[-1]
#                 print(f'{key}:{index}')
#
#                 customer = Meter(
#                     Comp_name=comp_name,
#                     meters=request.POST.get(f'meters', ''),
#                     meter_type=request.POST.get(f'meter_type', ''),  # Get the selected value (default: 'CT')
#                     generation_ct = request.POST.get(f'generation_ct', 'Required'),  # Get the selected value (default: 'Required')
#                 )
#
#                 if index == 'make':
#                     customer.m_meters_make = request.POST.get(f'm_meters_make', '')
#                     customer.meters_capacity = request.POST.get(f'm_meters_capacity', '')
#                     customer.meters_serial = request.POST.get(f'm_meters_serial', '')
#                 else:
#                     customer.m_meters_make = request.POST.get(f'm_meters_make_{index}', '')
#                     customer.meters_capacity = request.POST.get(f'm_meters_capacity_{index}', '')
#                     customer.meters_serial = request.POST.get(f'm_meters_serial_{index}', '')
#
#                 if index == 'make':
#                     customer.meter_make = request.POST.get(f'meter_make', '')
#                     customer.meter_capacity = request.POST.get(f'meter_capacity', '')
#                     customer.meter_serial = request.POST.get(f'meter_serial', '')
#                 else:
#                     customer.meter_make = request.POST.get(f'meter_make_{index}', '')
#                     customer.meter_capacity = request.POST.get(f'meter_capacity_{index}', '')
#                     customer.meter_serial = request.POST.get(f'meter_serial_{index}', '')
#
#                 if index == 'make':
#                     customer.generation_meter_make = request.POST.get(f'generation_meter_make', '')
#                     customer.generation_meter_capacity = request.POST.get(f'generation_meter_capacity', '')
#                     customer.generation_meter_serial = request.POST.get(f'generation_meter_serial', '')
#                 else:
#                     customer.generation_meter_make = request.POST.get(f'generation_meter_make_{index}', '')
#                     customer.generation_meter_capacity = request.POST.get(f'generation_meter_capacity_{index}', '')
#                     customer.generation_meter_serial = request.POST.get(f'generation_meter_serial_{index}', '')
#                 if index == 'make':
#                     customer.generation_ct_make = request.POST.get(f'generation_ct_make', '')
#                     customer.generation_ct_capacity = request.POST.get(f'generation_ct_capacity', '')
#                     customer.generation_ct_serial = request.POST.get(f'generation_ct_serial', '')
#
#                 else:
#                     customer.generation_ct_make = request.POST.get(f'generation_ct_make_{index}', '')
#                     customer.generation_ct_capacity = request.POST.get(f'generation_ct_capacity_{index}', '')
#                     customer.generation_ct_serial = request.POST.get(f'generation_ct_serial_{index}', '')
#
#                 # customer.generation_ct = request.POST.get(f'generation_ct', 'Required')  # Get the selected value (default: 'Required')
#
#                 customer.save()
#         return HttpResponse("Data saved successfully.")
#     return render(request, 'customer/add_meter.html', {'comp_names': comp_names})
# # #--------------------------------------------------------------------------------------------


from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from .models import Meter  # Import your Meter model

#
# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)
#
#     if request.method == 'POST':
#         comp_name = request.POST['Comp_name']
#
#         customer = Meter(
#             Comp_name=comp_name,
#             meters=request.POST.get('meters', ''),
#             meter_type=request.POST.get('meter_type', ''),
#             generation_ct=request.POST.get('generation_ct', 'Required')
#         )
#
#         # Loop through keys in POST data
#         for key in request.POST.keys():
#             if key.startswith('m_meters_make') or key.startswith('meter_make') or key.startswith(
#                     'generation_meter_make') or key.startswith('generation_ct_make'):
#                 index = key.split('_')[-1]
#                 print(f'{key}:{index}')
#
#                 # Create a single Meter object and populate fields based on the index
#                 customer.m_meters_make = request.POST.get(f'm_meters_make_{index}',
#                                                           '') if 'm_meters_make' in key else customer.m_meters_make
#                 customer.meter_make = request.POST.get(f'meter_make_{index}',
#                                                        '') if 'meter_make' in key else customer.meter_make
#                 customer.generation_meter_make = request.POST.get(f'generation_meter_make_{index}',
#                                                                   '') if 'generation_meter_make' in key else customer.generation_meter_make
#                 customer.generation_ct_make = request.POST.get(f'generation_ct_make_{index}',
#                                                                '') if 'generation_ct_make' in key else customer.generation_ct_make
#
#                 # customer.meters = request.POST.get('meters'),
#                 customer.m_meters_make=request.POST.get(f'm_meters_make_{index}', '') if 'm_meters_make' in key else customer.m_meters_make
#                 customer.meters_capacity=request.POST.get(f'm_meters_capacity_{index}', '') if 'm_meters_capacity' in key else customer.meters_capacity
#                 customer.meters_serial=request.POST.get(f'm_meters_serial_{index}', '') if 'm_meters_serial' in key else customer.meters_serial
#                 # customer.meter_type=request.POST.get('meter_type'),
#                 customer.meter_make=request.POST.get(f'meter_make_{index}', '') if 'meter_make' in key else customer.meter_make
#                 customer.meter_capacity=request.POST.get(f'meter_capacity_{index}', '') if 'meter_capacity' in key else customer.meter_capacity
#                 customer.meter_serial=request.POST.get(f'meter_serial_{index}', '') if 'meter_serial' in key else customer.meter_serial
#                 customer.generation_meter_make=request.POST.get(f'generation_meter_make_{index}', '') if 'generation_meter_make' in key else customer.generation_meter_make
#                 customer.generation_meter_capacity=request.POST.get(f'generation_meter_capacity_{index}', '') if 'generation_meter_capacity' in key else customer.generation_meter_capacity
#                 customer.generation_meter_serial=request.POST.get(f'generation_meter_serial_{index}', '') if 'generation_meter_serial' in key else customer.generation_meter_serial
#                 # customer.generation_ct=request.POST.get('generation_ct'),
#                 customer.generation_ct_make=request.POST.get(f'generation_ct_make_{index}', '') if 'generation_ct_make' in key else customer.generation_ct_make
#                 customer.generation_ct_capacity=request.POST.get(f'generation_ct_capacity_{index}', '') if 'generation_ct_capacity' in key else customer.generation_ct_capacity
#                 customer.generation_ct_serial=request.POST.get(f'generation_ct_serial_{index}', '') if 'generation_ct_serial' in key else customer.generation_ct_serial
#
#
#                 # Populate capacity and serial fields similarly
#
#         # Save the customer instance after collecting all values
#         customer.save()
#
#         return HttpResponse("Data saved successfully.")
#
#     return render(request, 'customer/add_meter.html', {'comp_names': comp_names})

def add_meter(request):
    comp_names = Customer.objects.values_list('Comp_name', flat=True)

    if request.method == 'POST':
        comp_name = request.POST['Comp_name']

        # Create a Meter instance with common fields
        customer = Meter(
            Comp_name=comp_name,
            meters=request.POST.get('meters', ''),
            meter_type=request.POST.get('meter_type', ''),
            generation_ct=request.POST.get('generation_ct', 'Required')
        )

        # Loop through keys in POST data
        for key in request.POST.keys():
            if key.startswith('m_meters_make') or key.startswith('meter_make') or key.startswith('generation_meter_make') or key.startswith('generation_ct_make'):
                index = key.split('_')[-1]

                # Map keys to corresponding model fields
                field_mapping = {
                    'm_meters_make': 'm_meters_make',
                    'meter_make': 'meter_make',
                    'generation_meter_make': 'generation_meter_make',
                    'generation_ct_make': 'generation_ct_make',
                }

                # Check if the key is in the field mapping
                if any(mapping_key in key for mapping_key in field_mapping.keys()):
                    field_key = next(mapping_key for mapping_key in field_mapping.keys() if mapping_key in key)

                    # Update the corresponding field of the customer instance
                    setattr(customer, field_mapping[field_key] + f'_{index}', request.POST.get(key, ''))

        # Save the customer instance after collecting all values
        customer.save()

        return HttpResponse("Data saved successfully.")

    return render(request, 'customer/add_meter.html', {'comp_names': comp_names})



#
# def save_meters(request):
#     if request.method == 'POST':
#         make = request.POST.get('make')
#         capacity = request.POST.get('capacity')
#         serial_no = request.POST.get('serial_no')
#         transformer_type = request.POST.get('transformer_type')
#         transformer_make = request.POST.get('transformer_make')
#         transformer_capacity = request.POST.get('transformer_capacity')
#         transformer_serial_number = request.POST.get('transformer_serial_number')
#
#         Meters.objects.create(make=make, capacity=capacity, serial_no=serial_no, transformer_type=transformer_type, transformer_make=transformer_make, transformer_capacity=transformer_capacity, transformer_serial_number=transformer_serial_number)
#
#         return HttpResponse("Meters data saved successfully.")
#
#     # return HttpResponse("Invalid request method.")
#     return render(request, 'customer/save_meters.html')
# def save_generation_meter(request):
#     if request.method == 'POST':
#         make = request.POST.get('make')
#         capacity = request.POST.get('capacity')
#         serial_no = request.POST.get('serial_no')
#
#         GenerationMeter.objects.create(make=make, capacity=capacity, serial_no=serial_no)
#
#         return HttpResponse("Generation Meter data saved successfully.")
#
#     # return HttpResponse("Invalid request method.")
#     return render(request, 'customer/meters.html')
# def save_generation_ct(request):
#     if request.method == 'POST':
#         make = request.POST.get('make')
#         capacity = request.POST.get('capacity')
#         serial_no = request.POST.get('serial_no')
#         required = request.POST.get('required')
#
#         GenerationCT.objects.create(make=make, capacity=capacity, serial_no=serial_no, required=required)
#
#         return HttpResponse("Generation CT data saved successfully.")
#
#     # return HttpResponse("Invalid request method.")
#     return render(request, 'customer/meters.html')


#
# # views.py
# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from .models import Meters, GenerationMeter, GenerationCT
# from .forms import GenerationMeterForm, GenerationCTForm
#
#
# def newmeters(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)
#
#     return render(request, 'customer/meters.html', {'comp_names': comp_names})
# #
#
# def save_meters(request):
#     if request.method == 'POST':
#         meters_type = request.POST.get('meters')
#         make = request.POST.get('make')
#         capacity = request.POST.get('capacity')
#         serial_no = request.POST.get('serial_no')
#         transformer_type = request.POST.get('transformer_type')
#         transformer_make = request.POST.get('transformer_make')
#         transformer_capacity = request.POST.get('transformer_capacity')
#         transformer_serial_number = request.POST.get('transformer_serial_number')
#
#         Meters.objects.create(
#             meter_type=meters_type,
#             make=make,
#             capacity=capacity,
#             serial_no=serial_no,
#             transformer_type=transformer_type,
#             transformer_make=transformer_make,
#             transformer_capacity=transformer_capacity,
#             transformer_serial_number=transformer_serial_number
#         )
#
#         return HttpResponse("Meters data saved successfully.")
#
#     return HttpResponse("Invalid request method.")
#
# def save_generation_meter(request):
#     if request.method == 'POST':
#         generation_meter_form = GenerationMeterForm(request.POST)
#         if generation_meter_form.is_valid():
#             generation_meter_form.save()
#             return HttpResponse("Generation Meter data saved successfully.")
#     else:
#         generation_meter_form = GenerationMeterForm()
#
#     return render(request, 'your_template.html', {'generation_meter_form': generation_meter_form})
#
# def save_generation_ct(request):
#     if request.method == 'POST':
#         generation_ct_form = GenerationCTForm(request.POST)
#         if generation_ct_form.is_valid():
#             generation_ct_form.save()
#             return HttpResponse("Generation CT data saved successfully.")
#     else:
#         generation_ct_form = GenerationCTForm()
#
#     return render(request, 'your_template.html', {'generation_ct_form': generation_ct_form})
#
#


from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Meters, GenerationMeter, GenerationCT
from .forms import GenerationMeterForm, GenerationCTForm
from customer.models import Customer  # Adjust the import path as needed

def newmeters(request):
    # comp_names = Customer.objects.values_list('Comp_name', flat=True)
    # comp_names = Customer.objects.all()
    # print(f"Comp_names: {comp_names}")

    # # Assuming you have authenticated user and get their assigned engineer
    # current_engineer = request.user  # Adjust this according to your user model
    #
    # # Filter comp_names queryset based on the customers assigned to the current engineer
    # comp_names = Customer.objects.filter(Engg_Assign=current_engineer).order_by('Comp_name').values_list('Comp_name',
    #                                                                                                      flat=True).distinct()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    if request.user.is_superuser:
        # If the user is a superuser, display all Comp_name values
        comp_names = Customer.objects.order_by('Comp_name').values_list('Comp_name', flat=True).distinct()
    elif request.user.is_staff:
        # If the user is a staff member, filter Comp_name values based on their assigned customers
        current_engineer = request.user  # Assuming the staff user has an assigned engineer
        comp_names = Customer.objects.filter(Engg_Assign=current_engineer).order_by('Comp_name').values_list(
            'Comp_name', flat=True).distinct()
    else:
        # For other users, provide an empty queryset or handle it as per your requirement
        comp_names = []
    return render(request, 'customer/meters.html', {'comp_names': comp_names, 'count1': count1, 'notification1': notification1,})


def save_meters(request):
    if request.method == 'POST':
        comp_name = request.POST.get('Comp_name')
        customer = Customer.objects.get(Comp_name=comp_name)


        meters_type = request.POST.get('meters')
        make = request.POST.get('make')
        capacity = request.POST.get('capacity')
        serial_no = request.POST.get('serial_no')
        transformer_type = request.POST.get('transformer_type')
        transformer_make = request.POST.get('transformer_make')
        transformer_capacity = request.POST.get('transformer_capacity')
        transformer_serial_number = request.POST.get('transformer_serial_number')
        AssignBy = request.user

        Meters.objects.create(
            customer=customer,
            comp_name=comp_name,
            meter_type=meters_type,
            make=make,
            capacity=capacity,
            serial_no=serial_no,
            transformer_type=transformer_type,
            transformer_make=transformer_make,
            transformer_capacity=transformer_capacity,
            transformer_serial_number=transformer_serial_number,
            AssignBy=AssignBy,
        )

        # # Add this line to set success message
        messages.success(request, 'Meters data saved successfully.')

        # Redirect back to the same page
        return redirect('customer-meters')  # 'meters_page' is the name of your meters page URL pattern

        # return HttpResponse("Meters data saved successfully.")

    return HttpResponse("Invalid request method.")



#
# def save_generation_meter(request):
#     if request.method == 'POST':
#         comp_name = request.POST.get('Comp_name')  # Assuming Comp_name is the customer identifier
#         # print(f"Received Comp_name: {comp_name}")
#         customer = Customer.objects.get(Comp_name=comp_name)
#         # customer, created = Customer.objects.get_or_create(Comp_name=comp_name)
#
#         generation_meter_form = GenerationMeterForm(request.POST)
#         if generation_meter_form.is_valid():
#             generation_meter = generation_meter_form.save(commit=False)
#             generation_meter.comp_name = comp_name  # Assuming Comp_name is a field in GenerationMeter
#             generation_meter.customer = customer
#             generation_meter.save()
#
#             return HttpResponse("Generation Meter data saved successfully.")
#     else:
#         generation_meter_form = GenerationMeterForm()
#
#     return render(request, 'customer/meters.html', {'generation_meter_form': generation_meter_form})

# def save_generation_meter(request):
#     if request.method == 'POST':
#         comp_name = request.POST.get('Comp_name')  # Assuming Comp_name is the customer identifier
#         # print(f"Received Comp_name: {comp_name}")
#         # customer = Customer.objects.get(Comp_name=comp_name)
#         # customer, created = Customer.objects.get_or_create(Comp_name=comp_name)
#
#         if request.method == 'POST':
#             customer, created = Customer.objects.get_or_create(Comp_name=comp_name)
#
#             row_count = int(request.POST.get('row_count'))
#
#             for i in range(row_count):
#                 form_data = {
#                     'comp_name': comp_name,
#                     'customer': customer,
#                     'make': request.POST.get(f'make_{i}'),  # Update the field names accordingly
#                     'capacity': request.POST.get(f'capacity_{i}'),
#                     'serial_no': request.POST.get(f'serial_no_{i}'),
#                 }
#
#                 generation_meter_form = GenerationMeterForm(form_data)
#                 if generation_meter_form.is_valid():
#                    generation_meter_form.save()
#
#                 # generation_meter_form = GenerationMeterForm(request.POST)
#                 # if generation_meter_form.is_valid():
#                 #     generation_meter = generation_meter_form.save(commit=False)
#                 #     generation_meter.comp_name = comp_name  # Assuming Comp_name is a field in GenerationMeter
#                 #     generation_meter.customer = customer
#                 #     generation_meter.save()
#
#             return HttpResponse("Generation Meter data saved successfully.")
#     else:
#         generation_meter_form = GenerationMeterForm()
#
#     return render(request, 'customer/meters.html', {'generation_meter_form': generation_meter_form})
#
# def save_generation_meter(request):
#     if request.method == 'POST':
#         comp_name = request.POST.get('Comp_name')  # Assuming Comp_name is the customer identifier
#
#         customer, created = Customer.objects.get_or_create(Comp_name=comp_name)
#
#         row_count = int(request.POST.get('row_count'))
#
#         for i in range(row_count):
#             form_data = {
#                 'comp_name': comp_name,
#                 'customer': customer,
#                 'make': request.POST.get(f'make_{i}'),  # Update the field names accordingly
#                 'capacity': request.POST.get(f'capacity_{i}'),
#                 'serial_no': request.POST.get(f'serial_no_{i}'),
#             }
#             print(form_data)
#             print(request.POST)
#             generation_meter_form = GenerationMeterForm(form_data)
#             if generation_meter_form.is_valid():
#                 # generation_meter = generation_meter_form.save()
#                 # generation_meter.save()
#
#                 generation_meter = generation_meter_form.save(commit=False)
#                 generation_meter.comp_name = comp_name  # Assuming Comp_name is a field in GenerationMeter
#                 generation_meter.customer = customer
#                 generation_meter.save()
#
#         return HttpResponse("Generation Meter data saved successfully.")
#     else:
#         generation_meter_form = GenerationMeterForm()
#
#     return render(request, 'customer/meters.html', {'generation_meter_form': generation_meter_form})

def save_generation_meter(request):
    # Process the data from the Generation Meter form
    comp_name = request.POST.get('Comp_name')  # Get the company name
    customer, created = Customer.objects.get_or_create(Comp_name=comp_name)

    row_count = int(request.POST.get('row_count', 0))  # Get the row count

    # Iterate through the rows and save data to the database
    for i in range(row_count):
        make = request.POST.get(f'make_{i}') or request.POST.get('make')
        capacity = request.POST.get(f'capacity_{i}') or request.POST.get('capacity')
        serial_no = request.POST.get(f'serial_no_{i}') or request.POST.get('serial_no')
        CT_make = request.POST.get(f'CT_make_{i}') or request.POST.get('CT_make')
        CT_capacity = request.POST.get(f'CT_capacity_{i}') or request.POST.get('CT_capacity')
        CT_serial_no = request.POST.get(f'CT_serial_no_{i}') or request.POST.get('CT_serial_no')
        AssignBy = request.user

        print(request.POST)
        # Print the received data for debugging
        # print(f'make_{i}: {make}, capacity_{i}: {capacity}, serial_no_{i}: {serial_no}')
        # Create a new instance of your model and save it to the database
        GenerationMeter.objects.create(
            comp_name=comp_name,
            customer=customer,
            make=make,
            capacity=capacity,
            serial_no=serial_no,
            CT_make = CT_make,
            CT_capacity = CT_capacity,
            CT_serial_no = CT_serial_no,
            AssignBy=AssignBy,
        )
    messages.success(request, 'Generation Meter data saved successfully.')

    return redirect('customer-meters')  # 'meters_page' is the name of your meters page URL pattern
    # return JsonResponse({'message': 'Data saved successfully'}, status=200)


def save_generation_ct(request):
    if request.method == 'POST':
        # Process the data from the Generation Meter form
        comp_name = request.POST.get('Comp_name')  # Get the company name

        # Check if the checkbox is present in the request.POST data and set required accordingly
        required = 'required' in request.POST

        # Convert the boolean value to 1 or 0
        required_value = int(required)

        customer, created = Customer.objects.get_or_create(Comp_name=comp_name)

        row_count = int(request.POST.get('row_count', 0))  # Get the row count

        # Iterate through the rows and save data to the database
        for i in range(row_count):
            make = request.POST.get(f'make_{i}') or request.POST.get('make')
            capacity = request.POST.get(f'capacity_{i}') or request.POST.get('capacity')
            serial_no = request.POST.get(f'serial_no_{i}') or request.POST.get('serial_no')

            print(request.POST)
            # Print the received data for debugging
            # print(f'make_{i}: {make}, capacity_{i}: {capacity}, serial_no_{i}: {serial_no}')
            # Create a new instance of your model and save it to the database
            GenerationCT.objects.create(
                comp_name=comp_name,
                customer=customer,
                make=make,
                capacity=capacity,
                serial_no=serial_no,
                required=required_value,
            )

        # Add this line to set success message
        messages.success(request, 'Generation CT data saved successfully.')
        #
        return redirect('customer-meters')  # 'meters_page' is the name of your meters page URL pattern
    # return JsonResponse({'message': 'Data saved successfully'}, status=200)


from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Meters, GenerationMeter, GenerationCT
from .forms import EditForm


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Meters, GenerationMeter, GenerationCT
from .forms import EditForm

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT
from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

#
# def edit_records(request):
#     comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
#
#     # Combine unique comp_names from all three models
#     comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)
#
#     if request.method == 'POST':
#         form = EditForm(request.POST)
#         if form.is_valid():
#             # Save the form data and update the records
#             form.save()
#
#             # Fetch records based on the selected company name after the update
#             selected_comp_name = form.cleaned_data['comp_name']
#             meters_records = Meters.objects.filter(comp_name=selected_comp_name)
#             generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
#             generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)
#
#             context = {
#                 'form': form,
#                 'comp_names': comp_names,
#                 'selected_comp_name': selected_comp_name,
#                 'meters_records': meters_records,
#                 'generation_meter_records': generation_meter_records,
#                 'generation_ct_records': generation_ct_records,
#             }
#
#             return render(request, 'customer/edit_meters.html', context)
#
#     else:
#         form = EditForm()
#
#     context = {
#         'form': form,
#         'comp_names': comp_names,
#     }
#
#     return render(request, 'customer/edit_meters.html', context)


# # views.py
#
# from django.shortcuts import render, redirect
# from .forms import EditForm
# from .models import Meters, GenerationMeter, GenerationCT
#
# def edit_records(request):
#     comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
#
#     # Combine unique comp_names from all three models
#     comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)
#
#     if request.method == 'POST':
#         form = EditForm(request.POST)
#         if form.is_valid():
#             selected_comp_name = form.cleaned_data['comp_name']
#
#             # Update records for Meters model
#             meters_records = Meters.objects.filter(comp_name=selected_comp_name)
#             for record in meters_records:
#                 record.capacity = form.cleaned_data.get(f'meters_capacity_{record.id}')
#                 # Update other fields similarly
#                 record.save()
#
#             # Update records for GenerationMeter model
#             generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
#             for record in generation_meter_records:
#                 record.capacity = form.cleaned_data.get(f'generation_meter_capacity_{record.id}')
#                 # Update other fields similarly
#                 record.save()
#
#             # Update records for GenerationCT model
#             generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)
#             for record in generation_ct_records:
#                 record.capacity = form.cleaned_data.get(f'generation_ct_capacity_{record.id}')
#                 # Update other fields similarly
#                 record.save()
#
#             return redirect('customer/edit_meters')  # Redirect to the same page after saving changes
#
#     else:
#         form = EditForm()
#
#     context = {
#         'form': form,
#         'comp_names': comp_names,
#     }
#
#     return render(request, 'customer/edit_meters.html', context)

from django.shortcuts import render, redirect
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

#
# def edit_records(request):
#     comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
#
#     comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)

#     selected_comp_name = None
#     meters_records = None
#     generation_meter_records = None
#     generation_ct_records = None
#
#     if request.method == 'POST':
#         form = EditForm(request.POST)
#         if form.is_valid():
#             selected_comp_name = form.cleaned_data['comp_name']
#
#             # Update records for Meters model
#             meters_records = Meters.objects.filter(comp_name=selected_comp_name)
#             for meter_record in meters_records:
#                 meter_record.make = form.cleaned_data.get('make', '')
#
#                 # Ensure 'capacity' is a valid number before saving
#                 capacity_value = form.cleaned_data.get('capacity', '')
#                 meter_record.capacity = int(capacity_value) if capacity_value.isdigit() else 0
#
#                 # Update other fields as needed
#                 meter_record.save()
#
#             # Update records for GenerationMeter model
#             generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
#             for gen_meter_record in generation_meter_records:
#                 gen_meter_record.make = form.cleaned_data.get('make', '')
#
#                 # Ensure 'capacity' is a valid number before saving
#                 capacity_value = form.cleaned_data.get('capacity', '')
#                 gen_meter_record.capacity = int(capacity_value) if capacity_value.isdigit() else 0
#
#                 # Update other fields as needed
#                 gen_meter_record.save()
#
#             # Update records for GenerationCT model
#             generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)
#             for gen_ct_record in generation_ct_records:
#                 gen_ct_record.make = form.cleaned_data.get('make', '')
#
#                 # Ensure 'capacity' is a valid number before saving
#                 capacity_value = form.cleaned_data.get('capacity', '')
#                 gen_ct_record.capacity = int(capacity_value) if capacity_value.isdigit() else 0
#
#                 # Update other fields as needed
#                 gen_ct_record.save()
#
#     else:
#         form = EditForm()
#
    # context = {
    #     'form': form,
    #     'comp_names': comp_names,
    #     'selected_comp_name': selected_comp_name,
    #     'meters_records': meters_records,
    #     'generation_meter_records': generation_meter_records,
    #     'generation_ct_records': generation_ct_records,
    # }
#
#     return render(request, 'customer/edit_meters.html', context)


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

# ... your other imports ...

# def edit_records(request):
    # comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
    # comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
    # comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
    #
    # # Combine unique comp_names from all three models
    # comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)
    #
    # selected_comp_name = None
    # meters_records = []
    # generation_meter_records = []
    # generation_ct_records = []
    #
    # if request.method == 'POST':
    #     form = EditForm(request.POST)
    #     if form.is_valid():
    #         # Fetch records based on the selected company name after the update
    #         selected_comp_name = form.cleaned_data['comp_name']
    #         meters_records = Meters.objects.filter(comp_name=selected_comp_name)
    #         generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
    #         generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)
    #
    # else:
    #     form = EditForm()
    #
    # context = {
    #     'form': form,
    #     'comp_names': comp_names,
    #     'selected_comp_name': selected_comp_name,
    #     'meters_records': meters_records,
    #     'generation_meter_records': generation_meter_records,
    #     'generation_ct_records': generation_ct_records,
    # }
    #
    # return render(request, 'customer/edit_meters.html', context)

    # from django.shortcuts import render, get_object_or_404
    # from django.http import HttpResponseRedirect
    # from django.urls import reverse

    # ... your other imports ...

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse



# ... other imports ...
#
# def edit_records(request):
#     comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
#
#     # Combine unique comp_names from all three models
#     comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)
#
#     selected_comp_name = None
#     records = []
#
#     if request.method == 'POST':
#         form = EditForm(request.POST)
#         if form.is_valid():
#             # Fetch records based on the selected company name after the update
#             selected_comp_name = form.cleaned_data['comp_name']
#             meters_records = Meters.objects.filter(comp_name=selected_comp_name)
#             generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
#             generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)
#
#             # Combine records from all models into a single list
#             records = list(meters_records.values('comp_name', 'make', 'capacity', 'serial_no')) + \
#                       list(generation_meter_records.values('comp_name', 'make', 'capacity', 'serial_no')) + \
#                       list(generation_ct_records.values('comp_name', 'make', 'capacity', 'serial_no'))
#
#     else:
#         form = EditForm()
#
#     context = {
#         'form': form,
#         'comp_names': comp_names,
#         'selected_comp_name': selected_comp_name,
#         'records': records,
#     }
#
#     return render(request, 'customer/edit_meters.html', context)


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

# ... other imports ...

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

# # ... other imports ...
#
# def edit_records(request):
#     comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
#
#     # Combine unique comp_names from all three models
#     comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)
#
#     selected_comp_name = None
#     records = []
#
#     if request.method == 'POST':
#         form = EditForm(request.POST)
#         if form.is_valid():
#             # Fetch records based on the selected company name after the update
#             selected_comp_name = form.cleaned_data['comp_name']
#             meters_records = Meters.objects.filter(comp_name=selected_comp_name)
#             generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
#             generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)
#
#             # Combine records from all models into a single list
#             records = list(meters_records.values('id', 'comp_name', 'make', 'capacity', 'serial_no')) + \
#                       list(generation_meter_records.values('id', 'comp_name', 'make', 'capacity', 'serial_no')) + \
#                       list(generation_ct_records.values('id', 'comp_name', 'make', 'capacity', 'serial_no'))
#
#             # Handle record deletion
#             if 'records_to_delete' in request.POST:
#                 records_to_delete = request.POST.getlist('records_to_delete')
#                 for record_id in records_to_delete:
#                     model_name, field_name, record_id = record_id.split('_')
#                     model = get_model_instance(model_name, record_id)
#                     try:
#                         model.delete()
#                         print(f"Successfully deleted record: {model_name} - {record_id}")
#                     except Exception as e:
#                         print(f"Error deleting record: {model_name} - {record_id}. Exception: {e}")
#
#                 # Redirect to the same page after deletion
#                 return HttpResponseRedirect(reverse('customer-edit_meters'))
#
#
#
#     else:
#         form = EditForm()
#
#     context = {
#         'form': form,
#         'comp_names': comp_names,
#         'selected_comp_name': selected_comp_name,
#         'records': records,
#     }
#
#     return render(request, 'customer/edit_meters.html', context)
#



import logging
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

# logger = logging.getLogger(__name__)
#
# def edit_records(request):
#     comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
#
#     # Combine unique comp_names from all three models
#     comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)
#
#     selected_comp_name = None
#     records = []
#
#     if request.method == 'POST':
#         form = EditForm(request.POST)
#         if form.is_valid():
#             # Fetch records based on the selected company name after the update
#             selected_comp_name = form.cleaned_data['comp_name']
#             meters_records = Meters.objects.filter(comp_name=selected_comp_name)
#             generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
#             generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)
#
#             # Combine records from all models into a single list
#             records = list(meters_records.values('id', 'comp_name', 'make', 'capacity', 'serial_no')) + \
#                       list(generation_meter_records.values('id', 'comp_name', 'make', 'capacity', 'serial_no')) + \
#                       list(generation_ct_records.values('id', 'comp_name', 'make', 'capacity', 'serial_no'))
#
#             # Handle record deletion
#
#             # Handle record deletion
#             if 'records_to_delete' in request.POST:
#                 records_to_delete_ids = request.POST.getlist('records_to_delete')
#                 for record_id in records_to_delete_ids:
#                     try:
#                         # Fetch the record instance
#                         record = get_object_or_404(Meters, id=record_id)
#                         # Delete the record
#                         record.delete()
#                         print(f"Successfully deleted record with ID: {record_id}")
#                     except Exception as e:
#                         print(f"Error deleting record with ID: {record_id}. Exception: {e}")
#
#                 # Refresh the records list after deletion
#                 meters_records = Meters.objects.filter(comp_name=selected_comp_name)
#                 generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
#                 generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)
#
#                 records = list(meters_records.values('id', 'comp_name', 'make', 'capacity', 'serial_no')) + \
#                           list(generation_meter_records.values('id', 'comp_name', 'make', 'capacity', 'serial_no')) + \
#                           list(generation_ct_records.values('id', 'comp_name', 'make', 'capacity', 'serial_no'))
#
#                 # Add a success message to the context
#                 success_message = "Records deleted successfully."
#                 context['success_message'] = success_message
#
#     else:
#         form = EditForm()
#
#     context = {
#         'form': form,
#         'comp_names': comp_names,
#         'selected_comp_name': selected_comp_name,
#         'records': records,
#     }
#
#     return render(request, 'customer/edit_meters.html', context)
#

from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

# def edit_records(request):
#     comp_names = Meters.objects.values_list('comp_name', flat=True).distinct()
#     selected_comp_name = None
#     selected_serial_no = None
#     records = []
#
#     if request.method == 'POST':
#         form = EditForm(request.POST)
#         if form.is_valid():
#             selected_comp_name = form.cleaned_data.get('comp_name')
#             selected_serial_no = form.cleaned_data.get('serial_no')
#
#             # Delete records with matching comp_name and serial_no from all three tables
#             try:
#                 if selected_serial_no:
#                     Meters.objects.filter(serial_no=selected_serial_no).delete()
#                     GenerationMeter.objects.filter(serial_no=selected_serial_no).delete()
#                     GenerationCT.objects.filter(serial_no=selected_serial_no).delete()
#                     success_message = "Records deleted successfully."
#                     # Fetch records again after deletion
#                     records = get_records(selected_comp_name, selected_serial_no)
#                 else:
#                     success_message = "Please select both company name and serial number."
#             except Exception as e:
#                 print(f"Error deleting records: {e}")
#                 success_message = "Error deleting records."
#     else:
#         form = EditForm()
#
#     context = {
#         'form': form,
#         'comp_names': comp_names,
#         'selected_comp_name': selected_comp_name,
#         'selected_serial_no': selected_serial_no,
#         'records': records,
#     }
#
#     return render(request, 'customer/edit_meters.html', context)
#
# def get_records(comp_name, serial_no):
#     meters_serial_nos = Meters.objects.filter(comp_name=comp_name).values_list('serial_no', flat=True).distinct()
#     generation_meter_serial_nos = GenerationMeter.objects.filter(comp_name=comp_name).values_list('serial_no', flat=True).distinct()
#     generation_ct_serial_nos = GenerationCT.objects.filter(comp_name=comp_name).values_list('serial_no', flat=True).distinct()
#
#     serial_nos = list(meters_serial_nos) + list(generation_meter_serial_nos) + list(generation_ct_serial_nos)
#     unique_serial_nos = list(set(serial_nos))
#
#     records = []
#
#     for serial_no in unique_serial_nos:
#         meters_records = Meters.objects.filter(comp_name=comp_name, serial_no=serial_no)
#         generation_meter_records = GenerationMeter.objects.filter(comp_name=comp_name, serial_no=serial_no)
#         generation_ct_records = GenerationCT.objects.filter(comp_name=comp_name, serial_no=serial_no)
#         records += list(meters_records) + list(generation_meter_records) + list(generation_ct_records)
#
#     return records

from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

# def edit_records(request):
#     comp_names = Meters.objects.values_list('comp_name', flat=True).distinct()
#     serial_nos = Meters.objects.values_list('serial_no', flat=True).distinct()
#
#     if request.method == 'POST':
#         form = EditForm(request.POST)
#         if form.is_valid():
#             comp_name = form.cleaned_data['comp_name']
#             serial_no = form.cleaned_data['serial_no']
#             # Handle record deletion
#             if 'delete_records' in request.POST:
#                 try:
#                     Meters.objects.filter(comp_name=comp_name, serial_no=serial_no).delete()
#                     GenerationMeter.objects.filter(comp_name=comp_name, serial_no=serial_no).delete()
#                     GenerationCT.objects.filter(comp_name=comp_name, serial_no=serial_no).delete()
#                     success_message = "Records deleted successfully."
#                 except Exception as e:
#                     success_message = f"Error deleting records: {e}"
#                 context = {
#                     'form': form,
#                     'comp_names': comp_names,
#                     'serial_nos': serial_nos,
#                     'success_message': success_message,
#                 }
#                 return render(request, 'customer/edit_meters.html', context)
#     else:
#         form = EditForm()
#
#     context = {
#         'form': form,
#         'comp_names': comp_names,
#         'serial_nos': serial_nos,
#     }
#
#     return render(request, 'customer/edit_meters.html', context)



from django.shortcuts import render, redirect
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

from django.shortcuts import render, redirect
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT


# delete meter records view
def edit_records(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
    comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
    comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()

    # Combine unique comp_names from all three models
    comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)

    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            selected_comp_name = form.cleaned_data['comp_name']

            if 'action' in request.POST and request.POST['action'] == 'delete':
                meters_to_delete = request.POST.getlist('meters_to_delete')
                delete_records(Meters, selected_comp_name, meters_to_delete)

            # if 'action' in request.POST and request.POST['action'] == 'delete':
                generation_meters_to_delete = request.POST.getlist('generation_meters_to_delete')
                delete_records(GenerationMeter, selected_comp_name, generation_meters_to_delete)

            # if 'action' in request.POST and request.POST['action'] == 'delete':
                generation_cts_to_delete = request.POST.getlist('generation_cts_to_delete')
                delete_records(GenerationCT, selected_comp_name, generation_cts_to_delete)




                # Add this line to set success message
                messages.success(request, 'Records Deleted successfully.')

                # Redirect to refresh the page after deletion
                return redirect('customer-edit_meters')

            # Fetch records after deletion
            meters_records = Meters.objects.filter(comp_name=selected_comp_name)
            generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
            generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)

            context = {
                'form': form,
                'comp_names': comp_names,
                'selected_comp_name': selected_comp_name,
                'meters_records': meters_records,
                'generation_meter_records': generation_meter_records,
                'generation_ct_records': generation_ct_records,
                'count1': count1,
                'notification1': notification1,
            }


            return render(request, 'customer/edit_meters.html', context)


    else:
        form = EditForm()

    context = {
        'form': form,
        'comp_names': comp_names,
    }

    return render(request, 'customer/edit_meters.html', context)

def delete_records(model, comp_name, record_ids):
    # Delete records from the provided model
    model.objects.filter(comp_name=comp_name, id__in=record_ids).delete()


from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

from django.db import transaction

from django.db import transaction

from django.shortcuts import redirect


def display_records(request):
    # comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
    # comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
    # comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    if request.user.is_superuser:
        # If user is a superuser or staff, fetch all comp_names
        comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
        comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
        comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
    elif request.user.is_staff:
        user = request.user

        # If user is not superuser or staff, filter comp_names based on related Engg_Assign
        comp_names_meters = Meters.objects.filter(customer_id__Engg_Assign=user).values_list('comp_name',
                                                                                          flat=True).distinct()
        comp_names_generation_meter = GenerationMeter.objects.filter(customer_id__Engg_Assign=user).values_list(
            'comp_name', flat=True).distinct()
        comp_names_generation_ct = GenerationCT.objects.filter(customer_id__Engg_Assign=user).values_list('comp_name',
                                                                                                       flat=True).distinct()
    # Combine unique comp_names from all three models
    comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)

    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            # Save the form data and update the records
            form.save()

            # Fetch records based on the selected company name after the update
            selected_comp_name = form.cleaned_data['comp_name']
            meters_records = Meters.objects.filter(comp_name=selected_comp_name)
            generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
            generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)

            context = {
                'form': form,
                'comp_names': comp_names,
                'selected_comp_name': selected_comp_name,
                'meters_records': meters_records,
                'generation_meter_records': generation_meter_records,
                'generation_ct_records': generation_ct_records,
                'count1': count1,
                'notification1': notification1,
            }

            return render(request, 'customer/display_meters.html', context)

    else:
        form = EditForm()

    context = {
        'form': form,
        'comp_names': comp_names,
        'count1': count1,
        'notification1': notification1,
    }

    return render(request, 'customer/display_meters.html', context)




from django.shortcuts import get_object_or_404
from .models import Meters, GenerationMeter, GenerationCT
def get_model_instance(model_name, record_id):
    if model_name == 'meters':
        instance = get_object_or_404(Meters, id=record_id)
        print(f"Got Meters instance: {instance}")
        return instance

    elif model_name == 'generation_meters':
        instance = get_object_or_404(GenerationMeter, id=record_id)
        print(f"Got GenerationMeter instance: {instance}")
        return instance
    elif model_name == 'generation_cts':
        instance = get_object_or_404(GenerationCT, id=record_id)
        print(f"Got GenerationCT instance: {instance}")
        return instance
    else:
        return None



# views.py

# from django.shortcuts import render, redirect
# from .forms import EditForm
# from .models import Meters, GenerationMeter, GenerationCT
#
# def edit_records(request):
#     comp_names_meters = Meters.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', flat=True).distinct()
#     comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', flat=True).distinct()
#
#     # Combine unique comp_names from all three models
#     comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)
#
#     if request.method == 'POST':
#         form = EditForm(request.POST)
#         if form.is_valid():
#             # Get the selected company name from the form
#             selected_comp_name = form.cleaned_data['comp_name']
#
#             # Update records for Meters model
#             meters_records = Meters.objects.filter(comp_name=selected_comp_name)
#             for record in meters_records:
#                 record.capacity = form.cleaned_data.get(f'meters_capacity_{record.id}')
#                 record.make = form.cleaned_data.get(f'meters_make_{record.id}')
#                 record.serial_no = form.cleaned_data.get(f'meters_serial_no_{record.id}')
#                 # Update other fields similarly
#                 record.save()
#
#             # Update records for GenerationMeter model
#             generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
#             for record in generation_meter_records:
#                 record.capacity = form.cleaned_data.get(f'generation_meter_capacity_{record.id}')
#                 record.make = form.cleaned_data.get(f'generation_meter_make_{record.id}')
#                 record.serial_no = form.cleaned_data.get(f'generation_meter_serial_no_{record.id}')
#                 # Update other fields similarly
#                 record.save()
#
#             # Update records for GenerationCT model
#             generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)
#             for record in generation_ct_records:
#                 record.capacity = form.cleaned_data.get(f'generation_ct_capacity_{record.id}')
#                 record.make = form.cleaned_data.get(f'generation_ct_make_{record.id}')
#                 record.serial_no = form.cleaned_data.get(f'generation_ct_serial_no_{record.id}')
#                 # Update other fields similarly
#                 record.save()
#
#             return redirect('customer/edit_meters')  # Redirect to the same page after saving changes
#
#     else:
#         form = EditForm()
#
#     context = {
#         'form': form,
#         'comp_names': comp_names,
#     }
#
#     return render(request, 'customer/edit_meters.html', context)
#
#
# def get_records_by_model(comp_name, model):
#     return model.objects.filter(comp_name=comp_name)
#
#


#
# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)
#     meters_count = 5  # Set a default value or retrieve it from somewhere
#     if request.method == 'POST':
#         # Get data from the POST request for each model
#         comp_name = request.POST.get('Comp_name')
#
#         # Meters data
#         # Meters data
#         meters = []
#         meters_count = int(request.POST.get('meters_count', 0))
#         for i in range(meters_count):
#             make = request.POST.get(f'm_meters_make_{i}')
#             capacity = request.POST.get(f'm_meters_capacity_{i}')
#             serial = request.POST.get(f'm_meters_serial_{i}')
#             meter = Meter(company_name=comp_name, make=make, capacity=capacity, serial_number=serial)
#             meter.save()
#             meters.append(meter)
#
#         # Transformer data
#         meter_type = request.POST.get('meter_type')
#         transformer = Transformer(
#             company_name=comp_name,
#             meter_type=meter_type,
#             make=request.POST.get('meter_make'),
#             capacity=request.POST.get('meter_capacity'),
#             serial_number=request.POST.get('meter_serial')
#         )
#         transformer.save()
#
#         # Generation Meter data
#         generation_meter = GenerationMeter(
#             company_name=comp_name,
#             make=request.POST.get('generation_meter_make'),
#             capacity=request.POST.get('generation_meter_capacity'),
#             serial_number=request.POST.get('generation_meter_serial')
#         )
#         generation_meter.save()
#
#         # Generation CT data
#         generation_ct_required = request.POST.get('generation_ct', 'Not Required') == 'Required'
#         generation_ct = GenerationCT(
#             company_name=comp_name,
#             required=generation_ct_required,
#             make=request.POST.get('generation_ct_make'),
#             capacity=request.POST.get('generation_ct_capacity'),
#             serial_number=request.POST.get('generation_ct_serial')
#         )
#         generation_ct.save()
#
#         # Redirect to a success page or wherever appropriate
#         return HttpResponse("Data saved successfully.")
#
#
#     # Render the form on GET request
#     return render(request, 'customer/add_meter.html', {'comp_names': comp_names})


#
# from django.shortcuts import render, redirect
# from django.forms import formset_factory
# from .models import Meter, Transformer, GenerationMeter, GenerationCT
# from .forms import MeterForm, TransformerForm, GenerationMeterForm, GenerationCTForm
#
# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)
#
#     MeterFormSet = formset_factory(MeterForm, extra=1)
#     TransformerFormSet = formset_factory(TransformerForm, extra=1)
#     GenerationMeterFormSet = formset_factory(GenerationMeterForm, extra=1)
#     GenerationCTFormSet = formset_factory(GenerationCTForm, extra=1)
#
#     if request.method == 'POST':
#         meter_formset = MeterFormSet(request.POST, prefix='meter')
#         transformer_formset = TransformerFormSet(request.POST, prefix='transformer')
#         generation_meter_formset = GenerationMeterFormSet(request.POST, prefix='generation_meter')
#         generation_ct_formset = GenerationCTFormSet(request.POST, prefix='generation_ct')
#
#         if all([meter_formset.is_valid(), transformer_formset.is_valid(),
#                 generation_meter_formset.is_valid(), generation_ct_formset.is_valid()]):
#             # Save the forms in the formsets
#             save_formset_data(meter_formset, Meters)
#             save_formset_data(transformer_formset, Transformer)
#             save_formset_data(generation_meter_formset, GenerationMeter)
#             save_formset_data(generation_ct_formset, GenerationCT)
#
#         return HttpResponse("Data saved successfully.")
#
#     else:
#         meter_formset = MeterFormSet(prefix='meter')
#         transformer_formset = TransformerFormSet(prefix='transformer')
#         generation_meter_formset = GenerationMeterFormSet(prefix='generation_meter')
#         generation_ct_formset = GenerationCTFormSet(prefix='generation_ct')
#
#     return render(request, 'customer/add_meter.html', {
#             'meter_formset': meter_formset,
#             'comp_names': comp_names,
#             'transformer_formset': transformer_formset,
#             'generation_meter_formset': generation_meter_formset,
#             'generation_ct_formset': generation_ct_formset,
#     })
#
#
#
# def save_formset_data(formset, model):
#     instances = []
#     for form in formset:
#         if form.has_changed():
#             instance = form.save(commit=False)
#             # If there's a foreign key relationship, set it here
#             # instance.some_foreign_key_field = some_value
#             instance.save()  # Save each instance individually
#             instances.append(instance)


# if instances:
    #     model.objects.bulk_create(instances)


# from .models import Meter
#
# #
#
# from django.shortcuts import render
# from django.http import HttpResponseRedirect
#
# def add_meter(request):
#         comp_names = Customer.objects.values_list('Comp_name', flat=True)
#         if request.method == 'POST':
#             comp_name = request.POST.get('Comp_name')
#             add_meter = None,
#
#             # Handle the initial textbox data
#             new_entry_initial = Meter(
#                 Comp_name=comp_name,
#                 meters=request.POST.get('meters'),
#                 m_meters_make=request.POST.get('m_meters_make'),
#                 meters_capacity=request.POST.get('m_meters_capacity'),
#                 meters_serial=request.POST.get('m_meters_serial'),
#                 meter_type=request.POST.get('meter_type'),
#                 meter_make=request.POST.get('meter_make'),
#                 meter_capacity=request.POST.get('meter_capacity'),
#                 meter_serial=request.POST.get('meter_serial'),
#                 generation_meter_make=request.POST.get('generation_meter_make'),
#                 generation_meter_capacity=request.POST.get('generation_meter_capacity'),
#                 generation_meter_serial=request.POST.get('generation_meter_serial'),
#                 generation_ct=request.POST.get('generation_ct'),
#                 generation_ct_make=request.POST.get('generation_ct_make'),
#                 generation_ct_capacity=request.POST.get('generation_ct_capacity'),
#                 generation_ct_serial=request.POST.get('generation_ct_serial')
#             )
#             new_entry_initial.save()  # Save initial textbox data to the database
#
#             # Handle the cloned data for 'Meters'
#             meters_rows = request.POST.getlist('m_meters_make_0')
#             for index, _ in enumerate(meters_rows):
#                 meters_make = request.POST.get(f'm_meters_make_{index}')
#                 meters_capacity = request.POST.get(f'm_meters_capacity_{index}')
#                 meters_serial = request.POST.get(f'm_meters_serial_{index}')
#
#                 # Create a new instance of your model for 'Meters' cloned data
#                 new_entry = Meter(
#                     Comp_name=comp_name,
#                     m_meters_make=meters_make,
#                     meters_capacity=meters_capacity,
#                     meters_serial=meters_serial
#                 )
#                 new_entry.save()  # Save the 'Meters' data to the database
#
#             # Handle the cloned data for 'Meters'
#             meters_rows = request.POST.getlist('meters')
#             for index, meters_type in enumerate(meters_rows):
#                 meters_make = request.POST.get(f'm_meters_make_{index}')
#                 meters_capacity = request.POST.get(f'm_meters_capacity_{index}')
#                 meters_serial = request.POST.get(f'm_meters_serial_{index}')
#
#                 # Create a new instance of your model for 'Meters' cloned data
#                 new_entry = Meter(
#                     Comp_name=comp_name,
#                     meters=meters_type,
#                     m_meters_make=meters_make,
#                     meters_capacity=meters_capacity,
#                     meters_serial=meters_serial,
#                 )
#                 new_entry.save()  # Save the 'Meters' data to the database
#
#             # Handle the cloned data for 'Meter Type'
#             meter_type_rows = request.POST.getlist('meter_type')
#             for index, meter_type in enumerate(meter_type_rows):
#                 transformer_make = request.POST.get(f'meter_make_{index}')
#                 transformer_capacity = request.POST.get(f'meter_capacity_{index}')
#                 transformer_serial = request.POST.get(f'meter_serial_{index}')
#
#                 # Create a new instance of your model for 'Meter Type' cloned data
#                 new_entry = Meter(
#                     Comp_name=comp_name,
#                     meter_type=meter_type,
#                     meter_make=transformer_make,
#                     meter_capacity=transformer_capacity,
#                     meter_serial=transformer_serial,
#
#                 )
#                 new_entry.save()  # Save the 'Meter Type' data to the database
#
#             # Handle the cloned data for 'Generation Meter'
#             generation_meter_make_rows = request.POST.getlist('generation_meter_make')
#             for index, generation_meter_make in enumerate(generation_meter_make_rows):
#                 generation_meter_capacity = request.POST.get(f'generation_meter_capacity_{index}')
#                 generation_meter_serial = request.POST.get(f'generation_meter_serial_{index}')
#
#                 # Create a new instance of your model for 'Generation Meter' cloned data
#                 new_entry = Meter(
#                     Comp_name=comp_name,
#                     generation_meter_make=generation_meter_make,
#                     generation_meter_capacity=generation_meter_capacity,
#                     generation_meter_serial=generation_meter_serial,
#                 )
#                 new_entry.save()  # Save the 'Generation Meter' data to the database
#
#             # Handle the cloned data for 'Generation CT'
#             generation_ct_rows = request.POST.getlist('generation_ct')
#             for index, generation_ct in enumerate(generation_ct_rows):
#                 generation_ct_make = request.POST.get(f'generation_ct_make_{index}')
#                 generation_ct_capacity = request.POST.get(f'generation_ct_capacity_{index}')
#                 generation_ct_serial = request.POST.get(f'generation_ct_serial_{index}')
#
#                 # Create a new instance of your model for 'Generation CT' cloned data
#                 new_entry = Meter(
#                     Comp_name=comp_name,
#                     generation_ct=generation_ct,
#                     generation_ct_make=generation_ct_make,
#                     generation_ct_capacity=generation_ct_capacity,
#                     generation_ct_serial=generation_ct_serial,
#                 )
#                 new_entry.save()  # Save the 'Generation CT' data to the database
#                 return HttpResponseRedirect('/customer/add_meter.html')  # Redirect to success page or other URL
#         return render(request, 'customer/add_meter.html', {'comp_names': comp_names})


#
# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)
#
#     if request.method == 'POST':
#         comp_name = request.POST['Comp_name']
#
#         for key in request.POST.keys():
#             index = None  # Initialize index variable outside the conditional checks
#             if key.startswith('m_meters_make'):
#                 index = key.split('_')[-1]
#                 print(f'm_meters_make:{index}')
#             elif key.startswith('meter_make'):
#                 index = key.split('_')[-1]
#                 print(f'meter_make:{index}')
#             elif key.startswith('generation_meter_make'):
#                 index = key.split('_')[-1]
#                 print(f'generation_meter_make:{index}')
#             elif key.startswith('generation_ct_make'):
#                 index = key.split('_')[-1]
#                 print(f'generation_ct_make:{index}')
#
#         customer = Meter(
#                     Comp_name=comp_name,
#                     meters=request.POST.get(f'meters', ''),
#                     meter_type=request.POST.get(f'meter_type', ''),  # Get the selected value (default: 'CT')
#                     generation_ct = request.POST.get(f'generation_ct', 'Required'),  # Get the selected value (default: 'Required')
#                 )
#         # for key in request.POST.keys():
#         #     if key.startswith('m_meters_make') or key.startswith('meter_make') or key.startswith(
#         #             'generation_meter_make') or key.startswith('generation_ct_make'):
#         #         index = key.split('_')[-1]
#         #         print(f'{key}:{index}')
#         if index == 'make':
#             customer.m_meters_make = request.POST.get(f'm_meters_make', '')
#             customer.meters_capacity = request.POST.get(f'm_meters_capacity', '')
#             customer.meters_serial = request.POST.get(f'm_meters_serial', '')
#         else:
#             customer.m_meters_make = request.POST.get(f'm_meters_make_{index}', '')
#             customer.meters_capacity = request.POST.get(f'm_meters_capacity_{index}', '')
#             customer.meters_serial = request.POST.get(f'm_meters_serial_{index}', '')
#
#         if index == 'make':
#             customer.meter_make = request.POST.get(f'meter_make', '')
#             customer.meter_capacity = request.POST.get(f'meter_capacity', '')
#             customer.meter_serial = request.POST.get(f'meter_serial', '')
#         else:
#             customer.meter_make = request.POST.get(f'meter_make_{index}', '')
#             customer.meter_capacity = request.POST.get(f'meter_capacity_{index}', '')
#             customer.meter_serial = request.POST.get(f'meter_serial_{index}', '')
#
#         if index == 'make':
#             customer.generation_meter_make = request.POST.get(f'generation_meter_make', '')
#             customer.generation_meter_capacity = request.POST.get(f'generation_meter_capacity', '')
#             customer.generation_meter_serial = request.POST.get(f'generation_meter_serial', '')
#         else:
#             customer.generation_meter_make = request.POST.get(f'generation_meter_make_{index}', '')
#             customer.generation_meter_capacity = request.POST.get(f'generation_meter_capacity_{index}', '')
#             customer.generation_meter_serial = request.POST.get(f'generation_meter_serial_{index}', '')
#
#         if index == 'make':
#             customer.generation_ct_make = request.POST.get(f'generation_ct_make', '')
#             customer.generation_ct_capacity = request.POST.get(f'generation_ct_capacity', '')
#             customer.generation_ct_serial = request.POST.get(f'generation_ct_serial', '')
#         else:
#             customer.generation_ct_make = request.POST.get(f'generation_ct_make_{index}', '')
#             customer.generation_ct_capacity = request.POST.get(f'generation_ct_capacity_{index}', '')
#             customer.generation_ct_serial = request.POST.get(f'generation_ct_serial_{index}', '')
#
#         # customer.generation_ct = request.POST.get(f'generation_ct', 'Required')  # Get the selected value (default: 'Required')
#
#         customer.save()
#
#         return HttpResponse("Data saved successfully.")
#
#     return render(request, 'customer/add_meter.html', {'comp_names': comp_names})



#
#
# def add_meter(request):
#     comp_names = Customer.objects.values_list('Comp_name', flat=True)
#
#     if request.method == 'POST':
#         comp_name = request.POST['Comp_name']
#         section = ""
#         index = ""
#
#         # Sections as dictionaries to streamline the processing
#         sections = {
#             'meters': {
#                 'key': 'm_meters_make',
#                 'prefix': 'meters'
#             },
#             'transformer': {
#                 'key': 'Transformer_make',
#                 'prefix': 'transformer'
#             },
#             'generation_meter': {
#                 'key': 'generation_meter_make',
#                 'prefix': 'generation_meter'
#             },
#             'generation_ct': {
#                 'key': 'generation_ct_make',
#                 'prefix': 'generation_ct'
#             }
#         }
#
#         for section, data in sections.items():
#             for key in request.POST.keys():
#                 if key.startswith(data['key']):
#                     index = key.split('_')[-1]
#                     print(f'{data["key"]}: {index}')
#
#                     if section in key:
#                         customer = Meter(
#                             Comp_name=comp_name,
#                             meters=request.POST.get(f'{data["prefix"]}_meters', ''),
#                             meter_type=request.POST.get(f'{data["prefix"]}_meter_type', 'CT'),
#                             generation_ct=request.POST.get(f'{data["prefix"]}_generation_ct', 'Required')
#                         )
#
#                         customer.m_meters_make = request.POST.get(f'{data["prefix"]}_meters_make_{index}', '')
#                         customer.meters_capacity = request.POST.get(f'{data["prefix"]}_meters_capacity_{index}', '')
#                         customer.meters_serial = request.POST.get(f'{data["prefix"]}_meters_serial_{index}', '')
#                         customer.meter_make = request.POST.get(f'{data["prefix"]}_meter_make_{index}', '')
#                         customer.meter_capacity = request.POST.get(f'{data["prefix"]}_meter_capacity_{index}', '')
#                         customer.meter_serial = request.POST.get(f'{data["prefix"]}_meter_serial_{index}', '')
#                         customer.generation_meter_make = request.POST.get(f'{data["prefix"]}_generation_meter_make_{index}', '')
#                         customer.generation_meter_capacity = request.POST.get(f'{data["prefix"]}_generation_meter_capacity_{index}', '')
#                         customer.generation_meter_serial = request.POST.get(f'{data["prefix"]}_generation_meter_serial_{index}', '')
#                         customer.generation_ct_make = request.POST.get(f'{data["prefix"]}_generation_ct_make_{index}', '')
#                         customer.generation_ct_capacity = request.POST.get(f'{data["prefix"]}_generation_ct_capacity_{index}', '')
#                         customer.generation_ct_serial = request.POST.get(f'{data["prefix"]}_generation_ct_serial_{index}', '')
#
#                         customer.save()
#
#         return HttpResponse("Data saved successfully.")
#
#     return render(request, 'customer/add_meter.html', {'comp_names': comp_names})



    #
    #
    #     for i in range(num_rows):
    #         customer = Meter(
    #             Comp_name=request.POST['Comp_name'],
    #             meters=request.POST.getlist(f'meters_{i}')[0],  # Use [0] to get the selected value
    #             m_meters_make=request.POST.get(f'm_meters_make_{i}', ''),
    #             meters_capacity=request.POST.get(f'meters_capacity_{i}', ''),
    #             meters_serial=request.POST.get(f'meters_serial_{i}', ''),
    #             meter_type=request.POST.get(f'meter_type', 'CT'),  # Get the selected value (default: 'CT')
    #             meter_make=request.POST.get(f'meter_make', ''),
    #             meter_capacity=request.POST.get(f'meter_capacity', ''),
    #             meter_serial=request.POST.get(f'meter_serial', ''),
    #             generation_meter_make=request.POST.get(f'generation_meter_make', ''),
    #             generation_meter_capacity=request.POST.get(f'generation_meter_capacity', ''),
    #             generation_meter_serial=request.POST.get(f'generation_meter_serial', ''),
    #             generation_ct=request.POST.get(f'generation_ct', 'Required'),  # Get the selected value (default: 'Required')
    #             generation_ct_make=request.POST.get(f'generation_ct_make', ''),
    #             generation_ct_capacity=request.POST.get(f'generation_ct_capacity', ''),
    #             generation_ct_serial=request.POST.get(f'generation_ct_serial', '')
    #         )
    #         customer.save()
    #
    #     return HttpResponse("Data saved successfully.")
    #
    # return render(request, 'customer/add_meter.html', {'comp_names': comp_names})
    #
    #


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
    customer = None

    if request.method == 'POST':
        search_by = request.POST.get('search_by', 'staff')  # Get the selected option from the form

        if search_by == 'staff':
            staff_assignee_id = request.POST.get('staff_assignee', '')
            report_filter = request.POST.get('report_filter', 'all')  # Get the selected filter option
            status_filter = request.POST.get('status_filter', '')  # Get the selected status filter option

            customer = Customer.objects.all()  # Get all fire reports initially

            if staff_assignee_id and staff_assignee_id != 'all':
                staff_assignee = User.objects.get(pk=staff_assignee_id)
                customer = customer.filter(Engg_Assign_id=staff_assignee_id)

            if report_filter == 'week':
                # Filter reports for the selected staff by week
                start_of_week = timezone.now().date() - timezone.timedelta(days=timezone.now().date().weekday())
                customer = customer.filter(po_date__gte=start_of_week)

            elif report_filter == 'month':
                # Filter reports for the selected staff by month
                start_of_month = timezone.now().date().replace(day=1)
                customer = customer.filter(po_date__gte=start_of_month)

            # Apply status_filter based on the selected option
            if status_filter:
                customer = customer.filter(Cust_type=status_filter)

        else:
            consumer_search_data = request.POST.get('consumer_search_data', '')
            if consumer_search_data:
                customer = Customer.objects.filter(
                    Q(Comp_name__icontains=consumer_search_data) |
                    # Q(phone=consumer_search_data) |
                    Q(City__icontains=consumer_search_data)
                )
                # Apply status_filter based on the selected option
                if status_filter:
                    customer = customer.filter(Cust_type=status_filter)

    else:
        customer = None

    context = {
        'search_by': search_by,
        'staff_list': staff_list,
        'customer': customer,
        'staff_assignee': staff_assignee,
        'report_filter': report_filter,
        'status_filter': status_filter,  # Add status_filter to the context
        'consumer_search_data': consumer_search_data,
        'notification1': notification1,
        'count1': count1,
    }
    return render(request, 'customer/search_by_staff.html', context)

def filter_data(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # departments = Profile.objects.values_list('department', flat=True).distinct()
    all_users = User.objects.filter(is_staff=1, is_active=0)
    unique_departments = set(user.profile.department for user in all_users)
    employees = User.objects.filter(is_staff=1, is_active=0)

    if request.method == 'POST':
        unique_departments = request.POST.get('department')
        employee_id = request.POST.get('AssignTo')
        # print(request.POST)

        all_users = User.objects.filter(is_staff=1, is_active=0)
        unique_departments = set(user.profile.department for user in all_users)
        employees = User.objects.filter(is_staff=1, is_active=0)

        all_users1 = User.objects.filter(is_staff=1, is_active=1)
        unique_departments1 = set(user.profile.department for user in all_users1)
        employees1 = User.objects.filter(is_staff=1, is_active=1)

        filtered_customers = Customer.objects.filter(Engg_Assign=employee_id)
        print(filtered_customers)

        return render(request, 'customer/change_staff.html', {'filtered_customers': filtered_customers, 'unique_departments': unique_departments, 'employees': employees, 'all_users': all_users, 'unique_departments1': unique_departments1, 'employees1': employees1, 'all_users1': all_users1, 'notification1': notification1,
                'count1': count1,})

    return render(request, 'customer/change_staff.html', {'unique_departments': unique_departments, 'employees': employees, 'all_users': all_users, 'notification1': notification1,
                'count1': count1,})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer
from django.contrib.auth.models import User

def save_change_staff(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    all_users = User.objects.filter(is_staff=1, is_active=0)
    unique_departments = set(user.profile.department for user in all_users)
    employees = User.objects.filter(is_staff=1, is_active=0)

    context = {
        'all_users': all_users,
        'unique_departments': unique_departments,
        'employees': employees,
        'notification1': notification1,
        'count1': count1,
    }

    if request.method == 'POST':
        selected_customer_ids = request.POST.getlist('selected_customers[]')
        department = request.POST.get('department1')
        # Retrieve AssignTo1 as a list
        engg_assign_list = request.POST.getlist('AssignTo1[]')

        # Loop through selected customer IDs and update the department and Engg_Assign fields
        for customer_id, engg_assign in zip(selected_customer_ids, engg_assign_list):
            # print("Processing customer ID:", customer_id)  # Print customer ID for debugging
            # print("Type of customer ID:", type(customer_id))  # Print type of customer ID for debugging
            # print("AssignTo1 value:", engg_assign)  # Print AssignTo1 value for debugging

            # Convert customer ID to integer
            try:
                customer_id_int = int(customer_id)
                print("Converted customer ID to int:", customer_id_int)  # Print converted ID for debugging
                customer = Customer.objects.get(Cust_id=customer_id_int)
                print("Found customer:", customer)  # Print customer object for debugging

                # Update Engg_Assign field
                # try:
                engg_user = User.objects.get(id=engg_assign)
                customer.Engg_Assign = engg_user
                customer.save()
                # # Add this line to set success message
                messages.success(request, 'The Consumer has been transferred to the Current Employee successfully.')
                # except User.DoesNotExist:
                #     print(f"User with username {engg_assign} does not exist.")

            except ValueError:
                print(f"Invalid customer ID: {customer_id}")  # Print error message for debugging
            except Customer.DoesNotExist:
                print(f"Customer with ID {customer_id_int} does not exist.")  # Print error message for debugging
            except Exception as e:
                print(f"Error occurred: {e}")  # Print any other unexpected errors for debugging

            # Redirect after processing POST data to avoid re-submitting form on refresh
        return render(request, 'customer/change_staff.html', context)

    else:
        return render(request, 'customer/change_staff.html', context)

from .models import MSEB, Customer
from django.http import JsonResponse
from django.shortcuts import render
from .models import Customer, MSEB

# def mseb_view(request):
#     customers = Customer.objects.values_list('Comp_name', flat=True)  # Get company names from Customer table
#
#     # if request.method == 'POST' and request.is_ajax():
#     #     comp_name = request.POST.get('compName')
#     #     customer = Customer.objects.get(Comp_name=comp_name)
#     #     current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     #     print(request.POST)
#     #
#     #     # Get or create the MSEB instance for the given company name
#     #     mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
#     #
#     #     # mseb_instance.customer = customer
#     #
#     #     # Update the MSEB instance with form data
#     #     mseb_instance.load_extension = request.POST.get('load_extension_ok') == 'on'
#     #     mseb_instance.load_extension_date = current_time
#     #
#     #     mseb_instance.flisibility = request.POST.get('flisibility_ok') == 'ok'
#     #     mseb_instance.flisibility_date = current_time
#     #
#     #     mseb_instance.quotation = request.POST.get('quotation_ok') == 'ok'
#     #     mseb_instance.quotation_date = current_time
#     #
#     #     mseb_instance.sent_to_bill = request.POST.get('sent_to_bill_ok') == 'ok'
#     #     mseb_instance.sent_to_bill_date = current_time
#     #
#     #     mseb_instance.net_meter = request.POST.get('net_meter_ok') == 'ok'
#     #     mseb_instance.net_meter_date = current_time
#     #
#     #     mseb_instance.flexibility = request.POST.get('flexibility_ok') == 'ok'
#     #     mseb_instance.flexibility_date = current_time
#     #
#     #     mseb_instance.approval = request.POST.get('approval_ok') == 'ok'
#     #     mseb_instance.approval_date = current_time
#     #
#     #     mseb_instance.meter_testing = request.POST.get('meter_testing_ok') == 'ok'
#     #     mseb_instance.meter_testing_date = current_time
#     #
#     #     mseb_instance.agreement = request.POST.get('agreement_ok') == 'ok'
#     #     mseb_instance.agreement_date = current_time
#     #
#     #     mseb_instance.release = request.POST.get('release_ok') == 'ok'
#     #     mseb_instance.release_date = current_time
#     #
#     #     mseb_instance.installation_date = request.POST.get('installation_date_ok') == 'ok'
#     #     mseb_instance.installation_date_date = current_time
#     #
#     #     # Save the MSEB instance
#     #     mseb_instance.save()
#     #
#     #     return JsonResponse({'status': 'success', 'message': 'Record saved successfully'})
#     if request.method == 'POST' and request.is_ajax():
#         comp_name = request.POST.get('compName')
#         customer = Customer.objects.get(Comp_name=comp_name)
#         current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
#         # Get or create the MSEB instance for the given company name
#         mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
#
#         # Update the MSEB instance with form data
#         field_name = request.POST.get('fieldName')  # Get the name of the field/checkbox
#         field_value = request.POST.get('isChecked') == 'true'  # Get the value of the checked checkbox
#
#         # Set the field value based on the field name
#         setattr(mseb_instance, field_name, field_value)
#         setattr(mseb_instance, f"{field_name}_date", current_time)  # Update corresponding date field
#
#         # Save the MSEB instance
#         mseb_instance.save()
#
#         return JsonResponse({'status': 'success', 'message': 'Record saved successfully'})
#     else:
#         return render(request, 'customer/MSEB.html', {'customers': customers})
# from datetime import datetime  # Import datetime module
# import datetime

# AUto genrate Date code save the records

# def mseb_view(request):
#     customers = Customer.objects.values_list('Comp_name', flat=True)
#
#     if request.method == 'POST' and request.is_ajax():
#         comp_name = request.POST.get('compName')
#         customer = Customer.objects.get(Comp_name=comp_name)
#         current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
#         # Get or create the MSEB instance for the given company name
#         mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
#
#         # Set the customer field of MSEB instance
#         mseb_instance.customer = customer
#
#         # Update the MSEB instance with form data
#         field_name = request.POST.get('fieldName')
#         field_value = request.POST.get('isChecked') == 'true'
#
#         # Check if the field is already filled
#         if getattr(mseb_instance, field_name) == field_value:
#             return JsonResponse({'status': 'success', 'message': 'Record already exists and field is unchanged'})
#
#         # Nullify the field value if it's being unchecked
#         if not field_value:
#             setattr(mseb_instance, field_name, None)
#             setattr(mseb_instance, f"{field_name}_date", None)
#         else:
#             # Set the field value and update corresponding date field
#             setattr(mseb_instance, field_name, field_value)
#             setattr(mseb_instance, f"{field_name}_date", current_time)
#
#         # Set the current user's ID to the mseb_instance
#         mseb_instance.AssignBy = request.user
#         # Save the MSEB instance
#         mseb_instance.save()
#
#         return JsonResponse({'status': 'success', 'message': 'Record saved successfully'})
#     else:
#         return render(request, 'customer/MSEB.html', {'customers': customers})
#

# def mseb_view(request):
#     customers = Customer.objects.values_list('Comp_name', flat=True)
#
#     if request.method == 'POST' and request.is_ajax():
#         comp_name = request.POST.get('compName')
#         customer = Customer.objects.get(Comp_name=comp_name)
#         current_time = datetime.datetime.now().strftime('%Y-%m-%d')
#
#         # Get or create the MSEB instance for the given company name
#         mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
#
#         # Set the customer field of MSEB instance
#         mseb_instance.customer = customer
#
#         # Update the MSEB instance with form data
#         field_name = request.POST.get('fieldName')
#         field_value = request.POST.get('isChecked') == 'true'
#
#         # Get the manually entered completion date from the AJAX request
#         completion_date = request.POST.get('createdAt')
#         completion_date = datetime.datetime.strptime(completion_date, '%Y-%m-%d').strftime('%Y-%m-%d')
#
#         # Check if completion_date is provided
#         if completion_date:
#             # Set the field value and update corresponding date field
#             setattr(mseb_instance, field_name, field_value)
#             setattr(mseb_instance, f"{field_name}_date", completion_date)
#         else:
#             # If completion_date is not provided, default to current time
#             setattr(mseb_instance, f"{field_name}_date", current_time)
#
#         # Set the current user's ID to the mseb_instance
#         mseb_instance.AssignBy = request.user
#
#         # Save the MSEB instance
#         mseb_instance.save()
#
#         return JsonResponse({'status': 'success', 'message': 'Record saved successfully'})
#     else:
#         return render(request, 'customer/MSEB.html', {'customers': customers})


import pytz
from django.utils import timezone

import pytz
from django.utils import timezone


def mseb_view(request):
    customers = Customer.objects.values_list('Comp_name', flat=True)

    if request.method == 'POST' and request.is_ajax():
        comp_name = request.POST.get('compName')
        customer = Customer.objects.get(Comp_name=comp_name)

        # Get the manually entered completion date from the AJAX request
        completion_date = request.POST.get('createdAt')

        # Convert the completion_date string to a timezone-aware datetime object
        if completion_date:
            # Assuming the completion date is in UTC timezone
            completion_datetime = timezone.make_aware(datetime.datetime.strptime(completion_date, '%Y-%m-%d'),
                                                      timezone=pytz.UTC)
        else:
            # If no completion_date is provided, default to current time
            completion_datetime = timezone.now()

        # Get or create the MSEB instance for the given company name
        mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)

        # Set the customer field of MSEB instance
        mseb_instance.customer = customer

        # Update the MSEB instance with form data
        field_name = request.POST.get('fieldName')
        field_value = request.POST.get('isChecked') == 'true'

        # Set the field value and update corresponding date field
        setattr(mseb_instance, field_name, field_value)
        setattr(mseb_instance, f"{field_name}_date", completion_datetime)

        # Set the current user's ID to the mseb_instance
        mseb_instance.AssignBy = request.user

        # Save the MSEB instance
        mseb_instance.save()

        return JsonResponse({'status': 'success', 'message': 'Record saved successfully'})
    else:
        return render(request, 'customer/MSEB.html', {'customers': customers})


# def mseb_view(request):
#     if request.method == 'POST' and request.is_ajax():
#         comp_name = request.POST.get('compName')
#
#         # Check if the company name exists in the MSEB table
#         mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
#
#         # If the instance is created, initialize fields with default values
#         if created:
#             mseb_instance.field1 = False  # Example field with default value
#             mseb_instance.save()
#
#         # Get all fields and their values for the MSEB instance
#         fields_data = {field.name: getattr(mseb_instance, field.name) for field in MSEB._meta.get_fields()}
#
#         return JsonResponse({'status': 'success', 'fields_data': fields_data})
#     else:
#         # Get the list of company names from the Customer table
#         customers = Customer.objects.values_list('Comp_name', flat=True)
#
#         return render(request, 'customer/MSEB.html', {'customers': customers})

#
# def mseb_view(request):
#     if request.method == 'POST' and request.is_ajax():
#         comp_name = request.POST.get('compName')
#
#         if not comp_name:  # If no company name is selected
#             return JsonResponse({'status': 'error', 'message': 'No company name selected'})
#
#         # Check if the company name exists in the MSEB table
#         try:
#             mseb_instance = MSEB.objects.get(comp_name=comp_name)
#         except MSEB.DoesNotExist:
#             # If the company name doesn't exist, create a new MSEB instance
#             mseb_instance = MSEB(comp_name=comp_name)
#             mseb_instance.save()
#
#         # Update the MSEB instance with form data
#         for field in MSEB._meta.get_fields():
#             field_name = field.name
#             if field_name != 'comp_name':  # Exclude 'comp_name' field from update
#                 field_value = request.POST.get(field_name, False) == 'true'
#                 setattr(mseb_instance, field_name, field_value)
#
#         # Set 'updated_at' field to current timestamp
#         mseb_instance.updated_at = datetime.datetime.now()
#         mseb_instance.save()
#
#         return JsonResponse({'status': 'success', 'message': 'Record saved successfully'})
#     else:
#         # Get the list of company names from the Customer table
#         customers = Customer.objects.values_list('Comp_name', flat=True)
#         return render(request, 'customer/MSEB.html', {'customers': customers})


    # if request.method == 'POST':
    #     selected_customer_id = request.POST.get('Comp_name')
    #     selected_customer = MSEB.objects.get(comp_name=selected_customer_id)
    #     compName = MSEB.objects.get(comp_name=selected_customer_id)
    #     selected_customer_fields = {field.name: getattr(selected_customer, field.name) for field in
    #                                 selected_customer._meta.fields if field.get_internal_type() == 'BooleanField'}
    #     return render(request, 'customer/mseb.html',
    #                   {'customers': customers, 'selected_customer': selected_customer,
    #                    'selected_customer_fields': selected_customer_fields, 'compName': compName})
    # else:
    #     return render(request, 'customer/MSEB.html', {'customers': customers})


# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from .models import Customer, MSEB
#
# def mseb_view(request):
#     customers = Customer.objects.values_list('Comp_name', flat=True)  # Get company names from Customer table
#
#     if request.method == 'POST':
#         selected_customer_id = request.POST.get('Comp_name')
#
#         try:
#             selected_customer = MSEB.objects.get(comp_name=selected_customer_id)
#             selected_customer_fields = {field.name: getattr(selected_customer, field.name) for field in
#                                         selected_customer._meta.fields if field.get_internal_type() == 'BooleanField'}
#             comp_name = selected_customer.comp_name  # Rename variable for clarity
#             if request.POST.get('update'):  # If form is submitted for updating
#                 for field in selected_customer_fields:
#                     updated_value = request.POST.get(field)
#                     setattr(selected_customer, field, updated_value)
#                 selected_customer.save()
#                 return HttpResponse("Fields Updated Successfully!")  # You might want to redirect to a success page instead
#             else:
#                 return render(request, 'customer/mseb.html',
#                               {'customers': customers, 'selected_customer': selected_customer,
#                                'selected_customer_fields': selected_customer_fields, 'compName': comp_name})
#         except MSEB.DoesNotExist:
#             return HttpResponse("Selected company does not exist!")  # Handle case where selected company doesn't exist
#         except Exception as e:
#             return HttpResponse("An error occurred: " + str(e))  # Handle other errors
#     else:
#         return render(request, 'customer/MSEB.html', {'customers': customers})
#
from django.core.serializers import serialize
from django.http import JsonResponse
from .models import MSEB
#
# def get_mseb_data(request):
#     comp_name = request.GET.get('comp_name')  # Get the selected company name
#     mseb_instance = MSEB.objects.filter(comp_name=comp_name).first()  # Fetch the MSEB instance for the selected company
#
#
#     if mseb_instance:
#         # Prepare the data dictionary
#         mseb_data = {
#             'load_extension_ok': {
#                 'value': mseb_instance.load_extension,
#                 'created_at': mseb_instance.load_extension_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.load_extension_date else None,
#             },
#             'flisibility_ok': {
#                 'value': mseb_instance.flisibility,
#                 'created_at': mseb_instance.flisibility_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.flisibility_date else None,
#             },
#             'quotation_ok': {
#                 'value': mseb_instance.quotation,
#                 'created_at': mseb_instance.quotation_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.quotation_date else None,
#             },
#             'sent_to_bill_ok': {
#                 'value': mseb_instance.sent_to_bill,
#                 'created_at': mseb_instance.sent_to_bill_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.sent_to_bill_date else None,
#             },
#             'net_meter_ok': {
#                 'value': mseb_instance.net_meter,
#                 'created_at': mseb_instance.net_meter_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.net_meter_date else None,
#             },
#             'flexibility_ok': {
#                 'value': mseb_instance.flexibility,
#                 'created_at': mseb_instance.flexibility_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.flexibility_date else None,
#             },
#             'approval_ok': {
#                 'value': mseb_instance.approval,
#                 'created_at': mseb_instance.approval_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.approval_date else None,
#             },
#             'meter_testing_ok': {
#                 'value': mseb_instance.meter_testing,
#                 'created_at': mseb_instance.meter_testing_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.meter_testing_date else None,
#             },
#             'agreement_ok': {
#                 'value': mseb_instance.agreement,
#                 'created_at': mseb_instance.agreement_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.agreement_date else None,
#             },
#             'release_ok': {
#                 'value': mseb_instance.release,
#                 'created_at': mseb_instance.release_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.release_date else None,
#             },
#             'installation_date_ok': {
#                 'value': mseb_instance.installation_date,
#                 'created_at': mseb_instance.installation_date_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.installation_date_date else None,
#             },
#             # Add other fields here
#         }
#         return JsonResponse(mseb_data)
#     else:
#         return JsonResponse({'error': 'No data found for the selected company'})


from django.http import JsonResponse
from .models import MSEB

# def get_mseb_data(request):
#     comp_name = request.GET.get('comp_name')
#     mseb_instance = MSEB.objects.filter(comp_name=comp_name).first()
#     customer = Customer.objects.get(Comp_name=comp_name)
#     if mseb_instance:
#         mseb_data = {}
#         fields = ['load_extension', 'flisibility', 'quotation', 'sent_to_bill', 'net_meter', 'flexibility', 'approval', 'meter_testing', 'agreement', 'release', 'installation_date']
#
#         # Assuming 'current_load' and 'loadsancution' are fields in the Customer model
#         current_load = customer.current_load
#         loadsancution = customer.loadsancution
#
#         # Add current_load and loadsancution to mseb_data
#         mseb_data['current_load'] = current_load
#         mseb_data['loadsancution'] = loadsancution

#         for field in fields:
#             field_name = f"{field}_ok"
#             created_at_field = f"{field}_date"
#             mseb_data[field_name] = {
#                 'value': getattr(mseb_instance, field),
#                 'created_at': getattr(mseb_instance, created_at_field).strftime('%Y-%m-%d %H:%M:%S') if getattr(mseb_instance, created_at_field) else None,
#             }
#
#         return JsonResponse(mseb_data)
#     else:
#         return JsonResponse({'error': 'No data found for the selected company'})
#
#
#
# def get_mseb_data(request):
#     comp_name = request.GET.get('comp_name')
#     mseb_instance = MSEB.objects.filter(comp_name=comp_name).first()
#     customer = Customer.objects.get(Comp_name=comp_name)
#     if mseb_instance:
#         mseb_data = {}
#
#
#         current_load = customer.current_load
#         loadsancution = customer.loadsancution
#
#         # Add current_load and loadsancution to mseb_data
#         mseb_data['current_load'] = current_load
#         mseb_data['loadsancution'] = loadsancution
#
#         # Check if both values are equal
#         if current_load == loadsancution:
#             # If equal, show all fields from net meter field and onwards
#             fields = ['net_meter', 'flexibility', 'approval', 'meter_testing', 'agreement', 'release',
#                       'installation_date']
#         else:
#             # If not equal, show all fields
#             fields = ['load_extension', 'flisibility', 'quotation', 'sent_to_bill', 'net_meter', 'flexibility',
#                       'approval', 'meter_testing', 'agreement', 'release', 'installation_date']
#
#         for field in fields:
#             field_name = f"{field}_ok"
#             created_at_field = f"{field}_date"
#             mseb_data[field_name] = {
#                 'value': getattr(mseb_instance, field),
#                 'created_at': getattr(mseb_instance, created_at_field).strftime('%Y-%m-%d %H:%M:%S') if getattr(
#                     mseb_instance, created_at_field) else None,
#             }
#
#         return JsonResponse(mseb_data)
#     else:
#         return JsonResponse({'error': 'No data found for the selected company'})

from django.shortcuts import render

from django.http import JsonResponse

from django.http import JsonResponse
from .models import MSEB, Customer

def get_mseb_data(request):
    comp_name = request.GET.get('comp_name')
    mseb_instance = MSEB.objects.filter(comp_name=comp_name).first()
    customer = Customer.objects.get(Comp_name=comp_name)
    if mseb_instance:
        mseb_data = {}

        current_load = customer.current_load
        loadsancution = customer.loadsancution

        # Add current_load and loadsancution to mseb_data
        mseb_data['current_load'] = current_load
        mseb_data['loadsancution'] = loadsancution

        # Check if both values are equal
        if current_load == loadsancution:
            # If equal, show all fields from net meter field and onwards
            fields = ['net_meter', 'flexibility', 'approval', 'meter_testing', 'agreement', 'release',
                      'installation_date']
        else:
            # If not equal, show all fields
            fields = ['load_extension', 'flisibility', 'quotation', 'sent_to_bill', 'net_meter', 'flexibility',
                      'approval', 'meter_testing', 'agreement', 'release', 'installation_date']

        for field in fields:
            field_name = f"{field}_ok"
            created_at_field = f"{field}_date"
            mseb_data[field_name] = {
                'value': getattr(mseb_instance, field),
                'created_at': getattr(mseb_instance, created_at_field).strftime('%Y-%m-%d %H:%M:%S') if getattr(
                    mseb_instance, created_at_field) else None,
            }


        return JsonResponse(mseb_data)
    else:
        return JsonResponse({'error': 'No data found for the selected company', 'current_load': customer.current_load, 'loadsancution': customer.loadsancution})

#
# def get_mseb_data(request):
#     comp_name = request.GET.get('comp_name')
#     mseb_instance = MSEB.objects.filter(comp_name=comp_name).first()
#     customer = Customer.objects.get(Comp_name=comp_name)
#     current_load = customer.current_load
#     loadsancution = customer.loadsancution
#     fields_to_display = []  # Initialize the list of fields to display
#
#     if mseb_instance:
#         mseb_data = {}
#         current_load = customer.current_load
#         loadsancution = customer.loadsancution
#
#         # Check if both values are equal
#         if current_load == loadsancution:
#             # If equal, show all fields from net_meter field and onwards
#             fields = ['net_meter', 'flexibility', 'approval', 'meter_testing', 'agreement', 'release',
#                       'installation_date']
#         else:
#             # If not equal, show all fields
#             fields = ['load_extension', 'flisibility', 'quotation', 'sent_to_bill', 'net_meter', 'flexibility',
#                       'approval', 'meter_testing', 'agreement', 'release', 'installation_date']
#
#         for field in fields:
#             field_name = f"{field}_ok"
#             created_at_field = f"{field}_date"
#             mseb_data[field_name] = {
#                 'value': getattr(mseb_instance, field),
#                 'created_at': getattr(mseb_instance, created_at_field).strftime('%Y-%m-%d %H:%M:%S') if getattr(
#                     mseb_instance, created_at_field) else None,
#             }
#
#         # Add current_load and loadsancution to mseb_data
#         mseb_data['current_load'] = current_load
#         mseb_data['loadsancution'] = loadsancution
#
#         return JsonResponse(mseb_data)
#     else:
#         # If MSEB data doesn't exist, determine which fields to display based on current_load and loadsancution
#         print(current_load)
#         print(loadsancution)
#
#         # Initialize the list of fields to display
#         # Retrieve current_load and loadsancution values
#         current_load = customer.current_load
#         loadsancution = customer.loadsancution
#         fields_to_display = []
#
#         if current_load == loadsancution:
#             # If current_load is equal to loadsancution, start displaying from 'net_meter' onwards
#             fields_to_display = ['net_meter', 'flexibility', 'approval', 'meter_testing', 'agreement', 'release',
#                                  'installation_date']
#         else:
#             # Otherwise, display all fields
#             fields_to_display = ['load_extension', 'flisibility', 'quotation', 'sent_to_bill', 'net_meter',
#                                  'flexibility', 'approval', 'meter_testing', 'agreement', 'release',
#                                  'installation_date']
#
#         # Return the list of fields to display
#         return JsonResponse({'fields_to_display': fields_to_display})
#

from django.shortcuts import redirect


# def get_mseb_data(request):
#     comp_name = request.GET.get('comp_name')
#     mseb_instance = MSEB.objects.filter(comp_name=comp_name).first()
#     customer = Customer.objects.get(Comp_name=comp_name)
#
#     if mseb_instance:
#         mseb_data = {}
#
#         current_load = customer.current_load
#         loadsancution = customer.loadsancution
#
#         # Add current_load and loadsancution to mseb_data
#         mseb_data['current_load'] = current_load
#         mseb_data['loadsancution'] = loadsancution
#
#         # Check if both values are equal
#         if current_load == loadsancution:
#             # If equal, show all fields from net meter field and onwards
#             fields = ['net_meter', 'flexibility', 'approval', 'meter_testing', 'agreement', 'release',
#                       'installation_date']
#         else:
#             # If not equal, show all fields
#             fields = ['load_extension', 'flisibility', 'quotation', 'sent_to_bill', 'net_meter', 'flexibility',
#                       'approval', 'meter_testing', 'agreement', 'release', 'installation_date']
#
#         for field in fields:
#             field_name = f"{field}_ok"
#             created_at_field = f"{field}_date"
#             mseb_data[field_name] = {
#                 'value': getattr(mseb_instance, field),
#                 'created_at': getattr(mseb_instance, created_at_field).strftime('%Y-%m-%d %H:%M:%S') if getattr(
#                     mseb_instance, created_at_field) else None,
#             }
#
#         return JsonResponse(mseb_data)
#     else:
#         # Check if current_load and loadsancution are equal
#         current_load = customer.current_load
#         loadsancution = customer.loadsancution
#         if current_load == loadsancution:
#             # If equal, redirect to MSEB1 HTML page
#             return redirect(
#                 'mseb1_page')  # 'mseb1_page' should be replaced with the appropriate URL name for MSEB1 page
#         else:
#             # If not equal, redirect to MSEB HTML page
#             return redirect('mseb_page')  # 'mseb_page' should be replaced with the appropriate URL name for MSEB page


from django.http import JsonResponse
from .models import Customer

def get_customer_data(request):
    if request.method == 'GET':
        comp_name = request.GET.get('comp_name')
        try:
            customer = Customer.objects.get(Comp_name=comp_name)
            # Assuming 'current_load' and 'loadsancution' are fields in the Customer model
            current_load = customer.current_load
            loadsancution = customer.loadsancution
            return JsonResponse({'current_load': current_load, 'loadsancution': loadsancution})
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

from django.http import JsonResponse
from .models import Customer, MSEB
#
# def get_mseb_data(request):
#     comp_name = request.GET.get('comp_name')
#     customer_instance = Customer.objects.filter(Comp_name=comp_name).first()
#     mseb_instance = MSEB.objects.filter(comp_name=comp_name).first()
#
#     if customer_instance:
#         mseb_data = {}
#         fields = ['load_extension', 'flisibility', 'quotation', 'sent_to_bill', 'net_meter', 'flexibility', 'approval', 'meter_testing', 'agreement', 'release', 'installation_date']
#
#         # Retrieve loadsancution and current_load values from Customer instance
#         loadsancution = customer_instance.loadsancution
#         current_load = customer_instance.current_load
#
#         for field in fields:
#             field_name = f"{field}_ok"
#             created_at_field = f"{field}_date"
#             mseb_data[field_name] = {
#                 'value': getattr(mseb_instance, field) if mseb_instance else None,
#                 'created_at': getattr(mseb_instance, created_at_field).strftime('%Y-%m-%d %H:%M:%S') if mseb_instance and getattr(mseb_instance, created_at_field) else None,
#                 'disabled': False  # By default, all checkboxes are enabled
#             }
#             # Add corresponding cancel checkbox for each field
#             mseb_data[f"{field}_cancel"] = {
#                 'disabled': False  # By default, all cancel checkboxes are enabled
#             }
#
#         # Check if loadsancution and current_load values match conditions
#         if loadsancution is not None and current_load is not None and mseb_instance:
#             if loadsancution is not None and current_load is not None and mseb_instance:
#                 if loadsancution == current_load:
#                     # Disable 'load_extension', 'flisibility', 'quotation', 'sent_to_bill' rows
#                     disabled_fields = ['load_extension', 'flisibility', 'quotation', 'sent_to_bill']
#                     for field in disabled_fields:
#                         mseb_data[f"{field}_ok"]['disabled'] = True
#                         mseb_data[f"{field}_cancel"]['disabled'] = True
#
#                     # Enable 'net_meter' row
#                     mseb_data['net_meter_ok']['disabled'] = False
#                     mseb_data['net_meter_cancel']['disabled'] = False
#                 else:
#                     # Disable all fields except 'net_meter'
#                     for field in fields:
#                         if field != 'net_meter':
#                             mseb_data[f"{field}_ok"]['disabled'] = True
#                             mseb_data[f"{field}_cancel"]['disabled'] = True
#
#         return JsonResponse(mseb_data)
#     else:
#         return JsonResponse({'error': 'No data found for the selected company'})



#
# from django.http import JsonResponse
# from .models import MSEB
# from django.utils import timezone
# import json
#
# def get_mseb_data(request):
#     if request.method == 'GET':
#         comp_name = request.GET.get('comp_name')  # Get the selected company name
#         mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
#
#         if created:
#             # If a new instance is created, initialize all fields to False
#             # mseb_instance.save()  # Save the newly created instance
#             comp_name = request.POST.get('compName')
#             customer = Customer.objects.get(Comp_name=comp_name)
#             current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
#             # Get or create the MSEB instance for the given company name
#             mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
#
#             # Update the MSEB instance with form data
#             field_name = request.POST.get('fieldName')  # Get the name of the field/checkbox
#             field_value = request.POST.get('isChecked') == 'true'  # Get the value of the checked checkbox
#
#             # Set the field value based on the field name
#             setattr(mseb_instance, field_name, field_value)
#             setattr(mseb_instance, f"{field_name}_date", current_time)  # Update corresponding date field
#
#             # Save the MSEB instance
#             mseb_instance.save()
#
#         data = {
#             'load_extension_ok': {
#                 'value': mseb_instance.load_extension,
#                 'created_at': mseb_instance.load_extension_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.load_extension_date else None,
#             },
#             'flisibility_ok': {
#                 'value': mseb_instance.flisibility,
#                 'created_at': mseb_instance.flisibility_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.flisibility_date else None,
#             },
#             'quotation_ok': {
#                 'value': mseb_instance.quotation,
#                 'created_at': mseb_instance.quotation_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.quotation_date else None,
#             },
#             'sent_to_bill_ok': {
#                 'value': mseb_instance.sent_to_bill,
#                 'created_at': mseb_instance.sent_to_bill_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.sent_to_bill_date else None,
#             },
#             'net_meter_ok': {
#                 'value': mseb_instance.net_meter,
#                 'created_at': mseb_instance.net_meter_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.net_meter_date else None,
#             },
#             'flexibility_ok': {
#                 'value': mseb_instance.flexibility,
#                 'created_at': mseb_instance.flexibility_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.flexibility_date else None,
#             },
#             'approval_ok': {
#                 'value': mseb_instance.approval,
#                 'created_at': mseb_instance.approval_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.approval_date else None,
#             },
#             'meter_testing_ok': {
#                 'value': mseb_instance.meter_testing,
#                 'created_at': mseb_instance.meter_testing_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.meter_testing_date else None,
#             },
#             'agreement_ok': {
#                 'value': mseb_instance.agreement,
#                 'created_at': mseb_instance.agreement_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.agreement_date else None,
#             },
#             'release_ok': {
#                 'value': mseb_instance.release,
#                 'created_at': mseb_instance.release_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.release_date else None,
#             },
#             'installation_date_ok': {
#                 'value': mseb_instance.installation_date,
#                 'created_at': mseb_instance.installation_date_date.strftime('%Y-%m-%d %H:%M:%S') if mseb_instance.installation_date_date else None,
#             },
#             # Add other fields here
#         }
#
#         return JsonResponse(data)
#     elif request.method == 'POST' and request.is_ajax():
#         # Process POST request for saving data
#         data = json.loads(request.body)
#
#         comp_name = data['comp_name']
#         mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
#
#         for field_name, field_data in data.items():
#             if field_name.endswith('_ok'):
#                 field_value = field_data['value']
#                 field_name_without_suffix = field_name[:-3]
#                 setattr(mseb_instance, field_name_without_suffix, field_value)
#
#                 if field_value:
#                     # If field value is True, set the corresponding date field to current time
#                     setattr(mseb_instance, field_name_without_suffix + '_date', timezone.now())
#
#         mseb_instance.save()  # Save the instance
#
#         return JsonResponse({'status': 'success'})


#
# def get_mseb_data(request):
#     comp_name = request.GET.get('comp_name')  # Get the selected company name
#     mseb_instance = MSEB.objects.filter(comp_name=comp_name).first()  # Fetch the MSEB instance for the selected company
#     print(request.GET)
#     if mseb_instance:
#         data = {
#             'load_extension_ok': mseb_instance.load_extension,
#             'flisibility_ok': mseb_instance.flisibility,
#             'quotation_ok': mseb_instance.quotation,
#             'sent_to_bill_ok': mseb_instance.sent_to_bill,
#             'net_meter_ok': mseb_instance.net_meter,
#             'flexibility_ok': mseb_instance.flexibility,
#             'approval_ok': mseb_instance.approval,
#             'meter_testing_ok': mseb_instance.meter_testing,
#             'agreement_ok': mseb_instance.agreement,
#             'release_ok': mseb_instance.release,
#             'installation_date_ok': mseb_instance.installation_date,
#             # Add other fields here
#         }
#         print(data)
#         return JsonResponse(data)
#     else:
#         return JsonResponse({'error': 'No data found for the selected company'})

    # if request.method == 'POST':
    #     selected_customer_id = request.POST.get('Comp_name')
    #     selected_customer = MSEB.objects.get(comp_name=selected_customer_id)
    #     compName = MSEB.objects.get(comp_name=selected_customer_id)
    #     selected_customer_fields = {field.name: getattr(selected_customer, field.name) for field in
    #                                 selected_customer._meta.fields if field.get_internal_type() == 'BooleanField'}
    #     return render(request, 'customer/mseb.html',
    #                   {'customers': customers, 'selected_customer': selected_customer,
    #                    'selected_customer_fields': selected_customer_fields, 'compName': compName})
    # else:
    #     return render(request, 'customer/MSEB.html', {'customers': customers})


    # customers = Customer.objects.values_list('Comp_name', flat=True)  # Get company names from Customer table
    # if request.method == 'POST' and request.is_ajax():
    #     comp_name = request.POST.get('compName')
    #     # customer = Customer.objects.get(Comp_name=comp_name)
    #     current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #
    #     # Get or create the MSEB instance for the given company name
    #     mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
    #
    #     # Update the MSEB instance with form data
    #     field_name = request.POST.get('fieldName')  # Get the name of the field/checkbox
    #     field_value = request.POST.get('isChecked') == 'true'  # Get the value of the checked checkbox
    #
    #     # Set the field value based on the field name
    #     setattr(mseb_instance, field_name, field_value)
    #     setattr(mseb_instance, f"{field_name}_date", current_time)  # Update corresponding date field
    #
    #     # Save the MSEB instance
    #     mseb_instance.save()
    #
    #     return JsonResponse({'status': 'success', 'message': 'Record saved successfully'})
    # else:
    #     return render(request, 'customer/MSEB.html', {'customers': customers})

# def get_mseb_data(request):
#     if request.method == 'POST' and request.is_ajax():
#         comp_name = request.POST.get('comp_name')
#         try:
#             mseb_entry = MSEB.objects.get(comp_name=comp_name)
#             # If the entry exists, return relevant data
#             data = {
#                 'exists': True,
#                 'values': {
#                     'load_extension_ok': mseb_entry.load_extension_ok,
#                     'flisibility_ok': mseb_entry.flisibility_ok,
#                     # Add other fields similarly
#                 }
#             }
#         except MSEB.DoesNotExist:
#             # If the entry doesn't exist, create a new one
#             MSEB.objects.create(comp_name=comp_name)
#             data = {
#                 'exists': False,
#                 'message': 'New entry created for {}'.format(comp_name)
#             }
#         return JsonResponse(data)

#
# def mseb_view(request):
#     customers = Customer.objects.all()
#     if request.method == 'POST':
#         comp_name_id = request.POST.get('Comp_name')
#         field_name, action, customer_id = request.POST.get('field').split('_')
#
#         # Check if the user exists in the database
#         try:
#             customer_mseb = MSEB.objects.get(Cust_id=customer_id)
#         except MSEB.DoesNotExist:
#             # If the customer doesn't exist, create a new one
#             customer_mseb = MSEB(comp_name_id=comp_name_id)
#             customer_mseb.save()
#
#         # Update the corresponding field based on action
#         setattr(customer_mseb, field_name, action == 'ok')
#         setattr(customer_mseb, field_name + '_date', datetime.now())
#         customer_mseb.save()
#
#         return redirect('order_page')
#
#     customers_mseb = MSEB.objects.all()
#     return render(request, 'customer/MSEB.html', {'customers_mseb': customers_mseb, 'customers': customers})

# from django.views.decorators.csrf import csrf_exempt
# def save_field(request):
#     if request.method == "POST" and request.is_ajax():
#         comp_name = request.POST.get("comp_name")
#         # field_name = request.POST.get("field")
#         print(comp_name)
#
#         # customer = Customer.objects.get(Comp_name=comp_name)
#         current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
#         # Get or create the MSEB instance for the given company name
#         mseb_instance, created = MSEB.objects.get_or_create(comp_name=comp_name)
#
#         # Update the MSEB instance with form data
#         field_name = request.POST.get('field')  # Get the name of the field/checkbox
#         field_value = request.POST.get('isChecked') == 'true'  # Get the value of the checked checkbox
#
#         # Set the field value based on the field name
#         setattr(mseb_instance, field_name, field_value)
#         setattr(mseb_instance, f"{field_name}_date", current_time)  # Update corresponding date field
#
#         # Save the MSEB instance
#         mseb_instance.save()
#         return JsonResponse({"status": "success"})
#         # except MSEB.DoesNotExist:
#         #     return JsonResponse({"status": "error", "message": "MSEB instance does not exist"})
#     else:
#         return JsonResponse({"status": "error", "message": "Invalid request"})
#
# import datetime
# # from django.http import JsonResponse
# from .models import MSEB
#
# @csrf_exempt
# def save_field(request):
#     customers = Customer.objects.all()
#     if request.method == 'POST':
#         comp_name_id = request.POST.get('comp_name')
#         field_value = request.POST.get('field')
#         # field_name, action, customer_id = request.POST.get('field').split('_')
#         # Split the field value into its components
#         field_name, action, customer_id = field_value.rsplit('_', 2)
#         # Check if the user exists in the database
#         try:
#             customer_mseb = MSEB.objects.get(Cust_id=customer_id)
#         except MSEB.DoesNotExist:
#             # If the customer doesn't exist, create a new one
#             customer_mseb = MSEB(comp_name_id=comp_name_id)
#             customer_mseb.save()
#
#         # Update the corresponding field based on action
#         setattr(customer_mseb, field_name, action == 'ok')
#         setattr(customer_mseb, field_name + '_date', datetime.now())
#         customer_mseb.save()
#
#         return redirect('order_page')
#
#     customers_mseb = MSEB.objects.all()
#     return render(request, 'customer/MSEB.html', {'customers_mseb': customers_mseb, 'customers': customers})



from django.shortcuts import render
from .forms import CustomerSelectForm
from .models import MSEB

from django.shortcuts import render, get_object_or_404
from .models import MSEB
from .forms import CustomerSelectForm

from django.shortcuts import render, get_object_or_404
from .forms import CustomerSelectForm
from .models import MSEB

#
# def MSEB_tracking_view(request, customer_id):
#     customer = get_object_or_404(Customer, Cust_id=customer_id)
#     mseb_data = MSEB.objects.filter(customer=customer).first()
#     progress_data = None
#
#     if mseb_data:
#         progress_data = {
#             'load_extension': mseb_data.load_extension,
#             'flisibility': mseb_data.flisibility,
#             'quotation': mseb_data.quotation,
#             'sent_to_bill': mseb_data.sent_to_bill,
#             'net_meter': mseb_data.net_meter,
#             'flexibility': mseb_data.flexibility,
#             'approval': mseb_data.approval,
#             'meter_testing': mseb_data.meter_testing,
#             'agreement': mseb_data.agreement,
#             'release': mseb_data.release,
#             'installation_date': mseb_data.installation_date,
#         }
#
#     return render(request, 'customer/MSEB_tracking.html', {'customer': customer, 'progress_data': progress_data})

from django.core.serializers.json import DjangoJSONEncoder
import json


#
# def MSEB_tracking_view(request, customer_id):
#     customer = get_object_or_404(Customer, Cust_id=customer_id)
#     mseb_data = MSEB.objects.filter(customer=customer).first()
#     progress_data = None
#
#     if mseb_data:
#         progress_data = {
#             'load_extension': {'value': mseb_data.load_extension, 'date': mseb_data.load_extension_date},
#             'flisibility': {'value': mseb_data.flisibility, 'date': mseb_data.flisibility_date},
#             'quotation': {'value': mseb_data.quotation, 'date': mseb_data.quotation_date},
#             'sent_to_bill': {'value': mseb_data.sent_to_bill, 'date': mseb_data.sent_to_bill_date},
#             'net_meter': {'value': mseb_data.net_meter, 'date': mseb_data.net_meter_date},
#             'flexibility': {'value': mseb_data.flexibility, 'date': mseb_data.flexibility_date},
#             'approval': {'value': mseb_data.approval, 'date': mseb_data.approval_date},
#             'meter_testing': {'value': mseb_data.meter_testing, 'date': mseb_data.meter_testing_date},
#             'agreement': {'value': mseb_data.agreement, 'date': mseb_data.agreement_date},
#             'release': {'value': mseb_data.release, 'date': mseb_data.release_date},
#             'installation_date': {'value': mseb_data.installation_date, 'date': mseb_data.installation_date_date},
#         }
#
#
#     return render(request, 'customer/MSEB_tracking.html',
#                   {'customer': customer, 'progress_data': progress_data})


def MSEB_tracking_view(request, customer_id):
    customer = get_object_or_404(Customer, Cust_id=customer_id)
    mseb_data = MSEB.objects.filter(customer=customer).first()
    records = MSEB.objects.filter(customer=customer).first()
    progress_data = None
    current_load = int(customer.current_load)  # Parse to integer
    loadsancution = int(customer.loadsancution)  # Parse to integer

    # Check if both values are equal
    if current_load == loadsancution:
        field_mapping = {
            'net_meter': 'Net Metering',
            'flexibility': 'Technical Feasibility',
            'approval': 'Approval',
            'meter_testing': 'Meter Testing',
            'agreement': 'NetMeter Agreement.',
            'release': 'Meter Release',
            'installation_date': 'Meter Installation Date',
        }
    else:
        field_mapping = {
            'load_extension': 'Load Extension',
            'flisibility': 'Off-Line Feasibility',
            'quotation': 'Firm Quotation Gen.',
            'sent_to_bill': 'Sent to Bill',
            'net_meter': 'Net Metering',
            'flexibility': 'Technical Feasibility',
            'approval': 'Approval',
            'meter_testing': 'Meter Testing',
            'agreement': 'NetMeter Agreement.',
            'release': 'Meter Release',
            'installation_date': 'Meter Installation Date',
        }

    # Constructing progress data with display names
    progress_data = {}
    for field, value in mseb_data.__dict__.items():
        if field in field_mapping:
            progress_data[field_mapping[field]] = {
                'value': value,
                'date': getattr(mseb_data, f"{field}_date") if f"{field}_date" in mseb_data.__dict__ else None
            }

    return render(request, 'customer/MSEB_tracking.html', {'customer': customer, 'progress_data': progress_data, 'records': records})
