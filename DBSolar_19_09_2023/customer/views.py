import uuid
from io import BytesIO

from django.contrib.auth.forms import UserCreationForm
from django.db.models.functions import Trim, Lower, Cast
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from detect_barcodes.models import BarcodeImage
from user.models import Profile
from .models import customer_technical_Details, Meter, Meters, GenerationMeter, GenerationCT, InspectionDetail, \
    SolarPump
from django.shortcuts import redirect
from .models import MSEB

from datetime import datetime, timedelta, date
# import datetime
from datetime import datetime
from django.db.models import Q
import re

from django.shortcuts import render
from django.http import JsonResponse
from .models import Customer
# Import Quotation model to mark converted status when creating customer from quotation
from quotation.models import Quotation
#from urllib.parse import quote as urlquote
from django.shortcuts import render, HttpResponse

import user
from dashboard.models import staff_Notification
from user.forms import CreateUserForm, UserUpdateForm
from user.views import profile
from .models import Customer, Role, Department
from django.contrib.auth.models import User, Group
from datetime import datetime
from django.db.models import Q, Max, Count, Sum, DateField
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
from .staff_access import customer_queryset_for_request

@login_required(login_url='user-login')
def cust(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    customer = customer_queryset_for_request(request.user)
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
#
# @login_required(login_url='user-login')
# def Cust_emp(request):
#     Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
#     Cust_type = 'Residential'
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')
#     cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')
#
#     if request.method == 'POST':
#         # Create a new user first
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.email = request.POST['email']  # Add email to user object
#             user.first_name = request.POST['first_name']
#             user.last_name = request.POST['last_name']
#             user.save()
#             # Add the user to the 'Customers' group
#             group = Group.objects.get(name='Customers')
#             user.groups.add(group)
#
#             # Retrieve phase value from POST data
#             phase = int(request.POST.get('phase', 0))  # Default to 0 if not provided
#             Comp_name = request.POST['first_name'] + " " + request.POST['last_name']
#             first_name= request.POST['first_name']
#             middle_name= request.POST['middle_name']
#             last_name= request.POST['last_name']
#             Address= request.POST['Address']
#             Plant_Capacity=int(request.POST['Plant_Capacity'])
#             Ups_Soft= request.POST['Ups_Soft']
#             email= request.POST['email']
#             phone=int(request.POST['phone'])
#             solar_comp= request.POST['solar_comp']
#             UPSC= request.POST['UPSC']
#             state= request.POST['state']
#             Pincode=int(request.POST['Pincode'])
#             po_date = (request.POST['po_date'])
#             po_order = request.POST['po_order']
#             qunt_solar = request.POST['qunt_solar']
#             qunt_inv = request.POST['qunt_inv']
#             Teamid = request.POST['Engineer_Assigned']
#             city_name = request.POST.get('city_name')
#             new_city_name = request.POST.get('new_city_name')
#             advance_paid = request.POST.get('advance_paid')  # Will be 'paid' or 'not_paid'
#
#             Emp_id = request.user
#             sol_warranty = request.POST['sol_warranty']
#             inv_warranty = request.POST['inv_warranty']
#             com_warranty = request.POST['com_warranty']
#             project_type = request.POST['project_type']
#
#             # Initialize fields
#             Consumer = None
#             current_load = None
#             loadsancution = None
#             solar_pump = None
#             pump_qunt = None
#             pump_warranty = None
#
#             if project_type == "Water Pump":
#                 solar_pump = request.POST.get('solar_pump')
#                 pump_qunt = request.POST.get('pump_qunt')
#                 pump_warranty = request.POST.get('pump_warranty')
#             else:
#                 Consumer = request.POST.get('Consumer')
#                 current_load = request.POST.get('Bill_unit')
#                 loadsancution = request.POST.get('loadsancution')
#
#             if city_name == "Other" and new_city_name:
#                 # Check if the new city already exists in the database
#                 existing_city = Customer.objects.filter(City=new_city_name).first()
#                 if not existing_city:
#                     city_name = new_city_name
#                 else:
#                     city_name = new_city_name
#
#             if Teamid:
#                 team1 = User.objects.get(id=Teamid)
#             else:
#                 team1 = 1
#
#             new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load, first_name=first_name, middle_name=middle_name, last_name=last_name,
#                                 Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
#                                 City=city_name, email=email, phone=phone, solar_comp=solar_comp,
#                                 UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user, loadsancution=loadsancution, po_date=po_date, po_order=po_order,
#                                 Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty, inv_warranty=inv_warranty, com_warranty=com_warranty,
#                                 project_type=project_type, solar_pump=solar_pump, pump_qunt=pump_qunt, pump_warranty=pump_warranty,  phase=phase, advance_paid = advance_paid)
#             new_cust.save()
#
#             # After saving Customer, create related Result entry
#             result = Result.objects.create(
#                     consumer=Comp_name,  # Or any other field like customer name
#                     consumer_id=new_cust,  # Link to newly created Customer
#                     AssignTo=Emp_id if isinstance(Emp_id, User) else None  # Assign the engineer if available
#                 )
#             result.save()
#             messages.info(request, 'New Customer enrolled Successfully')
#
#             cust = Customer.objects.all()
#             if Cust_id:
#                 cust = cust.filter(Cust_id=Cust_id)
#                 context = {
#                     'cust': cust,
#                     'count1': count1,
#                     'notification1': notification1,
#                     'engineers': engineers,
#                     'cities': cities,
#                 }
#                 return render(request, 'customer/Cust_emp.html', context)
#             return HttpResponseRedirect("customer/Cust_emp")
#         return HttpResponse("Form is not valid")  # Add this line
#     else:
#         form = UserCreationForm()
#         context = {
#             'form': form,
#             'count1': count1,
#             'notification1': notification1,
#             'engineers': engineers,
#             'cities': cities,
#         }
#         return render(request, 'customer/Cust_emp.html', context)

#
# @login_required(login_url='user-login')
# def Cust_emp(request):
#     # Get quotation data from session if coming from conversion
#     quotation_data = request.session.pop('quotation_data', None) if request.GET.get('from_quotation') else None
#
#     Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
#     Cust_type = 'Residential'
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(
#         is_staff='1').filter(is_active='1')
#     cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')
#
#     # If we have quotation data, pre-fill initial values
#     initial_data = {}
#     if quotation_data:
#         initial_data = {
#             'project_type': quotation_data.get('project_type', ''),
#             'Plant_Capacity': quotation_data.get('plant_capacity', ''),
#             'phase': quotation_data.get('phase', ''),
#             'po_order': quotation_data.get('po_order_no', ''),
#             'po_date': quotation_data.get('po_date', ''),
#             'first_name': quotation_data.get('first_name', ''),
#             'middle_name': quotation_data.get('middle_name', ''),
#             'last_name': quotation_data.get('last_name', ''),
#             'Address': quotation_data.get('address', ''),
#             'state': quotation_data.get('state', ''),
#             'email': quotation_data.get('email', ''),
#             'phone': quotation_data.get('phone', ''),
#             'Consumer': quotation_data.get('consumer_no', ''),
#         }
#
#     if request.method == 'POST':
#         # Create a new user first
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.email = request.POST['email']  # Add email to user object
#             user.first_name = request.POST['first_name']
#             user.last_name = request.POST['last_name']
#             user.save()
#             # Add the user to the 'Customers' group
#             group = Group.objects.get(name='Customers')
#             user.groups.add(group)
#
#             # Retrieve phase value from POST data
#             phase = int(request.POST.get('phase', 0))  # Default to 0 if not provided
#             Comp_name = request.POST['first_name'] + " " + request.POST['last_name']
#             first_name = request.POST['first_name']
#             middle_name = request.POST['middle_name']
#             last_name = request.POST['last_name']
#             Address = request.POST['Address']
#             Plant_Capacity = int(request.POST['Plant_Capacity'])
#             Ups_Soft = request.POST['Ups_Soft']
#             email = request.POST['email']
#             phone = int(request.POST['phone'])
#             solar_comp = request.POST['solar_comp']
#             UPSC = request.POST['UPSC']
#             state = request.POST['state']
#             Pincode = int(request.POST['Pincode'])
#             po_date = (request.POST['po_date'])
#             po_order = request.POST['po_order']
#             qunt_solar = request.POST['qunt_solar']
#             qunt_inv = request.POST['qunt_inv']
#             Teamid = request.POST['Engineer_Assigned']
#             city_name = request.POST.get('city_name')
#             new_city_name = request.POST.get('new_city_name')
#             advance_paid = request.POST.get('advance_paid')  # Will be 'paid' or 'not_paid'
#
#             Emp_id = request.user
#             sol_warranty = request.POST['sol_warranty']
#             inv_warranty = request.POST['inv_warranty']
#             com_warranty = request.POST['com_warranty']
#             project_type = request.POST['project_type']
#
#             # Initialize fields
#             Consumer = None
#             current_load = None
#             loadsancution = None
#             solar_pump = None
#             pump_qunt = None
#             pump_warranty = None
#
#             if project_type == "Water Pump":
#                 solar_pump = request.POST.get('solar_pump')
#                 pump_qunt = request.POST.get('pump_qunt')
#                 pump_warranty = request.POST.get('pump_warranty')
#             else:
#                 Consumer = request.POST.get('Consumer')
#                 current_load = request.POST.get('Bill_unit')
#                 loadsancution = request.POST.get('loadsancution')
#
#             if city_name == "Other" and new_city_name:
#                 # Check if the new city already exists in the database
#                 existing_city = Customer.objects.filter(City=new_city_name).first()
#                 if not existing_city:
#                     city_name = new_city_name
#                 else:
#                     city_name = new_city_name
#
#             if Teamid:
#                 team1 = User.objects.get(id=Teamid)
#             else:
#                 team1 = 1
#
#             new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load,
#                                 first_name=first_name, middle_name=middle_name, last_name=last_name,
#                                 Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
#                                 City=city_name, email=email, phone=phone, solar_comp=solar_comp,
#                                 UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user,
#                                 loadsancution=loadsancution, po_date=po_date, po_order=po_order,
#                                 Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty,
#                                 inv_warranty=inv_warranty, com_warranty=com_warranty,
#                                 project_type=project_type, solar_pump=solar_pump, pump_qunt=pump_qunt,
#                                 pump_warranty=pump_warranty, phase=phase, advance_paid=advance_paid)
#             new_cust.save()
#
#             # After saving Customer, create related Result entry
#             result = Result.objects.create(
#                 consumer=Comp_name,  # Or any other field like customer name
#                 consumer_id=new_cust,  # Link to newly created Customer
#                 AssignTo=Emp_id if isinstance(Emp_id, User) else None  # Assign the engineer if available
#             )
#             result.save()
#             messages.info(request, 'New Customer enrolled Successfully')
#
#             cust = Customer.objects.all()
#             if Cust_id:
#                 cust = cust.filter(Cust_id=Cust_id)
#                 context = {
#                     'cust': cust,
#                     'count1': count1,
#                     'notification1': notification1,
#                     'engineers': engineers,
#                     'cities': cities,
#                 }
#                 return render(request, 'customer/Cust_emp.html', context)
#             return HttpResponseRedirect("customer/Cust_emp")
#         return HttpResponse("Form is not valid")  # Add this line
#     else:
#         form = UserCreationForm()
#         context = {
#             'form': form,
#             'count1': count1,
#             'notification1': notification1,
#             'engineers': engineers,
#             'cities': cities,
#             'quotation_data': quotation_data,  # Add to context
#             # Add initial data to context for template
#             **initial_data
#         }
#         return render(request, 'customer/Cust_emp.html', context)
#
# @login_required(login_url='user-login')
# def Cust_emp(request):
#         # Check if coming from quotation conversion
#         from_quotation = request.GET.get('from_quotation', False)
#         quotation_data = None
#
#         if from_quotation:
#             # Get quotation data from session
#             session_data = request.session.get('quotation_data')
#             if session_data:
#                 # Check if data is recent (within last 5 minutes)
#                 import time
#                 timestamp = session_data.get('timestamp', 0)
#                 current_time = time.time()
#
#                 if current_time - timestamp < 300:  # 5 minutes
#                     quotation_data = session_data.get('data', {})
#                     # Clear the session data after retrieving it
#                     if 'quotation_data' in request.session:
#                         del request.session['quotation_data']
#                         request.session.modified = True
#                 else:
#                     # Data is too old
#                     if 'quotation_data' in request.session:
#                         del request.session['quotation_data']
#                         request.session.modified = True
#
#         Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
#         Cust_type = 'Residential'
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#         engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(
#             is_staff='1').filter(is_active='1')
#         cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')
#
#         # Debug: Print quotation data
#         print(f"From quotation: {from_quotation}")
#         print(f"Quotation data: {quotation_data}")
#
#         # Initialize context with default values
#         context = {
#             'count1': count1,
#             'notification1': notification1,
#             'engineers': engineers,
#             'cities': cities,
#             'from_quotation': from_quotation,
#         }
#
#         # If we have quotation data, add it to context
#         if quotation_data:
#             # Handle plant capacity - ensure it's a number
#             plant_capacity = quotation_data.get('plant_capacity', '')
#             if plant_capacity:
#                 try:
#                     plant_capacity = float(plant_capacity)
#                 except (ValueError, TypeError):
#                     plant_capacity = ''
#
#             # Handle phase conversion
#             phase = quotation_data.get('phase', '')
#             if phase == 'Single Phase':
#                 phase = 1
#             elif phase == 'Three Phase':
#                 phase = 3
#             elif phase == '0' or phase == 'Not Applicable':
#                 phase = 0
#             else:
#                 phase = ''
#
#             context.update({
#                 'consumer_type': quotation_data.get('consumer_type', ''),
#                 'project_type': quotation_data.get('project_type', ''),
#                 'Plant_Capacity': plant_capacity,
#                 'phase': phase,
#                 'po_order': quotation_data.get('po_order_no', ''),
#                 'po_date': quotation_data.get('po_date', ''),
#                 'first_name': quotation_data.get('first_name', ''),
#                 'middle_name': quotation_data.get('middle_name', ''),
#                 'last_name': quotation_data.get('last_name', ''),
#                 'Address': quotation_data.get('address', ''),
#                 'state': quotation_data.get('state', ''),
#                 'email': quotation_data.get('email', ''),
#                 'phone': quotation_data.get('phone', ''),
#                 'Consumer': quotation_data.get('consumer_no', ''),
#                 'city_name': quotation_data.get('city', ''),
#             })
#
#             # Debug: Print what we're passing to template
#             print(f"Context data being passed: {context.get('first_name')} {context.get('last_name')}")
#             print(f"Plant Capacity: {context.get('Plant_Capacity')}")
#             print(f"Address: {context.get('Address')}")
#
#         if request.method == 'POST':
#             # ... your existing POST handling code remains the same ...
#             form = UserCreationForm(request.POST)
#             if form.is_valid():
#                 user = form.save(commit=False)
#             user.email = request.POST['email']  # Add email to user object
#             user.first_name = request.POST['first_name']
#             user.last_name = request.POST['last_name']
#             user.save()
#             # Add the user to the 'Customers' group
#             group = Group.objects.get(name='Customers')
#             user.groups.add(group)
#
#             # Retrieve phase value from POST data
#             phase = int(request.POST.get('phase', 0))  # Default to 0 if not provided
#             Comp_name = request.POST['first_name'] + " " + request.POST['last_name']
#             first_name = request.POST['first_name']
#             middle_name = request.POST['middle_name']
#             last_name = request.POST['last_name']
#             Address = request.POST['Address']
#             Plant_Capacity = int(request.POST['Plant_Capacity'])
#             Ups_Soft = request.POST['Ups_Soft']
#             email = request.POST['email']
#             phone = int(request.POST['phone'])
#             solar_comp = request.POST['solar_comp']
#             UPSC = request.POST['UPSC']
#             state = request.POST['state']
#             Pincode = int(request.POST['Pincode'])
#             po_date = (request.POST['po_date'])
#             po_order = request.POST['po_order']
#             qunt_solar = request.POST['qunt_solar']
#             qunt_inv = request.POST['qunt_inv']
#             Teamid = request.POST['Engineer_Assigned']
#             city_name = request.POST.get('city_name')
#             new_city_name = request.POST.get('new_city_name')
#             advance_paid = request.POST.get('advance_paid')  # Will be 'paid' or 'not_paid'
#
#             Emp_id = request.user
#             sol_warranty = request.POST['sol_warranty']
#             inv_warranty = request.POST['inv_warranty']
#             com_warranty = request.POST['com_warranty']
#             project_type = request.POST['project_type']
#
#             # Initialize fields
#             Consumer = None
#             current_load = None
#             loadsancution = None
#             solar_pump = None
#             pump_qunt = None
#             pump_warranty = None
#
#             if project_type == "Water Pump":
#                 solar_pump = request.POST.get('solar_pump')
#                 pump_qunt = request.POST.get('pump_qunt')
#                 pump_warranty = request.POST.get('pump_warranty')
#             else:
#                 Consumer = request.POST.get('Consumer')
#                 current_load = request.POST.get('Bill_unit')
#                 loadsancution = request.POST.get('loadsancution')
#
#             if city_name == "Other" and new_city_name:
#                 # Check if the new city already exists in the database
#                 existing_city = Customer.objects.filter(City=new_city_name).first()
#                 if not existing_city:
#                     city_name = new_city_name
#                 else:
#                     city_name = new_city_name
#
#             if Teamid:
#                 team1 = User.objects.get(id=Teamid)
#             else:
#                 team1 = 1
#
#             new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load,
#                                 first_name=first_name, middle_name=middle_name, last_name=last_name,
#                                 Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
#                                 City=city_name, email=email, phone=phone, solar_comp=solar_comp,
#                                 UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user,
#                                 loadsancution=loadsancution, po_date=po_date, po_order=po_order,
#                                 Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty,
#                                 inv_warranty=inv_warranty, com_warranty=com_warranty,
#                                 project_type=project_type, solar_pump=solar_pump, pump_qunt=pump_qunt,
#                                 pump_warranty=pump_warranty, phase=phase, advance_paid=advance_paid)
#             new_cust.save()
#
#             # After saving Customer, create related Result entry
#             result = Result.objects.create(
#                 consumer=Comp_name,  # Or any other field like customer name
#                 consumer_id=new_cust,  # Link to newly created Customer
#                 AssignTo=Emp_id if isinstance(Emp_id, User) else None  # Assign the engineer if available
#             )
#             result.save()
#             messages.info(request, 'New Customer enrolled Successfully')
#
#             cust = Customer.objects.all()
#             if Cust_id:
#                 cust = cust.filter(Cust_id=Cust_id)
#                 context = {
#                     'cust': cust,
#                     'count1': count1,
#                     'notification1': notification1,
#                     'engineers': engineers,
#                     'cities': cities,
#                 }
#                 return render(request, 'customer/Cust_emp.html', context)
#             return HttpResponseRedirect("customer/Cust_emp")
#             return HttpResponse("Form is not valid")  # Add this line
#         else:
#          form = UserCreationForm()
#          context['form'] = form
#          return render(request, 'customer/Cust_emp.html', context)


@login_required(login_url='user-login')
def Cust_emp(request):
    # Check if coming from quotation conversion
    from_quotation = request.GET.get('from_quotation', False)

    # Debug: Print all GET parameters
    print(f"DEBUG Cust_emp - from_quotation: {from_quotation}")
    if from_quotation:
        print("DEBUG Cust_emp - All GET parameters:")
        for key, value in request.GET.items():
            print(f"  {key}: {value}")

    Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
    Cust_type = 'Residential'
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(
        is_staff='1').filter(is_active='1')
    associates = User.objects.filter(profile__department__isnull=False).filter(profile__department='Associate').filter(
        is_staff='1').filter(is_active='1')
    cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')

    # Initialize context with default values
    context = {
        'count1': count1,
        'notification1': notification1,
        'engineers': engineers,
        'associates': associates,
        'cities': cities,
        'from_quotation': from_quotation,
    }

    # If coming from quotation, get data from URL parameters (NOT session)
    if from_quotation:
        # Extract and process data from GET parameters
        consumer_type = request.GET.get('consumer_type', '')
        project_type = request.GET.get('project_type', '')

        # Handle plant capacity - safely convert to float
        plant_capacity = request.GET.get('plant_capacity', '')
        if plant_capacity:
            try:
                plant_capacity = float(plant_capacity)
            except (ValueError, TypeError):
                plant_capacity = ''

        # Handle phase conversion
        phase = request.GET.get('phase', '')
        if '1 Phase' in str(phase) or str(phase) == '1' or 'Single Phase' in str(phase):
            phase = 1
        elif '3 Phase' in str(phase) or str(phase) == '3' or 'Three Phase' in str(phase):
            phase = 3
        elif str(phase) == '0' or 'Not Applicable' in str(phase):
            phase = 0
        else:
            try:
                phase = int(phase)
            except (ValueError, TypeError):
                phase = ''

        # Get names directly from GET parameters
        first_name = request.GET.get('first_name', '')
        middle_name = request.GET.get('middle_name', '')
        last_name = request.GET.get('last_name', '')

        # If names are empty but we have consumer_full_name, try to extract
        if not first_name and request.GET.get('consumer_full_name'):
            full_name = request.GET.get('consumer_full_name', '')
            name_parts = full_name.split()
            if len(name_parts) >= 1:
                first_name = name_parts[0]
                if len(name_parts) >= 2:
                    last_name = name_parts[-1]
                if len(name_parts) > 2:
                    middle_name = ' '.join(name_parts[1:-1])

        # Get city - check multiple possible parameter names
        city = request.GET.get('city', '')
        if not city:
            city = request.GET.get('consumer_address2', '')

        # Get consumer number
        consumer_no = request.GET.get('consumer_no', '')

        # Get PO details
        po_order_no = request.GET.get('po_order_no', '')
        po_date = request.GET.get('po_date', '')

        # Get other details
        address = request.GET.get('address', '')
        state = request.GET.get('state', '')
        email = request.GET.get('email', '')
        phone = request.GET.get('phone', '')

        # Update context with ALL values
        context.update({
            'consumer_type': consumer_type,
            'project_type': project_type,
            'Plant_Capacity': plant_capacity,
            'phase': phase,
            'po_order': po_order_no,
            'po_date': po_date,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'Address': address,
            'city_name': city,  # Note: template uses city_name
            'state': state,
            'email': email,
            'phone': phone,
            'Consumer': consumer_no,
        })

        # Debug: Print what we're setting in context
        print(f"DEBUG Cust_emp - Context data being set:")
        for key in ['consumer_type', 'project_type', 'Plant_Capacity', 'phase', 'po_order',
                    'po_date', 'first_name', 'middle_name', 'last_name', 'Address',
                    'city_name', 'state', 'email', 'phone', 'Consumer']:
            print(f"  {key}: {context.get(key, 'Not set')}")

    if request.method == 'POST':
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

            # Retrieve phase value from POST data
            phase = int(request.POST.get('phase', 0))  # Default to 0 if not provided
            Comp_name = request.POST['first_name'] + " " + request.POST['last_name']
            first_name = request.POST['first_name']
            middle_name = request.POST['middle_name']
            last_name = request.POST['last_name']
            Address = request.POST['Address']
            Plant_Capacity = int(request.POST['Plant_Capacity'])
            Ups_Soft = request.POST['Ups_Soft']
            email = request.POST['email']
            phone = int(request.POST['phone'])
            solar_comp = request.POST['solar_comp']
            UPSC = request.POST['UPSC']
            state = request.POST['state']
            Pincode = int(request.POST['Pincode'])
            # po_date = (request.POST['po_date'])
            # Date
            po_date_str = request.POST.get('po_date')
            po_date = datetime.strptime(po_date_str, "%Y-%m-%d").date() if po_date_str else None

            po_order = request.POST['po_order']
            qunt_solar = request.POST['qunt_solar']
            qunt_inv = request.POST['qunt_inv']
            Teamid = request.POST['Engineer_Assigned']
            AssocId = request.POST.get('Associate_Assigned')
            city_name = request.POST.get('city_name')
            new_city_name = request.POST.get('new_city_name')
            advance_paid = request.POST.get('advance_paid')  # Will be 'paid' or 'not_paid'

            Emp_id = request.user
            sol_warranty = request.POST['sol_warranty']
            inv_warranty = request.POST['inv_warranty']
            com_warranty = request.POST['com_warranty']
            project_type = request.POST['project_type']

            # Initialize fields
            Consumer = None
            current_load = None
            loadsancution = None
            solar_pump = None
            pump_qunt = None
            pump_warranty = None

            if project_type == "Water Pump":
                solar_pump = request.POST.get('solar_pump')
                pump_qunt = request.POST.get('pump_qunt')
                pump_warranty = request.POST.get('pump_warranty')
            else:
                Consumer = request.POST.get('Consumer')
                current_load = request.POST.get('Bill_unit')
                loadsancution = request.POST.get('loadsancution')

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

            assoc_user = User.objects.get(id=AssocId) if AssocId else None

            new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load,
                                first_name=first_name, middle_name=middle_name, last_name=last_name,
                                Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
                                City=city_name, email=email, phone=phone, solar_comp=solar_comp,
                                UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user,
                                loadsancution=loadsancution, po_date=po_date, po_order=po_order,
                                Engg_Assign=team1, Assoc_Assign=assoc_user, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty,
                                inv_warranty=inv_warranty, com_warranty=com_warranty,
                                project_type=project_type, solar_pump=solar_pump, pump_qunt=pump_qunt,
                                pump_warranty=pump_warranty, phase=phase, advance_paid=advance_paid)
            new_cust.save()

            # If this customer was created from a quotation conversion, mark the quotation converted
            quotation_id = request.GET.get('quotation_id') or request.POST.get('quotation_id') or \
                           (request.session.get('quotation_data', {}) or {}).get('quotation_id')
            if quotation_id:
                try:
                    Quotation.objects.filter(pk=quotation_id).update(convert_consumer=True)
                except Exception as e:
                    print(f"Failed to mark quotation {quotation_id} as converted: {e}")

            # # If this customer was created from a quotation conversion, mark the quotation converted
            # quotation_id = request.GET.get('quotation_id') or request.POST.get('quotation_id') or \
            #                (request.session.get('quotation_data', {}) or {}).get('quotation_id')
            # if quotation_id:
            #     try:
            #         Quotation.objects.filter(pk=quotation_id).update(convert_consumer=True)
            #     except Exception as e:
            #         print(f"Failed to mark quotation {quotation_id} as converted: {e}")

            # After saving Customer, create related Result entry
            result = Result.objects.create(
                consumer=Comp_name,  # Or any other field like customer name
                consumer_id=new_cust,  # Link to newly created Customer
                AssignTo=Emp_id if isinstance(Emp_id, User) else None  # Assign the engineer if available
            )
            result.save()
            messages.info(request, 'New Customer enrolled Successfully')

            cust = customer_queryset_for_request(request.user)
            if Cust_id:
                cust = cust.filter(Cust_id=Cust_id)
                context = {
                    'cust': cust,
                    'count1': count1,
                    'notification1': notification1,
                    'engineers': engineers,
                    'associates': associates,
                    'cities': cities,
                }
                return render(request, 'customer/Cust_emp.html', context)
            return HttpResponseRedirect("customer/Cust_emp")
        else:
            context['form'] = form
            return render(request, 'customer/Cust_emp.html', context)
    else:
        form = UserCreationForm()
        context['form'] = form
        return render(request, 'customer/Cust_emp.html', context)
#
# @login_required(login_url='user-login')
# def Comm_Cust(request):
#     Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#     engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')
#     cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')
#
#     Cust_type = 'Commersial'
#     if request.method == 'POST':
#         # Create a new user first
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.email = request.POST['email']  # Add email to user object
#             user.first_name = request.POST['first_name']
#             user.last_name = request.POST['last_name']
#
#             user.save()
#             # Add the user to the 'Customers' group
#             group = Group.objects.get(name='Customers')
#             user.groups.add(group)
#
#             # Retrieve phase value from POST data
#             phase = int(request.POST.get('phase', 0))  # Default to 0 if not provided
#
#             # Create a new customer first
#             Comp_name = request.POST['Comp_name']
#
#             first_name = request.POST['first_name']
#             middle_name = request.POST['middle_name']
#             last_name = request.POST['last_name']
#             Address = request.POST['Address']
#             Plant_Capacity = int(request.POST['Plant_Capacity'])
#             Ups_Soft = request.POST['Ups_Soft']
#             phone = int(request.POST['phone'])
#             solar_comp = request.POST['solar_comp']
#             UPSC = request.POST['UPSC']
#             state = request.POST['state']
#             Pincode = int(request.POST['Pincode'])
#
#             po_date = (request.POST['po_date'])
#             po_order = request.POST['po_order']
#             qunt_solar = request.POST['qunt_solar']
#             qunt_inv = request.POST['qunt_inv']
#             Teamid = request.POST['Engineer_Assigned']
#             city_name = request.POST.get('city_name')
#             new_city_name = request.POST.get('new_city_name')
#             advance_paid = request.POST.get('advance_paid')  # Will be 'paid' or 'not_paid'
#
#             Emp_id = request.user
#
#             sol_warranty = request.POST['sol_warranty']
#             inv_warranty = request.POST['inv_warranty']
#             com_warranty = request.POST['com_warranty']
#             project_type = request.POST['project_type']
#
#             # Initialize fields
#             Consumer = None
#             current_load = None
#             loadsancution = None
#             solar_pump = None
#             pump_qunt = None
#             pump_warranty = None
#
#             if project_type == "Water Pump":
#                 solar_pump = request.POST.get('solar_pump')
#                 pump_qunt = request.POST.get('pump_qunt')
#                 pump_warranty = request.POST.get('pump_warranty')
#             else:
#                 Consumer = request.POST.get('Consumer')
#                 current_load = request.POST.get('Bill_unit')
#                 loadsancution = request.POST.get('loadsancution')
#
#             if city_name == "Other" and new_city_name:
#                 # Check if the new city already exists in the database
#                 existing_city = Customer.objects.filter(City=new_city_name).first()
#                 if not existing_city:
#                     city_name = new_city_name
#                 else:
#                     city_name = new_city_name
#
#             if Teamid:
#                 team1 = User.objects.get(id=Teamid)
#             else:
#                 team1 = 1
#
#             new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load, first_name=first_name,
#                                 middle_name=middle_name, last_name=last_name, Address=Address, Plant_Capacity=Plant_Capacity,
#                                 Ups_Soft=Ups_Soft, Cust_type=Cust_type, City=city_name, email=user.email, phone=phone,
#                                 solar_comp=solar_comp, UPSC=UPSC, Emp_id=Emp_id, state=state,
#                                 Pincode=Pincode, new_customer=user, loadsancution=loadsancution, po_order=po_order, po_date=po_date,
#                                 Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty, inv_warranty=inv_warranty, com_warranty=com_warranty,
#                                 project_type=project_type, solar_pump=solar_pump, pump_qunt=pump_qunt, pump_warranty=pump_warranty,  phase=phase, advance_paid = advance_paid)
#             new_cust.save()
#
#             # After saving Customer, create related Result entry
#             result = Result.objects.create(
#                 consumer=Comp_name,  # Or any other field like customer name
#                 consumer_id=new_cust,  # Link to newly created Customer
#                 AssignTo=Emp_id if isinstance(Emp_id, User) else None  # Assign the engineer if available
#             )
#             result.save()
#
#             error = "no"
#             messages.info(request, 'New Customer enrolled Successfully')
#             cust = Customer.objects.all()
#             if Cust_id:
#                 cust = cust.filter(Cust_id=Cust_id)
#                 context = {
#                     'cust': cust,
#                     'count1': count1,
#                     'notification1': notification1,
#                     'engineers': engineers,
#                     'cities': cities,
#                 }
#                 return render(request, 'customer/Comm_Cust.html', context)
#             return HttpResponse("Form is not valid")  # Add this line
#
#     else:
#         form = UserCreationForm()
#         context = {
#             'form': form,
#             'count1': count1,
#             'notification1': notification1,
#             'engineers': engineers,
#             'cities': cities,
#             # 'project_type': project_type,
#         }
#         return render(request, 'customer/Comm_Cust.html', context)


@login_required(login_url='user-login')
def Comm_Cust(request):
    Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(
        is_staff='1').filter(is_active='1')
    associates = User.objects.filter(profile__department__isnull=False).filter(profile__department='Associate').filter(
        is_staff='1').filter(is_active='1')
    cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')

    Cust_type = 'Commersial'

    # Debug: Print all GET parameters if coming from quotation
    from_quotation = request.GET.get('from_quotation', False)
    if from_quotation:
        print(f"DEBUG Comm_Cust - GET parameters: {dict(request.GET)}")

    # Initialize context
    context = {
        'count1': count1,
        'notification1': notification1,
        'engineers': engineers,
        'associates': associates,
        'cities': cities,
        'Cust_type': Cust_type,
        'from_quotation': from_quotation,
    }

    # If coming from quotation, get data from URL parameters
    if from_quotation:
        # Handle plant capacity - safely convert to float
        plant_capacity = request.GET.get('plant_capacity', '')
        if plant_capacity:
            try:
                plant_capacity = float(plant_capacity)
            except (ValueError, TypeError):
                plant_capacity = ''

        # Handle phase conversion
        phase = request.GET.get('phase', '')
        if '1 Phase' in str(phase) or str(phase) == '1' or 'Single Phase' in str(phase):
            phase = 1
        elif '3 Phase' in str(phase) or str(phase) == '3' or 'Three Phase' in str(phase):
            phase = 3
        elif str(phase) == '0' or 'Not Applicable' in str(phase):
            phase = 0
        else:
            try:
                phase = int(phase)
            except (ValueError, TypeError):
                phase = ''

        # Get consumer full name for company/farm name
        consumer_full_name = request.GET.get('consumer_full_name', '')
        comp_name = request.GET.get('comp_name', consumer_full_name)

        # Get city
        city = request.GET.get('city', '')

        context.update({
            'project_type': request.GET.get('project_type', ''),
            'Plant_Capacity': plant_capacity,
            'phase': phase,
            'po_order': request.GET.get('po_order_no', ''),
            'po_date': request.GET.get('po_date', ''),
            'Comp_name': comp_name,
            'first_name': request.GET.get('first_name', ''),
            'middle_name': request.GET.get('middle_name', ''),
            'last_name': request.GET.get('last_name', ''),
            'Address': request.GET.get('address', ''),
            'city_name': city,
            'state': request.GET.get('state', ''),
            'email': request.GET.get('email', ''),
            'phone': request.GET.get('phone', ''),
            'Consumer': request.GET.get('consumer_no', ''),
        })

    if request.method == 'POST':
        print(f"DEBUG Comm_Cust - POST data received")

        # Create a new user first
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.email = request.POST['email']
                user.first_name = request.POST['first_name']
                user.last_name = request.POST['last_name']
                user.save()

                # Add the user to the 'Customers' group
                group = Group.objects.get(name='Customers')
                user.groups.add(group)

                # SAFELY retrieve phase value from POST data
                phase = 0
                try:
                    phase = int(request.POST.get('phase', 0))
                except (ValueError, TypeError):
                    phase = 0

                # Create a new customer
                Comp_name = request.POST['Comp_name']
                first_name = request.POST['first_name']
                middle_name = request.POST['middle_name']
                last_name = request.POST['last_name']
                Address = request.POST['Address']

                # SAFELY convert Plant_Capacity to int
                Plant_Capacity = 0
                try:
                    Plant_Capacity = int(request.POST['Plant_Capacity'])
                except (ValueError, TypeError):
                    # Try float first, then convert to int
                    try:
                        Plant_Capacity = int(float(request.POST['Plant_Capacity']))
                    except:
                        Plant_Capacity = 0

                Ups_Soft = request.POST['Ups_Soft']

                # SAFELY convert phone to int
                phone = 0
                try:
                    phone = int(request.POST['phone'])
                except (ValueError, TypeError):
                    phone = 0

                solar_comp = request.POST['solar_comp']
                UPSC = request.POST['UPSC']
                state = request.POST['state']

                # SAFELY convert Pincode to int
                Pincode = 0
                try:
                    Pincode = int(request.POST['Pincode'])
                except (ValueError, TypeError):
                    Pincode = 0

                po_date = request.POST['po_date']
                po_order = request.POST['po_order']

                # SAFELY convert quantities
                qunt_solar = 0
                try:
                    qunt_solar = int(request.POST['qunt_solar'])
                except (ValueError, TypeError):
                    qunt_solar = 0

                qunt_inv = 0
                try:
                    qunt_inv = int(request.POST['qunt_inv'])
                except (ValueError, TypeError):
                    qunt_inv = 0

                Teamid = request.POST['Engineer_Assigned']
                AssocId = request.POST.get('Associate_Assigned')
                city_name = request.POST.get('city_name')
                new_city_name = request.POST.get('new_city_name')
                advance_paid = request.POST.get('advance_paid')
                Emp_id = request.user

                # SAFELY convert warranty fields
                sol_warranty = 0
                try:
                    sol_warranty = int(request.POST['sol_warranty'])
                except (ValueError, TypeError):
                    sol_warranty = 0

                inv_warranty = 0
                try:
                    inv_warranty = int(request.POST['inv_warranty'])
                except (ValueError, TypeError):
                    inv_warranty = 0

                com_warranty = 0
                try:
                    com_warranty = int(request.POST['com_warranty'])
                except (ValueError, TypeError):
                    com_warranty = 0

                project_type = request.POST['project_type']

                # Initialize fields
                Consumer = None
                current_load = None
                loadsancution = None
                solar_pump = None
                pump_qunt = None
                pump_warranty = None

                if project_type == "Water Pump":
                    solar_pump = request.POST.get('solar_pump')
                    pump_qunt = request.POST.get('pump_qunt')
                    pump_warranty = request.POST.get('pump_warranty')
                else:
                    Consumer = request.POST.get('Consumer')
                    current_load = request.POST.get('Bill_unit')
                    loadsancution = request.POST.get('loadsancution')

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

                assoc_user = User.objects.get(id=AssocId) if AssocId else None

                # Create the customer record
                new_cust = Customer(
                    Cust_id=Cust_id,
                    Comp_name=Comp_name,
                    Consumer=Consumer,
                    current_load=current_load,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    Address=Address,
                    Plant_Capacity=Plant_Capacity,
                    Ups_Soft=Ups_Soft,
                    Cust_type=Cust_type,
                    City=city_name,
                    email=user.email,
                    phone=phone,
                    solar_comp=solar_comp,
                    UPSC=UPSC,
                    Emp_id=Emp_id,
                    state=state,
                    Pincode=Pincode,
                    new_customer=user,
                    loadsancution=loadsancution,
                    po_order=po_order,
                    po_date=po_date,
                    Engg_Assign=team1,
                    Assoc_Assign=assoc_user,
                    qunt_solar=qunt_solar,
                    qunt_inv=qunt_inv,
                    sol_warranty=sol_warranty,
                    inv_warranty=inv_warranty,
                    com_warranty=com_warranty,
                    project_type=project_type,
                    solar_pump=solar_pump,
                    pump_qunt=pump_qunt,
                    pump_warranty=pump_warranty,
                    phase=phase,
                    advance_paid=advance_paid
                )
                new_cust.save()

                # If this customer was created from a quotation conversion, mark the quotation converted
                quotation_id = request.GET.get('quotation_id') or request.POST.get('quotation_id') or \
                               (request.session.get('quotation_data', {}) or {}).get('quotation_id')
                if quotation_id:
                    try:
                        Quotation.objects.filter(pk=quotation_id).update(convert_consumer=True)
                    except Exception as e:
                        print(f"Failed to mark quotation {quotation_id} as converted: {e}")

                # After saving Customer, create related Result entry
                result = Result.objects.create(
                    consumer=Comp_name,
                    consumer_id=new_cust,
                    AssignTo=Emp_id if isinstance(Emp_id, User) else None
                )
                result.save()

                messages.info(request, 'New Customer enrolled Successfully')
                cust = customer_queryset_for_request(request.user)
                if Cust_id:
                    cust = cust.filter(Cust_id=Cust_id)
                    context = {
                        'cust': cust,
                        'count1': count1,
                        'notification1': notification1,
                        'engineers': engineers,
                        'associates': associates,
                        'cities': cities,
                    }
                    return render(request, 'customer/Comm_Cust.html', context)

            except Exception as e:
                print(f"DEBUG Comm_Cust - Error saving form: {str(e)}")
                print(f"DEBUG Comm_Cust - Error type: {type(e)}")
                import traceback
                print(f"DEBUG Comm_Cust - Traceback: {traceback.format_exc()}")
                messages.error(request, f'Error saving customer: {str(e)}')
                return render(request, 'customer/Comm_Cust.html', context)

        else:
            print(f"DEBUG Comm_Cust - Form errors: {form.errors}")
            messages.error(request, 'Form is not valid. Please check your inputs.')
            return render(request, 'customer/Comm_Cust.html', context)

    else:
        form = UserCreationForm()
        context['form'] = form
        return render(request, 'customer/Comm_Cust.html', context)


def check_company_name(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        company_name = data.get('comp_name')
        exists = Customer.objects.filter(Comp_name__iexact=company_name).exists()
        return JsonResponse({'exists': exists})

def check_username(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        exists = User.objects.filter(username__iexact=username).exists()
        return JsonResponse({'exists': exists})

#
# @login_required(login_url='user-login')
# def Comp_Cust(request):
#     Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     Cust_type = 'Industrial'
#     engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')
#     cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')
#
#     if request.method == 'POST':
#         # Create a new user first
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.email = request.POST['email']  # Add email to user object
#             user.save()
#             # Add the user to the 'Customers' group
#             group = Group.objects.get(name='Customers')
#             user.groups.add(group)
#
#             # Retrieve phase value from POST data
#             phase = int(request.POST.get('phase', 0))  # Default to 0 if not provided
#
#             #Cust_id = int(request.POST['Cust_id'])
#             Comp_name = request.POST['Comp_name']
#             Address= request.POST['Address']
#             Plant_Capacity=int(request.POST['Plant_Capacity'])
#             Ups_Soft= request.POST['Ups_Soft']
#             email= request.POST['email']
#             phone=int(request.POST['phone'])
#             solar_comp= request.POST['solar_comp']
#             UPSC= request.POST['UPSC']
#             state= request.POST['state']
#             Pincode=int(request.POST['Pincode'])
#             po_date = (request.POST['po_date'])
#             po_order = request.POST['po_order']
#             qunt_solar = request.POST['qunt_solar']
#             qunt_inv = request.POST['qunt_inv']
#             Teamid = request.POST['Engineer_Assigned']
#             city_name = request.POST.get('city_name')
#             new_city_name = request.POST.get('new_city_name')
#             advance_paid = request.POST.get('advance_paid')  # Will be 'paid' or 'not_paid'
#
#             Emp_id = request.user
#
#             sol_warranty = request.POST['sol_warranty']
#             inv_warranty = request.POST['inv_warranty']
#             com_warranty = request.POST['com_warranty']
#             project_type = request.POST['project_type']
#
#
#             # Initialize fields
#             Consumer = None
#             current_load = None
#             loadsancution = None
#             solar_pump = None
#             pump_qunt = None
#             pump_warranty = None
#
#             if project_type == "Water Pump":
#                 solar_pump = request.POST.get('solar_pump')
#                 pump_qunt = request.POST.get('pump_qunt')
#                 pump_warranty = request.POST.get('pump_warranty')
#             else:
#                 Consumer = request.POST.get('Consumer')
#                 current_load = request.POST.get('Bill_unit')
#                 loadsancution = request.POST.get('loadsancution')
#
#             if city_name == "Other" and new_city_name:
#                 # Check if the new city already exists in the database
#                 existing_city = Customer.objects.filter(City=new_city_name).first()
#                 if not existing_city:
#                  city_name = new_city_name
#                 else:
#                   city_name = new_city_name
#
#             if Teamid:
#                 team1 = User.objects.get(id=Teamid)
#             else:
#                 team1 = 1
#
#             new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load,
#                                 Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
#                                 City=city_name, email=email, phone=phone, solar_comp=solar_comp,
#                                 UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user, loadsancution=loadsancution, po_date=po_date, po_order=po_order,
#                                 Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty, inv_warranty=inv_warranty, com_warranty=com_warranty,
#                                 project_type=project_type, solar_pump=solar_pump, pump_qunt=pump_qunt, pump_warranty=pump_warranty, phase=phase, advance_paid = advance_paid)
#             new_cust.save()
#
#             # After saving Customer, create related Result entry
#             result = Result.objects.create(
#                 consumer=Comp_name,  # Or any other field like customer name
#                 consumer_id=new_cust,  # Link to newly created Customer
#                 AssignTo=Emp_id if isinstance(Emp_id, User) else None  # Assign the engineer if available
#             )
#             result.save()
#
#             messages.info(request, 'New Customer enrolled Successfully')
#             cust = Customer.objects.all()
#             if Cust_id:
#                 cust = cust.filter(Cust_id=Cust_id)
#                 context = {
#                     'count1': count1,
#                     'cust': cust,
#                     'notification1': notification1,
#                     'engineers': engineers,
#                     'cities': cities,
#                 }
#                 return render(request, 'customer/Comp_Cust.html', context)
#             return HttpResponse("Form is not valid")  # Add this line
#     else:
#         form = UserCreationForm()
#         context = {
#              'form': form,
#              'count1': count1,
#              'notification1': notification1,
#              'engineers': engineers,
#              'cities': cities,
#         }
#         return render(request, 'customer/Comp_Cust.html', context)


# from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Max

from .models import Customer, Result
from .forms import UserCreationForm
# from notification.models import staff_Notification

#
# @login_required(login_url='user-login')
# def Comp_Cust(request):
#
#     count1 = staff_Notification.objects.filter(
#         staff_id=request.user.id, status=False
#     ).count()
#
#     notification1 = staff_Notification.objects.filter(
#         staff_id=request.user.id, status=False
#     ).order_by('-created_at')
#
#     Cust_type = 'Industrial'
#
#     engineers = User.objects.filter(
#         profile__department='Engineers',
#         is_staff=True,
#         is_active=True
#     )
#
#     cities = Customer.objects.values_list(
#         'City', flat=True
#     ).distinct().order_by('City')
#
#     if request.method == 'POST':
#
#         # ---------------- USER CREATION ----------------
#         form = UserCreationForm(request.POST)
#
#         if not form.is_valid():
#             messages.error(request, "User form is invalid")
#             return render(request, 'customer/Comp_Cust.html', {
#                 'form': form,
#                 'count1': count1,
#                 'notification1': notification1,
#                 'engineers': engineers,
#                 'cities': cities,
#             })
#
#         user = form.save(commit=False)
#         user.email = request.POST.get('email')
#         user.save()
#
#         group = Group.objects.get(name='Customers')
#         user.groups.add(group)
#
#         # ---------------- SAFE POST DATA ----------------
#         Comp_name = request.POST.get('Comp_name')
#         Address = request.POST.get('Address')
#         Ups_Soft = request.POST.get('Ups_Soft')
#         email = request.POST.get('email')
#         solar_comp = request.POST.get('solar_comp')
#         UPSC = request.POST.get('UPSC')
#         state = request.POST.get('state')
#         po_order = request.POST.get('po_order')
#         project_type = request.POST.get('project_type')
#         advance_paid = request.POST.get('advance_paid', 'not_paid')
#
#         # Integers (safe)
#         Plant_Capacity = int(request.POST.get('Plant_Capacity', 0))
#         phone = int(request.POST.get('phone', 0))
#         Pincode = int(request.POST.get('Pincode', 0))
#         qunt_solar = int(request.POST.get('qunt_solar', 0))
#         qunt_inv = int(request.POST.get('qunt_inv', 0))
#         sol_warranty = int(request.POST.get('sol_warranty', 0))
#         inv_warranty = int(request.POST.get('inv_warranty', 0))
#         com_warranty = int(request.POST.get('com_warranty', 0))
#         phase = int(request.POST.get('phase', 0))
#
#         # Date
#         po_date_str = request.POST.get('po_date')
#         po_date = datetime.strptime(po_date_str, "%Y-%m-%d").date() if po_date_str else None
#
#
#         # ---------------- CITY ----------------
#         city_name = request.POST.get('city_name')
#         new_city_name = request.POST.get('new_city_name')
#
#         if city_name == "Other" and new_city_name:
#             city_name = new_city_name
#
#         # ---------------- ENGINEER ----------------
#         Teamid = request.POST.get('Engineer_Assigned')
#         team1 = User.objects.get(id=Teamid) if Teamid else None
#
#         # ---------------- PROJECT TYPE ----------------
#         Consumer = None
#         current_load = None
#         loadsancution = None
#         solar_pump = None
#         pump_qunt = None
#         pump_warranty = None
#
#         if project_type == "Water Pump":
#             solar_pump = request.POST.get('solar_pump')
#             pump_qunt = int(request.POST.get('pump_qunt', 0))
#             pump_warranty = int(request.POST.get('pump_warranty', 0))
#         else:
#             Consumer = request.POST.get('Consumer')
#             current_load = int(request.POST.get('Bill_unit', 0))
#             loadsancution = int(request.POST.get('loadsancution', 0))
#
#         # ---------------- CUSTOMER SAVE ----------------
#         new_cust = Customer.objects.create(
#             Comp_name=Comp_name,
#             Consumer=Consumer,
#             current_load=current_load,
#             Address=Address,
#             Plant_Capacity=Plant_Capacity,
#             Ups_Soft=Ups_Soft,
#             Cust_type=Cust_type,
#             City=city_name,
#             email=email,
#             phone=phone,
#             solar_comp=solar_comp,
#             UPSC=UPSC,
#             Emp_id=request.user,
#             state=state,
#             Pincode=Pincode,
#             new_customer=user,
#             loadsancution=loadsancution,
#             po_date=po_date,
#             po_order=po_order,
#             Engg_Assign=team1,
#             qunt_solar=qunt_solar,
#             qunt_inv=qunt_inv,
#             sol_warranty=sol_warranty,
#             inv_warranty=inv_warranty,
#             com_warranty=com_warranty,
#             project_type=project_type,
#             solar_pump=solar_pump,
#             pump_qunt=pump_qunt,
#             pump_warranty=pump_warranty,
#             phase=phase,
#             advance_paid=advance_paid
#         )
#
#         # ---------------- RESULT SAVE ----------------
#         Result.objects.create(
#             consumer=Comp_name,
#             consumer_id=new_cust,
#             AssignTo=request.user
#         )
#
#         messages.success(request, "New Customer enrolled Successfully")
#
#     # ---------------- GET REQUEST ----------------
#     form = UserCreationForm()
#     return render(request, 'customer/Comp_Cust.html', {
#         'form': form,
#         'count1': count1,
#         'notification1': notification1,
#         'engineers': engineers,
#         'cities': cities,
#     })
#
#
#
# @login_required(login_url='user-login')
# def Govt_Cust(request):
#     Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     Cust_type = 'Goverment'
#     engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')
#     cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')
#
#     if request.method == 'POST':
#         # Create a new user first
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.email = request.POST['email']  # Add email to user object
#             user.save()
#             # Add the user to the 'Customers' group
#             group = Group.objects.get(name='Customers')
#             user.groups.add(group)
#
#             # Retrieve phase value from POST data
#             phase = int(request.POST.get('phase', 0))  # Default to 0 if not provided
#
#             Comp_name = request.POST['Comp_name']
#             Consumer= request.POST['Consumer']
#             current_load= request.POST['Bill_unit']
#             Address= request.POST['Address']
#             Plant_Capacity=int(request.POST['Plant_Capacity'])
#             Ups_Soft= request.POST['Ups_Soft']
#             email= request.POST['email']
#             phone=int(request.POST['phone'])
#             solar_comp= request.POST['solar_comp']
#             UPSC= request.POST['UPSC']
#             state= request.POST['state']
#             Pincode=int(request.POST['Pincode'])
#             Gender= request.POST.get('Gender')
#             loadsancution = request.POST['loadsancution']
#             po_date = (request.POST['po_date'])
#             po_order = request.POST['po_order']
#             qunt_solar = request.POST['qunt_solar']
#             qunt_inv = request.POST['qunt_inv']
#             Teamid = request.POST['Engineer_Assigned']
#             city_name = request.POST.get('city_name')
#             new_city_name = request.POST.get('new_city_name')
#             Emp_id = request.user
#
#             sol_warranty = request.POST['sol_warranty']
#             inv_warranty = request.POST['inv_warranty']
#             com_warranty = request.POST['com_warranty']
#             project_type = request.POST['project_type']
#
#             advance_paid = request.POST.get('advance_paid')  # Will be 'paid' or 'not_paid'
#
#             # Initialize fields
#             Consumer = None
#             current_load = None
#             loadsancution = None
#             solar_pump = None
#             pump_qunt = None
#             pump_warranty = None
#
#             if project_type == "Water Pump":
#                 solar_pump = request.POST.get('solar_pump')
#                 pump_qunt = request.POST.get('pump_qunt')
#                 pump_warranty = request.POST.get('pump_warranty')
#             else:
#                 Consumer = request.POST.get('Consumer')
#                 current_load = request.POST.get('Bill_unit')
#                 loadsancution = request.POST.get('loadsancution')
#
#
#             if city_name == "Other" and new_city_name:
#                 # Check if the new city already exists in the database
#                 existing_city = Customer.objects.filter(City=new_city_name).first()
#                 if not existing_city:
#                     city_name = new_city_name
#                 else:
#                     city_name = new_city_name
#
#             if Teamid:
#                 team1 = User.objects.get(id=Teamid)
#             else:
#                 team1 = 1
#
#             new_cust = Customer(Cust_id=Cust_id, Comp_name=Comp_name, Consumer=Consumer, current_load=current_load,
#                                 Address=Address, Plant_Capacity=Plant_Capacity, Ups_Soft=Ups_Soft, Cust_type=Cust_type,
#                                 City=city_name, email=email, phone=phone, solar_comp=solar_comp,
#                                 UPSC=UPSC, Emp_id=Emp_id, state=state, Pincode=Pincode, new_customer=user, loadsancution=loadsancution, po_date=po_date, po_order=po_order,
#                                 Engg_Assign=team1, qunt_solar=qunt_solar, qunt_inv=qunt_inv, sol_warranty=sol_warranty, inv_warranty=inv_warranty, com_warranty=com_warranty,
#                                 project_type=project_type, solar_pump=solar_pump, pump_qunt=pump_qunt, pump_warranty=pump_warranty, phase=phase,  advance_paid=advance_paid)
#             new_cust.save()
#
#             # After saving Customer, create related Result entry
#             result = Result.objects.create(
#                 consumer=Comp_name,  # Or any other field like customer name
#                 consumer_id=new_cust,  # Link to newly created Customer
#                 AssignTo=Emp_id if isinstance(Emp_id, User) else None  # Assign the engineer if available
#             )
#             result.save()
#
#             messages.info(request, 'New Consumer enrolled Successfully')
#             cust = Customer.objects.all()
#             if Cust_id:
#                 cust = cust.filter(Cust_id=Cust_id)
#                 context = {
#                     'count1': count1,
#                     'cust': cust,
#                     'notification1': notification1,
#                     'engineers': engineers,
#                     'cities': cities,
#                 }
#                 return render(request , 'customer/Govt_Cust.html', context)
#             return HttpResponse("Form is not valid")  # Add this line
#            # return HttpResponseRedirect(request, 'customer/Govt_Cust.html', context)
#     else:
#         form = UserCreationForm()
#         context = {
#             'form': form,
#             'count1': count1,
#             'notification1': notification1,
#             'engineers': engineers,
#             'cities': cities,
#         }
#         return render(request, 'customer/Govt_Cust.html', context)


@login_required(login_url='user-login')
def Comp_Cust(request):
    # Check if coming from quotation conversion
    from_quotation = request.GET.get('from_quotation', False)

    # Debug: Print all GET parameters
    print(f"DEBUG Comp_Cust - from_quotation: {from_quotation}")
    if from_quotation:
        print("DEBUG Comp_Cust - All GET parameters:")
        for key, value in request.GET.items():
            print(f"  {key}: {value}")

    count1 = staff_Notification.objects.filter(
        staff_id=request.user.id, status=False
    ).count()

    notification1 = staff_Notification.objects.filter(
        staff_id=request.user.id, status=False
    ).order_by('-created_at')

    Cust_type = 'Industrial'

    engineers = User.objects.filter(
        profile__department='Engineers',
        is_staff=True,
        is_active=True
    )
    associates = User.objects.filter(
        profile__department='Associate',
        is_staff=True,
        is_active=True
    )

    cities = Customer.objects.values_list(
        'City', flat=True
    ).distinct().order_by('City')

    # Initialize context with default values
    context = {
        'count1': count1,
        'notification1': notification1,
        'engineers': engineers,
        'associates': associates,
        'cities': cities,
        'Cust_type': Cust_type,
        'from_quotation': from_quotation,
    }

    # If coming from quotation, get data from URL parameters
    if from_quotation:
        # Extract and process data from GET parameters
        consumer_type = request.GET.get('consumer_type', '')
        project_type = request.GET.get('project_type', '')

        # Handle plant capacity - safely convert to float
        plant_capacity = request.GET.get('plant_capacity', '')
        if plant_capacity:
            try:
                plant_capacity = float(plant_capacity)
            except (ValueError, TypeError):
                plant_capacity = ''

        # Handle phase conversion
        phase = request.GET.get('phase', '')
        if '1 Phase' in str(phase) or str(phase) == '1' or 'Single Phase' in str(phase):
            phase = 1
        elif '3 Phase' in str(phase) or str(phase) == '3' or 'Three Phase' in str(phase):
            phase = 3
        elif str(phase) == '0' or 'Not Applicable' in str(phase):
            phase = 0
        else:
            try:
                phase = int(phase)
            except (ValueError, TypeError):
                phase = ''

        # Get consumer full name for company/farm name
        consumer_full_name = request.GET.get('consumer_full_name', '')
        comp_name = request.GET.get('comp_name', consumer_full_name)

        # Get city
        city = request.GET.get('city', '')

        # Get consumer number
        consumer_no = request.GET.get('consumer_no', '')

        # Get PO details
        po_order_no = request.GET.get('po_order_no', '')
        po_date = request.GET.get('po_date', '')

        # Get other details
        address = request.GET.get('address', '')
        state = request.GET.get('state', '')
        email = request.GET.get('email', '')
        phone = request.GET.get('phone', '')

        # Update context with ALL values
        context.update({
            'consumer_type': consumer_type,
            'project_type': project_type,
            'Plant_Capacity': plant_capacity,
            'phase': phase,
            'po_order': po_order_no,
            'po_date': po_date,
            'Comp_name': comp_name,
            'Address': address,
            'city_name': city,
            'state': state,
            'email': email,
            'phone': phone,
            'Consumer': consumer_no,
        })

        # Debug: Print what we're setting in context
        print(f"DEBUG Comp_Cust - Context data being set:")
        for key in ['consumer_type', 'project_type', 'Plant_Capacity', 'phase', 'po_order',
                    'po_date', 'Comp_name', 'Address', 'city_name', 'state', 'email',
                    'phone', 'Consumer']:
            print(f"  {key}: {context.get(key, 'Not set')}")

    if request.method == 'POST':
        # ---------------- USER CREATION ----------------
        form = UserCreationForm(request.POST)

        if not form.is_valid():
            messages.error(request, "User form is invalid")
            context['form'] = form
            return render(request, 'customer/Comp_Cust.html', context)

        user = form.save(commit=False)
        user.email = request.POST.get('email')
        user.save()

        group = Group.objects.get(name='Customers')
        user.groups.add(group)

        # ---------------- SAFE POST DATA ----------------
        Comp_name = request.POST.get('Comp_name')
        Address = request.POST.get('Address')
        Ups_Soft = request.POST.get('Ups_Soft')
        email = request.POST.get('email')
        solar_comp = request.POST.get('solar_comp')
        UPSC = request.POST.get('UPSC')
        state = request.POST.get('state')
        po_order = request.POST.get('po_order')
        project_type = request.POST.get('project_type')
        advance_paid = request.POST.get('advance_paid', 'not_paid')

        # Integers (safe)
        Plant_Capacity = int(request.POST.get('Plant_Capacity', 0))
        phone = int(request.POST.get('phone', 0))
        Pincode = int(request.POST.get('Pincode', 0))
        qunt_solar = int(request.POST.get('qunt_solar', 0))
        qunt_inv = int(request.POST.get('qunt_inv', 0))
        sol_warranty = int(request.POST.get('sol_warranty', 0))
        inv_warranty = int(request.POST.get('inv_warranty', 0))
        com_warranty = int(request.POST.get('com_warranty', 0))
        phase = int(request.POST.get('phase', 0))

        # Date
        po_date_str = request.POST.get('po_date')
        po_date = datetime.strptime(po_date_str, "%Y-%m-%d").date() if po_date_str else None

        # ---------------- CITY ----------------
        city_name = request.POST.get('city_name')
        new_city_name = request.POST.get('new_city_name')

        if city_name == "Other" and new_city_name:
            city_name = new_city_name

        # ---------------- ENGINEER ----------------
        Teamid = request.POST.get('Engineer_Assigned')
        team1 = User.objects.get(id=Teamid) if Teamid else None
        AssocId = request.POST.get('Associate_Assigned')
        assoc_user = User.objects.get(id=AssocId) if AssocId else None

        # ---------------- PROJECT TYPE ----------------
        Consumer = None
        current_load = None
        loadsancution = None
        solar_pump = None
        pump_qunt = None
        pump_warranty = None

        if project_type == "Water Pump":
            solar_pump = request.POST.get('solar_pump')
            pump_qunt = int(request.POST.get('pump_qunt', 0))
            pump_warranty = int(request.POST.get('pump_warranty', 0))
        else:
            Consumer = request.POST.get('Consumer')
            current_load = int(request.POST.get('Bill_unit', 0))
            loadsancution = int(request.POST.get('loadsancution', 0))

        # ---------------- CUSTOMER SAVE ----------------
        Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1

        new_cust = Customer.objects.create(
            Cust_id=Cust_id,
            Comp_name=Comp_name,
            Consumer=Consumer,
            current_load=current_load,
            Address=Address,
            Plant_Capacity=Plant_Capacity,
            Ups_Soft=Ups_Soft,
            Cust_type=Cust_type,
            City=city_name,
            email=email,
            phone=phone,
            solar_comp=solar_comp,
            UPSC=UPSC,
            Emp_id=request.user,
            state=state,
            Pincode=Pincode,
            new_customer=user,
            loadsancution=loadsancution,
            po_date=po_date,
            po_order=po_order,
            Engg_Assign=team1,
            Assoc_Assign=assoc_user,
            qunt_solar=qunt_solar,
            qunt_inv=qunt_inv,
            sol_warranty=sol_warranty,
            inv_warranty=inv_warranty,
            com_warranty=com_warranty,
            project_type=project_type,
            solar_pump=solar_pump,
            pump_qunt=pump_qunt,
            pump_warranty=pump_warranty,
            phase=phase,
            advance_paid=advance_paid
        )

        # # If this customer was created from a quotation conversion, mark the quotation converted
        # quotation_id = request.GET.get('quotation_id') or request.POST.get('quotation_id') or \
        #                (request.session.get('quotation_data', {}) or {}).get('quotation_id')
        # if quotation_id:
        #     try:
        #         Quotation.objects.filter(pk=quotation_id).update(convert_consumer=True)
        #     except Exception as e:
        #         print(f"Failed to mark quotation {quotation_id} as converted: {e}")
        #
        # # ---------------- RESULT SAVE ----------------
        # Result.objects.create(
        #     consumer=Comp_name,
        #     consumer_id=new_cust,
        #     AssignTo=request.user
        # )
        new_cust.save()

        # If this customer was created from a quotation conversion, mark the quotation converted
        quotation_id = request.GET.get('quotation_id') or request.POST.get('quotation_id') or \
                       (request.session.get('quotation_data', {}) or {}).get('quotation_id')
        if quotation_id:
            try:
                Quotation.objects.filter(pk=quotation_id).update(convert_consumer=True)
            except Exception as e:
                print(f"Failed to mark quotation {quotation_id} as converted: {e}")

        # After saving Customer, create related Result entry
        result = Result.objects.create(
            consumer=Comp_name,
            consumer_id=new_cust,
            AssignTo=request.user
        )
        result.save()

        messages.success(request, "New Customer enrolled Successfully")
        return HttpResponseRedirect(reverse('customer-cust'))

    # ---------------- GET REQUEST ----------------
    form = UserCreationForm()
    context['form'] = form
    return render(request, 'customer/Comp_Cust.html', context)


@login_required(login_url='user-login')
def Govt_Cust(request):
    # Check if coming from quotation conversion
    from_quotation = request.GET.get('from_quotation', False)

    # Debug: Print all GET parameters
    print(f"DEBUG Govt_Cust - from_quotation: {from_quotation}")
    if from_quotation:
        print("DEBUG Govt_Cust - All GET parameters:")
        for key, value in request.GET.items():
            print(f"  {key}: {value}")

    Cust_id = 1001 if Customer.objects.count() == 0 else Customer.objects.aggregate(max=Max('Cust_id'))["max"] + 1
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    Cust_type = 'Goverment'
    engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(
        is_staff='1').filter(is_active='1')
    associates = User.objects.filter(profile__department__isnull=False).filter(profile__department='Associate').filter(
        is_staff='1').filter(is_active='1')
    cities = Customer.objects.values_list('City', flat=True).distinct().order_by('City')

    # Initialize context with default values
    context = {
        'count1': count1,
        'notification1': notification1,
        'engineers': engineers,
        'associates': associates,
        'cities': cities,
        'Cust_type': Cust_type,
        'from_quotation': from_quotation,
    }

    # If coming from quotation, get data from URL parameters
    if from_quotation:
        # Extract and process data from GET parameters
        consumer_type = request.GET.get('consumer_type', '')
        project_type = request.GET.get('project_type', '')

        # Handle plant capacity - safely convert to float
        plant_capacity = request.GET.get('plant_capacity', '')
        if plant_capacity:
            try:
                plant_capacity = float(plant_capacity)
            except (ValueError, TypeError):
                plant_capacity = ''

        # Handle phase conversion
        phase = request.GET.get('phase', '')
        if '1 Phase' in str(phase) or str(phase) == '1' or 'Single Phase' in str(phase):
            phase = 1
        elif '3 Phase' in str(phase) or str(phase) == '3' or 'Three Phase' in str(phase):
            phase = 3
        elif str(phase) == '0' or 'Not Applicable' in str(phase):
            phase = 0
        else:
            try:
                phase = int(phase)
            except (ValueError, TypeError):
                phase = ''

        # Get consumer full name for company/farm name
        consumer_full_name = request.GET.get('consumer_full_name', '')
        comp_name = request.GET.get('comp_name', consumer_full_name)

        # Get city
        city = request.GET.get('city', '')

        # Get consumer number
        consumer_no = request.GET.get('consumer_no', '')

        # Get PO details
        po_order_no = request.GET.get('po_order_no', '')
        po_date = request.GET.get('po_date', '')

        # Get other details
        address = request.GET.get('address', '')
        state = request.GET.get('state', '')
        email = request.GET.get('email', '')
        phone = request.GET.get('phone', '')

        # Update context with ALL values
        context.update({
            'consumer_type': consumer_type,
            'project_type': project_type,
            'Plant_Capacity': plant_capacity,
            'phase': phase,
            'po_order': po_order_no,
            'po_date': po_date,
            'Comp_name': comp_name,
            'Address': address,
            'city_name': city,
            'state': state,
            'email': email,
            'phone': phone,
            'Consumer': consumer_no,
        })

        # Debug: Print what we're setting in context
        print(f"DEBUG Govt_Cust - Context data being set:")
        for key in ['consumer_type', 'project_type', 'Plant_Capacity', 'phase', 'po_order',
                    'po_date', 'Comp_name', 'Address', 'city_name', 'state', 'email',
                    'phone', 'Consumer']:
            print(f"  {key}: {context.get(key, 'Not set')}")

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

            # Retrieve phase value from POST data
            phase = int(request.POST.get('phase', 0))  # Default to 0 if not provided

            Comp_name = request.POST['Comp_name']
            Consumer = request.POST['Consumer']
            current_load = request.POST['Bill_unit']
            Address = request.POST['Address']
            Plant_Capacity = int(request.POST['Plant_Capacity'])
            Ups_Soft = request.POST['Ups_Soft']
            email = request.POST['email']
            phone = int(request.POST['phone'])
            solar_comp = request.POST['solar_comp']
            UPSC = request.POST['UPSC']
            state = request.POST['state']
            Pincode = int(request.POST['Pincode'])
            loadsancution = request.POST['loadsancution']
            # po_date = (request.POST['po_date'])
            # Date
            po_date_str = request.POST.get('po_date')
            po_date = datetime.strptime(po_date_str, "%Y-%m-%d").date() if po_date_str else None

            po_order = request.POST['po_order']
            qunt_solar = request.POST['qunt_solar']
            qunt_inv = request.POST['qunt_inv']
            Teamid = request.POST['Engineer_Assigned']
            AssocId = request.POST.get('Associate_Assigned')
            city_name = request.POST.get('city_name')
            new_city_name = request.POST.get('new_city_name')
            Emp_id = request.user

            sol_warranty = request.POST['sol_warranty']
            inv_warranty = request.POST['inv_warranty']
            com_warranty = request.POST['com_warranty']
            project_type = request.POST['project_type']
            advance_paid = request.POST.get('advance_paid')  # Will be 'paid' or 'not_paid'

            # Initialize fields
            Consumer = None
            current_load = None
            loadsancution = None
            solar_pump = None
            pump_qunt = None
            pump_warranty = None

            if project_type == "Water Pump":
                solar_pump = request.POST.get('solar_pump')
                pump_qunt = request.POST.get('pump_qunt')
                pump_warranty = request.POST.get('pump_warranty')
            else:
                Consumer = request.POST.get('Consumer')
                current_load = request.POST.get('Bill_unit')
                loadsancution = request.POST.get('loadsancution')

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

            assoc_user = User.objects.get(id=AssocId) if AssocId else None

            new_cust = Customer(
                Cust_id=Cust_id,
                Comp_name=Comp_name,
                Consumer=Consumer,
                current_load=current_load,
                Address=Address,
                Plant_Capacity=Plant_Capacity,
                Ups_Soft=Ups_Soft,
                Cust_type=Cust_type,
                City=city_name,
                email=email,
                phone=phone,
                solar_comp=solar_comp,
                UPSC=UPSC,
                Emp_id=Emp_id,
                state=state,
                Pincode=Pincode,
                new_customer=user,
                loadsancution=loadsancution,
                po_date=po_date,
                po_order=po_order,
                Engg_Assign=team1,
                Assoc_Assign=assoc_user,
                qunt_solar=qunt_solar,
                qunt_inv=qunt_inv,
                sol_warranty=sol_warranty,
                inv_warranty=inv_warranty,
                com_warranty=com_warranty,
                project_type=project_type,
                solar_pump=solar_pump,
                pump_qunt=pump_qunt,
                pump_warranty=pump_warranty,
                phase=phase,
                advance_paid=advance_paid
            )
            new_cust.save()

            # If this customer was created from a quotation conversion, mark the quotation converted
            quotation_id = request.GET.get('quotation_id') or request.POST.get('quotation_id') or \
                           (request.session.get('quotation_data', {}) or {}).get('quotation_id')
            if quotation_id:
                try:
                    Quotation.objects.filter(pk=quotation_id).update(convert_consumer=True)
                except Exception as e:
                    print(f"Failed to mark quotation {quotation_id} as converted: {e}")


            # After saving Customer, create related Result entry
            result = Result.objects.create(
                consumer=Comp_name,
                consumer_id=new_cust,
                AssignTo=Emp_id if isinstance(Emp_id, User) else None
            )
            result.save()

            messages.info(request, 'New Consumer enrolled Successfully')
            cust = customer_queryset_for_request(request.user)
            if Cust_id:
                cust = cust.filter(Cust_id=Cust_id)
                context = {
                    'count1': count1,
                    'cust': cust,
                    'notification1': notification1,
                    'engineers': engineers,
                    'associates': associates,
                    'cities': cities,
                }
                return render(request, 'customer/Govt_Cust.html', context)
        else:
            context['form'] = form
            return render(request, 'customer/Govt_Cust.html', context)

    # GET REQUEST
    form = UserCreationForm()
    context['form'] = form
    return render(request, 'customer/Govt_Cust.html', context)


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
        displaydata = customer_queryset_for_request(request.user)
        return render(request, 'customer/Cust_Search.html', {"data": displaydata, "count1": count1, "notification1": notification1})

from django.db.models import Q
from django.utils import timezone


@login_required(login_url='user-login')
def view_all_cust(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    mseb = MSEB.objects.all()

    solar_items = BarcodeImage.objects.filter(product_name='SolarPanel')
    inverter_items = BarcodeImage.objects.filter(product_name='Inverter')
    replace_items = BarcodeImage.objects.filter(product_name='Replace')
    solar_panel_total_quantity = solar_items.count()
    solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
    inverter_panel_total_quantity = inverter_items.count()
    inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
    replace_panel_total_quantity = replace_items.count()
    replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))

    # Get the filter option from the GET request
    filter_option = request.GET.get('filter', 'All')
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
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
        caption_text1 = "Today"
    elif filter_option == "Last7Days":
        start_date = today - timedelta(days=7)
        end_date = today
        caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
        # caption_text = "Display Last 7 Days View"
        caption_text1 = "Last 7 Days"
    elif filter_option == "Last30Days":
        start_date = today - timedelta(days=30)
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

    # Filter by user's permissions (Associates: Assoc_Assign; other staff: Engg_Assign)
    emps = customer_queryset_for_request(request.user)

    # Define a variable to store the filtered data
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

    # po_date may be stored as text in PostgreSQL while Django model uses DateField — cast for comparisons
    def _po_date_cast(qs):
        return qs.annotate(_po_d_cast=Cast('po_date', output_field=DateField()))

    if filter_option == 'Today':
        emps = _po_date_cast(emps).filter(_po_d_cast=today.date())
    elif filter_option == 'Last7Days':
        last_week = today - timedelta(days=7)
        emps = _po_date_cast(emps).filter(_po_d_cast__gte=last_week.date())
    elif filter_option == 'Last30Days':
        last_month = today - timedelta(days=30)
        emps = _po_date_cast(emps).filter(_po_d_cast__gte=last_month.date())
    elif filter_option == 'ThisMonth':
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        emps = _po_date_cast(emps).filter(_po_d_cast__gte=current_month.date())

    # Handle the custom range filter
    if filter_option == 'Custom' and start_date and end_date:
        try:
            sd = datetime.strptime(str(start_date)[:10], '%Y-%m-%d').date()
            ed = datetime.strptime(str(end_date)[:10], '%Y-%m-%d').date()
            emps = _po_date_cast(emps).filter(_po_d_cast__range=(sd, ed))
        except ValueError:
            pass

    if request.method == 'POST':
        name = request.POST.get('name', None)
        dept = request.POST.get('dept', None)

        if name:
             emps = emps.filter(Q(Comp_name__icontains=name)| Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(phone__icontains=name) | Q(state__icontains=name) | Q(City__icontains=name) | Q(Cust_id__icontains=name))
        if dept:
            emps = emps.filter(Q(Cust_type__icontains=dept))

        # Check if filter_option is not "Custom" before applying the filter
        if filter_option != 'Custom':
            today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

            if filter_option == 'Today':
                emps = _po_date_cast(emps).filter(_po_d_cast=today.date())
            elif filter_option == 'Last7Days':
                last_week = today - timedelta(days=7)
                emps = _po_date_cast(emps).filter(_po_d_cast__gte=last_week.date())
            elif filter_option == 'Last30Days':
                last_month = today - timedelta(days=30)
                emps = _po_date_cast(emps).filter(_po_d_cast__gte=last_month.date())
            elif filter_option == 'ThisMonth':
                current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                emps = _po_date_cast(emps).filter(_po_d_cast__gte=current_month.date())

        # Calculate project status (all users; queryset already scoped above)
        project_status_list = []
        for cust in emps:
            solar_condition = BarcodeImage.objects.filter(product_name='SolarPanel',
                                                          AssignTo_id=cust.new_customer_id).count() >= cust.qunt_solar

            inverter_condition = BarcodeImage.objects.filter(product_name='Inverter',
                                                             AssignTo_id=cust.new_customer_id).count() >= cust.qunt_inv

            meter_condition = (
                    Meters.objects.annotate(trimmed=Trim('comp_name'))
                    .filter(trimmed=cust.Comp_name.strip()).exists()
                    and
                    GenerationMeter.objects.annotate(trimmed=Trim('comp_name'))
                    .filter(trimmed=cust.Comp_name.strip()).exists()
            )

            mseb_condition = MSEB.objects.filter(
                customer__Cust_id=cust.Cust_id,
                installation_date_date__isnull=False
            ).exists()

            if solar_condition and inverter_condition and meter_condition and mseb_condition:
                project_status = "Completed"
            else:
                project_status = "Pending"

            project_status_list.append({
                'Cust_id': cust.Cust_id,
                'project_status': project_status
            })

        emps = list(emps)
        for emp in emps:
            for status in project_status_list:
                if emp.Cust_id == status['Cust_id']:
                    emp.project_status = status['project_status']
                    break

        context = {

            'mseb_record': mseb,
            'emps': emps,
            'count1': count1,
            'notification1': notification1,
            'solar_panel_total_quantity': solar_panel_total_quantity,
            'inverter_panel_total_quantity': inverter_panel_total_quantity,
        }
        return render(request, 'customer/view_all_cust.html', context)
    elif request.method == 'GET':
        project_status_list = []
        for cust in emps:

            solar_condition = BarcodeImage.objects.filter(product_name='SolarPanel',
                                                          AssignTo_id=cust.new_customer_id).count() >= cust.qunt_solar
            inverter_condition = BarcodeImage.objects.filter(product_name='Inverter',
                                                             AssignTo_id=cust.new_customer_id).count() >= cust.qunt_inv

            meter_condition = (
                    Meters.objects.annotate(trimmed=Trim('comp_name'))
                    .filter(trimmed=cust.Comp_name.strip()).exists()
                    and
                    GenerationMeter.objects.annotate(trimmed=Trim('comp_name'))
                    .filter(trimmed=cust.Comp_name.strip()).exists()
            )

            mseb_condition = MSEB.objects.filter(
                customer__Cust_id=cust.Cust_id,
                installation_date_date__isnull=False
            ).exists()

            # Determine project status
            if solar_condition and inverter_condition and meter_condition and mseb_condition:
                project_status = "Completed"
            else:
                project_status = "Pending"

            project_status_list.append({
                'Cust_id': cust.Cust_id,
                'project_status': project_status
            })

        # Merge status list with customers
        emps = list(emps)
        for emp in emps:
            for status in project_status_list:
                if emp.Cust_id == status['Cust_id']:
                    emp.project_status = status['project_status']
                    break

        context = {

            'mseb_record': mseb,
            'emps': emps,
            'count1': count1,
            'notification1': notification1,
            'solar_panel_total_quantity': solar_panel_total_quantity,
            'inverter_panel_total_quantity': inverter_panel_total_quantity,
            'caption_text': caption_text,
            'caption_text1': caption_text1,
        }
        return render(request, 'customer/view_all_cust.html', context)
    else:
        return HttpResponse('An Exception Occurred')


@login_required(login_url='user-login')
def view_all(request):

        base_customers = customer_queryset_for_request(request.user)
        totalIndividual = base_customers.filter(Cust_type='Residential').count()
        totalComersial = base_customers.filter(Cust_type='Commersial').count()
        totalCompany = base_customers.filter(Cust_type='Industrial').count()
        totalGoverment = base_customers.filter(Cust_type='Goverment').count()
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
        project_status_list = []
        customer_type = request.GET.get('Cust_type')

        customers = base_customers

        mseb = MSEB.objects.all()

        solar_items = BarcodeImage.objects.filter(product_name='SolarPanel')
        inverter_items = BarcodeImage.objects.filter(product_name='Inverter')
        replace_items = BarcodeImage.objects.filter(product_name='Replace')
        solar_panel_total_quantity = solar_items.count()
        solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
        inverter_panel_total_quantity = inverter_items.count()
        inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
        replace_panel_total_quantity = replace_items.count()
        replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))

        if customer_type:
            customers = base_customers.filter(Cust_type=customer_type)

        project_status_list = []
        for cust in customers:

            solar_condition = BarcodeImage.objects.filter(product_name='SolarPanel',
                                                          AssignTo_id=cust.new_customer_id).count() >= cust.qunt_solar
            inverter_condition = BarcodeImage.objects.filter(product_name='Inverter',
                                                             AssignTo_id=cust.new_customer_id).count() >= cust.qunt_inv
            meter_condition = Meters.objects.filter(
                comp_name=cust.Comp_name).exists() and GenerationMeter.objects.filter(comp_name=cust.Comp_name).exists()
            mseb_condition = MSEB.objects.filter(comp_name=cust.Comp_name,
                                                 installation_date_date__isnull=False).exists()

            # Determine project status
            if solar_condition and inverter_condition and meter_condition and mseb_condition:
                project_status = "Completed"
            else:
                project_status = "Pending"

            project_status_list.append({
                'Cust_id': cust.Cust_id,
                'project_status': project_status
            })

        # Merge status list with customers
        emps = list(customers)
        for emp in emps:
            for status in project_status_list:
                if emp.Cust_id == status['Cust_id']:
                    emp.project_status = status['project_status']
                    break

        return render(request, 'customer/index.html', locals())


@login_required(login_url='user-login')
def customer_update(request, Cust_id):

    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    customer = Customer.objects.get(Cust_id=Cust_id)
    engineers = User.objects.filter(profile__department__isnull=False).filter(profile__department='Engineers').filter(is_staff='1').filter(is_active='1')
    associates = User.objects.filter(profile__department__isnull=False).filter(profile__department='Associate').filter(is_staff='1').filter(is_active='1')
    assigned_assoc = customer.Assoc_Assign
    if assigned_assoc:
        associates = associates.exclude(id=assigned_assoc.id)

    # Predefined Project Type options
    project_types = ["Rooftop", "Ground Mount PV", "Street Light", "Water Pump", "Hi-Mas", "Other"]

    # If there's an assigned engineer, remove them from the list
    assigned_user = customer.Engg_Assign
    if assigned_user:
        # assigned_user = engineers.exclude(id=assigned_engineer.id)
        engineers = engineers.exclude(id=assigned_user.id) if assigned_user else User.objects.all()

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

    if 'Cuspoorder' in request.POST:
        po_order = request.POST['Cuspoorder']
    else:
        po_order = None

    if request.method == "POST":
        ct = request.POST['custtype']
        cid = request.POST['custid']
        pc = request.POST['plantcapacity']
        sc = request.POST['solarcomp']
        upsc = request.POST['UPSC']
        cad = request.POST['Cusactdate']
        ph = request.POST['phone']
        email = request.POST['email']
        add = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pin = request.POST['pincode']
        us = request.POST['upssoft']
        qunt_solar = request.POST['qunt_solar']
        qunt_inv = request.POST['qunt_inv']
        Teamid = request.POST['Engineer_Assigned']
        AssocId = request.POST.get('Associate_Assigned')
        sol_warranty = request.POST['sol_warranty']
        inv_warranty = request.POST['inv_warranty']
        com_warranty = request.POST['com_warranty']
        project_type = request.POST.get('projecttype', None)
        # In the POST handling section of customer_update view
        advance_paid = request.POST.get('advance_paid', 'not_paid')


        phase = int(request.POST.get('phase', 0))  # default to 0 if missing

        if project_type == "Water Pump":
            solar_pump = request.POST.get('solar_pump')
            pump_qunt = request.POST.get('pump_qunt')
            pump_warranty = request.POST.get('pump_warranty')

            customer.solar_pump = solar_pump
            customer.pump_qunt = pump_qunt
            customer.pump_warranty = pump_warranty

            # Clear other fields
            customer.Consumer = None
            customer.current_load = None
            customer.loadsancution = None
        else:
            consumer = request.POST.get('consumer')
            current_load = request.POST.get('current_load')
            loadsancution = request.POST.get('loadsancution')

            customer.Consumer = consumer
            customer.current_load = current_load
            customer.loadsancution = loadsancution

            # Clear Water Pump fields
            customer.solar_pump = None
            customer.pump_qunt = None
            customer.pump_warranty = None


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
        customer.email = email
        customer.Address = add
        customer.City = city
        customer.state = state
        customer.Pincode = pin
        customer.qunt_solar = qunt_solar
        customer.qunt_inv = qunt_inv
        customer.sol_warranty =sol_warranty
        customer.inv_warranty = inv_warranty
        customer.com_warranty = com_warranty
        customer.project_type = project_type
        customer.phase = phase
        customer.advance_paid = advance_paid

        if po_order:
            customer.po_order = po_order

        if po_date:
            customer.po_date = po_date

        # Combine first_name and last_name to update Comp_name
        if ct == "Residential":
            customer.Comp_name = f"{firstname} {lastname}".strip()

        if cad:
            customer.Cus_Act_Date = cad

        if Teamid:
            team1 = User.objects.get(id=Teamid)
            customer.Engg_Assign = team1
        else:
            customer.Engg_Assign = 1

        if AssocId:
            customer.Assoc_Assign = User.objects.get(id=AssocId)
        else:
            customer.Assoc_Assign = None

        # Update the associated user’s email if the customer is linked to a user
        if customer.new_customer:
           user = User.objects.filter(id=customer.new_customer.id).first()
           if user:
              user.email = email
              user.save()

        try:
            customer.save()

            # Update related Result record
            try:
                result = Result.objects.get(consumer_id=customer)
                result.consumer = customer.Comp_name
                if customer.Emp_id and isinstance(customer.Emp_id, User):
                    result.AssignTo = customer.Emp_id
                result.save()
            except Result.DoesNotExist:
                # You can choose to create a new Result if needed
                pass

            error="no"
        except:
            error="yes"
    return render(request, 'customer/customer_update.html', locals())


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

@login_required(login_url='user-login')
def Site_Technical_Details(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    companies = Customer.objects.all()

    if request.method == 'POST':
        company_name = request.POST.get('comp_name')
        solar_panel_no = request.POST.get('solar_panel_no')
        detected_barcode = request.POST.get('detected_barcode')
        detected_inverter = request.POST.get('detected_inverter')
        meter_image = request.FILES.get('meter_image')
        netmeter_image = request.FILES.get('netmeter_image')
        abt_meter_image = request.FILES.get('abt_meter_image')
        ct_cubic_image = request.FILES.get('ct_cubic_image')
        new_customer_id = request.POST.get('new_customer_id')

        assign_to_user = User.objects.get(id=new_customer_id) if new_customer_id.isdigit() else None
        customer_instance = get_object_or_404(Customer, id=new_customer_id)

        try:
            new_customer_technical_details = customer_technical_Details.objects.create(
                company_name=company_name,
                meter_image=meter_image,
                netmeter_image=netmeter_image,
                abt_meter_image=abt_meter_image,
                ct_cubic_image=ct_cubic_image,
                AssignTo=assign_to_user,
                AssignBy=request.user
            )

            # Ensure a record exists in the Result table
            result_instance, created = Result.objects.get_or_create(
                consumer_id=customer_instance,
                defaults={
                    'consumer': customer_instance.Comp_name,
                    'AssignTo': assign_to_user,
                    'inspection_report': True
                }
            )

            # If the record already exists, update the inspection_report field
            if not created:
                result_instance.inspection_report = True
                result_instance.save()

            messages.success(request, 'Data saved successfully and inspection report updated.')
            return redirect('customer-Site_Technical_Details')

        except IntegrityError:
            messages.error(request, 'An error occurred while saving the data.')

    return render(request, 'customer/Site_Technical_Details.html', locals())


def _site_inspection_page(request, default_mode='new'):
    """
    Unified Site Inspection: New (entry form) + View (display records) on one template.
    default_mode: 'new' from Site_Inspection_Details URL, 'view' from display_Site_Inspection URL.
    """
    from django.urls import reverse
    from .forms import EditForm

    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    mode = request.GET.get('mode', default_mode)
    if mode not in ('new', 'view'):
        mode = default_mode

    if request.user.is_superuser:
        comp_names_meters = InspectionDetail.objects.values('company_name', 'customer_id').distinct()
    elif request.user.is_staff:
        comp_names_meters = InspectionDetail.objects.filter(
            customer_id__Engg_Assign=request.user
        ).values('company_name', 'customer_id').distinct()
    else:
        comp_names_meters = []

    comp_names = sorted(
        {(item['company_name'], item['customer_id']) for item in comp_names_meters},
        key=lambda x: x[0].lower(),
    )

    existing_company_names = InspectionDetail.objects.values_list('company_name', flat=True).distinct()
    all_customers = Customer.objects.all()
    completed_customers = []

    for cust in all_customers:
        solar_condition = BarcodeImage.objects.filter(product_name='SolarPanel',
                                                      AssignTo_id=cust.new_customer_id).count() >= cust.qunt_solar
        inverter_condition = BarcodeImage.objects.filter(product_name='Inverter',
                                                         AssignTo_id=cust.new_customer_id).count() >= cust.qunt_inv
        meter_condition = Meters.objects.filter(comp_name=cust.Comp_name).exists() and GenerationMeter.objects.filter(
            comp_name=cust.Comp_name).exists()
        mseb_condition = MSEB.objects.filter(comp_name=cust.Comp_name, installation_date_date__isnull=False).exists()

        if solar_condition and inverter_condition and meter_condition and mseb_condition:
            project_status = "Completed"
        else:
            project_status = "Pending"

        if project_status == "Completed" and cust.Comp_name not in existing_company_names:
            completed_customers.append(cust)

    ctx = {
        'companies': completed_customers,
        'count1': count1,
        'notification1': notification1,
        'site_inspection_mode': mode,
        'form': EditForm(),
        'comp_names': comp_names,
    }

    if request.method == 'POST':
        is_preview = (
            request.POST.get('site_inspection_action') == 'preview_view'
            or ('comp_name' in request.POST and 'company_name' not in request.POST)
        )
        if is_preview:
            form = EditForm(request.POST)
            if form.is_valid():
                selected_comp_name = form.cleaned_data['comp_name']
                selected_customer_id = form.cleaned_data['customer_id']

                meters_records = InspectionDetail.objects.filter(customer_id=selected_customer_id)
                mseb = MSEB.objects.filter(customer_id=selected_customer_id)

                meters = Meters.objects.filter(customer__Cust_id=selected_customer_id)
                meter_details = list(meters.values('meter_type', 'make', 'capacity', 'transformer_type', 'transformer_make', 'transformer_capacity'))
                unique_meter_details = {frozenset(item.items()) for item in meter_details}
                meters_count = len(meters)

                generation = GenerationMeter.objects.filter(customer__Cust_id=selected_customer_id)
                generation_details = list(generation.values('make', 'capacity', 'serial_no', 'CT_make', 'CT_capacity', 'CT_serial_no'))
                unique_generation_details = list(generation.values('make', 'capacity', 'CT_make', 'CT_capacity').distinct())
                has_ct_make = any(detail['CT_make'] for detail in unique_generation_details)

                gen_meter_count = len(generation)

                solar_panels = BarcodeImage.objects.filter(company=selected_comp_name, product_name='SolarPanel')
                solar_panel_details = list(solar_panels.values('company_name', 'wattage'))
                unique_solar_panel_details = {frozenset(item.items()) for item in solar_panel_details}
                solar_panel_count = len(solar_panels)

                inverters = BarcodeImage.objects.filter(company=selected_comp_name, product_name='Inverter')
                inverter_details = list(inverters.values('company_name', 'wattage'))
                unique_inverter_details = {frozenset(item.items()) for item in inverter_details}
                inverter_count = len(inverters)

                ctx.update({
                    'form': form,
                    'selected_comp_name': selected_comp_name,
                    'meters_records': meters_records,
                    'unique_meter_details': [dict(item) for item in unique_meter_details],
                    'meter_count': meters_count,
                    'unique_generation_details': [dict(item) for item in unique_generation_details],
                    'gen_meter_count': gen_meter_count,
                    'unique_solar_panel_details': [dict(item) for item in unique_solar_panel_details],
                    'solar_panel_count': solar_panel_count,
                    'unique_inverter_details': [dict(item) for item in unique_inverter_details],
                    'inverter_count': inverter_count,
                    'has_ct_make': has_ct_make,
                    'mseb': mseb,
                    'site_inspection_mode': 'view',
                })
            else:
                ctx['form'] = form
                ctx['site_inspection_mode'] = 'view'
            return render(request, 'customer/Site_Inspection_Details.html', ctx)

        company_name = request.POST.get('company_name')
        if not company_name:
            messages.error(request, 'Please select a company.')
            return redirect(f"{reverse('customer-Site_Inspection_Details')}?mode=new")

        customer = Customer.objects.get(Comp_name=company_name)
        created_at = timezone.now()
        assign_by_id = request.user

        InspectionDetail.objects.create(
            company_name=company_name,
            created_at=created_at,
            customer=customer,
            AssignBy=assign_by_id,
            solar_Module_Completed=request.POST.get('solar_Module_Completed') == 'on',
            solar_Module_Reason=request.POST.get('solar_Module_Reason', ''),
            solar_Module_Reason_other=request.POST.get('solar_Module_Reason_other', ''),
            inverter_Completed=request.POST.get('inverter_Completed') == 'on',
            inverter_Reason=request.POST.get('inverter_Reason', ''),
            inverter_Reason_other=request.POST.get('inverter_Reason_other', ''),
            net_Meter_Completed=request.POST.get('net_Meter_Completed') == 'on',
            net_Meter_Reason=request.POST.get('net_Meter_Reason', ''),
            net_Meter_Reason_other=request.POST.get('net_Meter_Reason_other', ''),
            ct_Completed=request.POST.get('ct_Completed') == 'on',
            ct_Reason=request.POST.get('ct_Reason', ''),
            ct_Checkmark_other=request.POST.get('ct_Checkmark_other', ''),
            generation_Meters_Completed=request.POST.get('generation_Meters_Completed') == 'on',
            generation_Meters_Reason=request.POST.get('generation_Meters_Reason', ''),
            generation_Meters_Reason_other=request.POST.get('generation_Meters_Reason_other', ''),
            gen_CT_Meters_Completed=request.POST.get('gen_CT_Meters_Completed') == 'on',
            gen_CT_Meters_Reason=request.POST.get('gen_CT_Meters_Reason', ''),
            gen_CT_Meters_Reason_other=request.POST.get('gen_CT_Meters_Reason_other', ''),
            ac_Panel_Cabling_Completed=request.POST.get('ac_Panel_Cabling_Completed') == 'on',
            ac_Panel_Cabling_Reason=request.POST.get('ac_Panel_Cabling_Reason', ''),
            ac_Panel_Cabling_Reason_other=request.POST.get('ac_Panel_Cabling_Reason_other', ''),
            dc_Panel_Cabling_Completed=request.POST.get('dc_Panel_Cabling_Completed') == 'on',
            dc_Panel_Cabling_Reason=request.POST.get('dc_Panel_Cabling_Reason', ''),
            dc_Panel_Cabling_Reason_other=request.POST.get('dc_Panel_Cabling_Reason_other', ''),
            fabrication_Completed=request.POST.get('fabrication_Completed') == 'on',
            fabrication_Reason=request.POST.get('fabrication_Reason', ''),
            fabrication_Reason_other=request.POST.get('fabrication_Reason_other', ''),
            walkway_Completed=request.POST.get('walkway_Completed') == 'on',
            walkway_Reason=request.POST.get('walkway_Reason', ''),
            walkway_Reason_other=request.POST.get('walkway_Reason_other', ''),
            pipeline_Completed=request.POST.get('pipeline_Completed') == 'on',
            pipeline_Reason=request.POST.get('pipeline_Reason', ''),
            pipeline_Reason_other=request.POST.get('pipeline_Reason_other', ''),
            ropeway_Completed=request.POST.get('ropeway_Completed') == 'on',
            ropeway_Reason=request.POST.get('ropeway_Reason', ''),
            ropeway_Reason_other=request.POST.get('ropeway_Reason_other', ''),
            rolling_Completed=request.POST.get('rolling_Completed') == 'on',
            rolling_Reason=request.POST.get('rolling_Reason', ''),
            rolling_Reason_other=request.POST.get('rolling_Reason_other', ''),
            overall_Details=request.POST.get('overall_Details', ''),
            info_Correct=request.POST.get('info_Correct') == 'on',
        )

        Result.objects.filter(consumer_id=customer).update(inspection_report=True)
        messages.success(request, "Inspection details successfully saved.")
        return redirect(f"{reverse('customer-Site_Inspection_Details')}?mode=new")

    return render(request, 'customer/Site_Inspection_Details.html', ctx)


@login_required(login_url='user-login')
def Site_Inspection_Details(request):
    return _site_inspection_page(request, default_mode='new')


@login_required(login_url='user-login')
def display_Site_Inspection(request):
    return _site_inspection_page(request, default_mode='view')


def get_company_data(request):
    company_name = request.GET.get('company_name')
    selected_company_name = company_name
    meters = Meters.objects.filter(customer__Comp_name=company_name)
    meter_names = ', '.join(meter.make for meter in meters)
    meter_names = {(item.meter_type, item.make, item.capacity, item.serial_no) for item in meters}
    transformer_names = {(item.transformer_type, item.transformer_make, item.transformer_capacity, item.transformer_serial_number) for item in meters}
    meters_count = meters.count()

    generation = GenerationMeter.objects.filter(customer__Comp_name=company_name)
    generation_names = {(item.make, item.capacity, item.serial_no) for item in generation}
    gen_ct_names = {(item.CT_make, item.CT_capacity, item.CT_serial_no) for item in generation}
    gen_meter_count = generation.count()


    solar_panels = BarcodeImage.objects.filter(company=company_name, product_name='SolarPanel')
    solar_panel_data = {(item.company_name, item.wattage) for item in solar_panels}
    solar_panel_count = solar_panels.count()

    inverters = BarcodeImage.objects.filter(company=company_name, product_name='Inverter')
    inverter_data = {(item.company_name, item.wattage) for item in inverters}
    inverter_count = inverters.count()

    data = {
        'meters': list(meter_names),
        'meter_count': meters_count,
        'meter_names': list(meter_names),
        'transformer_names': list(transformer_names),
        'solarPanelCount': solar_panel_count,
        'inverterCount': inverter_count,
        'solarPanelData': list(solar_panel_data),
        'inverterData': list(inverter_data),
        'generationnames': list(generation_names),
        'gen_names': list(gen_ct_names),
        'gen_count': gen_meter_count,
        'selected_company_name': selected_company_name,
    }
    return JsonResponse(data)


# ================== genrate consumer list pdf ==================

from .forms import consumerGenerationForm, displayinspection

@login_required(login_url='user-login')
def consumer_pdf(request):
    if request.method == 'POST':
        form = consumerGenerationForm(request.POST)
        if form.is_valid():
            customer_type_filter = request.POST.get('userType')
            selected_field = request.POST.get('selectedField')  # Get the selected field from the hidden input
            selected_value = request.POST.get('selectedValue')  # Get the selected value from the hidden input

            # Define the base queryset (scoped for Associate / engineer staff)
            base_queryset = customer_queryset_for_request(request.user)

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
            data = []
            for customer in users:
                customer_profile = customer.profile if hasattr(customer, 'profile') else None
                # print(f'User ID: {customer.Cust_id}, Customer ID: {customer_profile.customer_id if customer_profile else "N/A"}')

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
    qs = customer_queryset_for_request(request.user)
    if selected_field is None or selected_field == 'all':
        # Return all unique values for the selected field
        values = qs.values(selected_field).distinct().order_by(selected_field)
    else:
        # Return unique values for the selected field
        values = qs.values(selected_field).distinct().order_by(selected_field)

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

    response.write(buffer.getvalue())
    buffer.close()

    return response


from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from .models import Meter  # Import your Meter model

@login_required(login_url='user-login')
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


from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Meters, GenerationMeter, GenerationCT
from .forms import GenerationMeterForm, GenerationCTForm
from customer.models import Customer  # Adjust the import path as needed

def filter_comp_names(request):
    user = request.user
    meter_type = request.GET.get('meter_type')

    # 1) Build base “existing_names” from either Meters or GenerationMeter
    if meter_type == 'meters':
        existing_names = Meters.objects.values_list('comp_name', flat=True)
    elif meter_type == 'generation':
        existing_names = GenerationMeter.objects.values_list('comp_name', flat=True)
    else:
        existing_names = []

    # 2) Start from all Customer records that we care about
    base_qs = Customer.objects.annotate(comp_name_clean=Trim(Lower('Comp_name'))).exclude(project_type="Water Pump").order_by('comp_name_clean')
    # base_qs = Customer.objects.annotate(comp_name_clean=Trim(Lower('Comp_name'))).exclude(project_type="Water Pump").exclude(project_type__isnull=True).order_by('comp_name_clean')

    # 3) Role-based narrowing
    if user.is_superuser:
        comp_qs = base_qs
    elif user.is_staff:
        comp_qs = base_qs.filter(Engg_Assign=user)
    else:
        return JsonResponse({'comp_names': []})

    # 4) Exclude any names already used in the selected meter_type
    comp_qs = comp_qs.exclude(Comp_name__in=existing_names)

    # print("Count of comp_names:", len(comp_qs))

    # 5) Return only the three fields your JS needs
    comp_list = comp_qs.values_list('Cust_id', 'Comp_name', 'City')

    return JsonResponse({'comp_names': list(comp_list)})


from django.db.models import Q, Func, F
def newmeters(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    if request.user.is_superuser:
        comp_names = Customer.objects.filter(
            ~Q(project_type="Water Pump") & ~Q(project_type__isnull=True)
        ).annotate(
            comp_name_clean=Func(F('Comp_name'), function='LOWER')
        ).order_by('comp_name_clean').values_list('Cust_id', 'Comp_name')

    elif request.user.is_staff:
        current_engineer = request.user
        comp_names = Customer.objects.filter(
            Engg_Assign=current_engineer
        ).filter(
            ~Q(project_type="Water Pump") & ~Q(project_type__isnull=True)
        ).annotate(
            comp_name_clean=Func(F('Comp_name'), function='LOWER')
        ).order_by('comp_name_clean').values_list('Cust_id', 'Comp_name')

    else:
        comp_names = []

    # --- merged single-page section data ---
    active_meter_tab = 'meter-add-section'

    # View section (same data source logic as display_records)
    if request.user.is_superuser:
        _v_m = Meters.objects.select_related('customer_id').values('comp_name', 'customer_id', 'customer_id__City').distinct()
        _v_gm = GenerationMeter.objects.select_related('customer_id').values('comp_name', 'customer_id', 'customer_id__City').distinct()
        _v_gc = GenerationCT.objects.select_related('customer_id').values('comp_name', 'customer_id', 'customer_id__City').distinct()
    elif request.user.is_staff:
        user = request.user
        _v_m = Meters.objects.filter(customer_id__Engg_Assign=user).select_related('customer_id').values('comp_name', 'customer_id', 'customer_id__City').distinct()
        _v_gm = GenerationMeter.objects.filter(customer_id__Engg_Assign=user).select_related('customer_id').values('comp_name', 'customer_id', 'customer_id__City').distinct()
        _v_gc = GenerationCT.objects.filter(customer_id__Engg_Assign=user).select_related('customer_id').values('comp_name', 'customer_id', 'customer_id__City').distinct()
    else:
        _v_m = _v_gm = _v_gc = []

    view_comp_names = sorted(
        {(x['comp_name'], x['customer_id'], x['customer_id__City']) for x in _v_m} |
        {(x['comp_name'], x['customer_id'], x['customer_id__City']) for x in _v_gm} |
        {(x['comp_name'], x['customer_id'], x['customer_id__City']) for x in _v_gc},
        key=lambda x: (x[0] or '').lower()
    )

    # Delete section (same source logic as edit_records)
    d_m = Meters.objects.values_list('comp_name', 'customer_id').distinct()
    d_gm = GenerationMeter.objects.values_list('comp_name', 'customer_id').distinct()
    d_gc = GenerationCT.objects.values_list('comp_name', 'customer_id').distinct()
    delete_comp_names = sorted([f"{n} ({cid})" for n, cid in (set(d_m) | set(d_gm) | set(d_gc))])

    selected_view_comp_name = None
    selected_view_customer_id = None
    view_meters_records = None
    view_generation_meter_records = None
    view_generation_ct_records = None

    selected_delete_comp_name = None
    delete_meters_records = None
    delete_generation_meter_records = None
    delete_generation_ct_records = None

    search_barcode_value = ''
    search_attempted = False
    search_meters = None
    search_generation_meter = None
    search_customer = None
    search_matched_field = None

    if request.method == 'POST':
        merged_action = (request.POST.get('merged_action') or '').strip()

        if merged_action == 'view_preview':
            active_meter_tab = 'meter-view-section'
            selected_view_comp_name = (request.POST.get('view_comp_name') or '').strip()
            selected_view_customer_id = (request.POST.get('view_customer_id') or '').strip()
            if selected_view_comp_name and selected_view_customer_id:
                view_meters_records = Meters.objects.filter(comp_name=selected_view_comp_name, customer_id=selected_view_customer_id)
                view_generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_view_comp_name, customer_id=selected_view_customer_id)
                view_generation_ct_records = GenerationCT.objects.filter(comp_name=selected_view_comp_name, customer_id=selected_view_customer_id)

        elif merged_action == 'delete_preview':
            active_meter_tab = 'meter-delete-section'
            selected_delete_comp_name = request.POST.get('delete_comp_name')
            if selected_delete_comp_name:
                try:
                    selected_comp_name, customer_id = selected_delete_comp_name.rsplit(" (", 1)
                    customer_id = customer_id[:-1]
                except Exception:
                    selected_comp_name, customer_id = None, None

                if selected_comp_name and customer_id:
                    if request.POST.get('action') == 'delete':
                        delete_records(Meters, selected_comp_name, request.POST.getlist('meters_to_delete'))
                        delete_records(GenerationMeter, selected_comp_name, request.POST.getlist('generation_meters_to_delete'))
                        delete_records(GenerationCT, selected_comp_name, request.POST.getlist('generation_cts_to_delete'))
                        messages.success(request, 'Records Deleted successfully.')

                    delete_meters_records = Meters.objects.filter(comp_name=selected_comp_name, customer_id=customer_id)
                    delete_generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name, customer_id=customer_id)
                    delete_generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name, customer_id=customer_id)

        elif merged_action == 'search_preview':
            active_meter_tab = 'meter-search-section'
            search_attempted = True
            search_barcode_value = (request.POST.get('barcode_value') or '').strip()
            if search_barcode_value:
                search_meters = Meters.objects.filter(serial_no=search_barcode_value).first() or \
                                Meters.objects.filter(transformer_serial_number=search_barcode_value).first()
                if search_meters:
                    search_matched_field = 'serial_no' if search_meters.serial_no == search_barcode_value else 'transformer_serial_number'
                else:
                    search_generation_meter = GenerationMeter.objects.filter(serial_no=search_barcode_value).first() or \
                                              GenerationMeter.objects.filter(CT_serial_no=search_barcode_value).first()
                    if search_generation_meter:
                        search_matched_field = 'serial_no' if search_generation_meter.serial_no == search_barcode_value else 'CT_serial_no'
                meter_obj = search_meters or search_generation_meter
                if meter_obj:
                    try:
                        search_customer = Customer.objects.get(Cust_id=meter_obj.customer_id)
                    except Customer.DoesNotExist:
                        search_customer = None

    return render(request, 'customer/meters.html', {
        'comp_names': comp_names,
        'count1': count1,
        'notification1': notification1,
        'active_meter_tab': active_meter_tab,
        'view_comp_names': view_comp_names,
        'selected_view_comp_name': selected_view_comp_name,
        'selected_view_customer_id': selected_view_customer_id,
        'view_meters_records': view_meters_records,
        'view_generation_meter_records': view_generation_meter_records,
        'view_generation_ct_records': view_generation_ct_records,
        'delete_comp_names': delete_comp_names,
        'selected_delete_comp_name': selected_delete_comp_name,
        'delete_meters_records': delete_meters_records,
        'delete_generation_meter_records': delete_generation_meter_records,
        'delete_generation_ct_records': delete_generation_ct_records,
        'search_barcode_value': search_barcode_value,
        'search_attempted': search_attempted,
        'search_meters': search_meters,
        'search_generation_meter': search_generation_meter,
        'search_customer': search_customer,
        'search_matched_field': search_matched_field,
    })

from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
import traceback


def save_meters(request):
    if request.method == 'POST':
        comp_name = (request.POST.get('Comp_name') or '').strip()
        if not comp_name:
            messages.error(request, 'Please select a company name.')
            return redirect('customer-meters')
        try:
            customer = Customer.objects.get(Comp_name=comp_name)
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid company selected. Choose a company from the list.')
            return redirect('customer-meters')

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

def save_generation_meter(request):
    # Process the data from the Generation Meter form
    comp_name = (request.POST.get('Comp_name') or '').strip()
    if not comp_name:
        messages.error(request, 'Please select a company name.')
        return redirect('customer-meters')
    try:
        customer = Customer.objects.get(Comp_name=comp_name)
    except Customer.DoesNotExist:
        messages.error(request, 'Invalid company selected. Choose a company from the list.')
        return redirect('customer-meters')

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
        comp_name = (request.POST.get('Comp_name') or '').strip()
        if not comp_name:
            messages.error(request, 'Please select a company name.')
            return redirect('customer-meters')
        try:
            customer = Customer.objects.get(Comp_name=comp_name)
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid company selected. Choose a company from the list.')
            return redirect('customer-meters')

        # Check if the checkbox is present in the request.POST data and set required accordingly
        required = 'required' in request.POST

        # Convert the boolean value to 1 or 0
        required_value = int(required)

        row_count = int(request.POST.get('row_count', 0))  # Get the row count

        # Iterate through the rows and save data to the database
        for i in range(row_count):
            make = request.POST.get(f'make_{i}') or request.POST.get('make')
            capacity = request.POST.get(f'capacity_{i}') or request.POST.get('capacity')
            serial_no = request.POST.get(f'serial_no_{i}') or request.POST.get('serial_no')

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


from django.shortcuts import render, redirect
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

# ... other imports ...

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse


import logging
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse


from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT


from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT


from django.shortcuts import render, redirect
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

from django.shortcuts import render, redirect
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT


@login_required(login_url='user-login')
def edit_records(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    # Fetch comp_name and customer_id pairs
    comp_names_meters = Meters.objects.values_list('comp_name', 'customer_id').distinct()
    comp_names_generation_meter = GenerationMeter.objects.values_list('comp_name', 'customer_id').distinct()
    comp_names_generation_ct = GenerationCT.objects.values_list('comp_name', 'customer_id').distinct()

    # Combine unique comp_names from all three models
    comp_names = set(comp_names_meters) | set(comp_names_generation_meter) | set(comp_names_generation_ct)

    # Create combined strings for the dropdown
    comp_names_with_ids = [f"{comp_name} ({customer_id})" for comp_name, customer_id in comp_names]

    # Sort the combined strings in ascending order
    comp_names_with_ids.sort()

    selected_comp_name = None
    meters_records = None
    generation_meter_records = None
    generation_ct_records = None
    selected_comp_name_with_id = None
    if request.method == 'POST':
        selected_comp_name_with_id = request.POST.get('comp_name')

        # Ensure selected_comp_name_with_id is not None
        if selected_comp_name_with_id:
            # Extract the selected_comp_name and customer_id from the combined string
            selected_comp_name, customer_id = selected_comp_name_with_id.rsplit(" (", 1)
            customer_id = customer_id[:-1]  # Remove the closing bracket ")"

            if 'action' in request.POST and request.POST['action'] == 'delete':
                meters_to_delete = request.POST.getlist('meters_to_delete')
                delete_records(Meters, selected_comp_name, meters_to_delete)

                generation_meters_to_delete = request.POST.getlist('generation_meters_to_delete')
                delete_records(GenerationMeter, selected_comp_name, generation_meters_to_delete)

                generation_cts_to_delete = request.POST.getlist('generation_cts_to_delete')
                delete_records(GenerationCT, selected_comp_name, generation_cts_to_delete)

                messages.success(request, 'Records Deleted successfully.')
                return redirect('customer-edit_meters')

            # Fetch records after deletion
            meters_records = Meters.objects.filter(comp_name=selected_comp_name, customer_id=customer_id)
            generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name, customer_id=customer_id)
            generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name, customer_id=customer_id)

    context = {
        'comp_names': comp_names_with_ids,
        'selected_comp_name': selected_comp_name_with_id,
        'meters_records': meters_records,
        'generation_meter_records': generation_meter_records,
        'generation_ct_records': generation_ct_records,
        'count1': count1,
        'notification1': notification1,
    }

    return render(request, 'customer/edit_meters.html', context)

# @login_required(login_url='user-login')
def delete_records(model, comp_name, record_ids):
    # Ensure the correct records are being targeted
    # print(f"Deleting records from {model.__name__} where comp_name='{comp_name}' and id in {record_ids}")
    model.objects.filter(comp_name=comp_name, id__in=record_ids).delete()


from django.shortcuts import render
from .forms import EditForm
from .models import Meters, GenerationMeter, GenerationCT

from django.db import transaction

from django.db import transaction

from django.shortcuts import redirect


@login_required(login_url='user-login')
def display_records(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    if request.user.is_superuser:
        comp_names_meters = Meters.objects.select_related('customer_id').values('comp_name', 'customer_id',
                                                                                'customer_id__City').distinct()
        comp_names_generation_meter = GenerationMeter.objects.select_related('customer_id').values('comp_name',
                                                                                                   'customer_id',
                                                                                                   'customer_id__City').distinct()
        comp_names_generation_ct = GenerationCT.objects.select_related('customer_id').values('comp_name', 'customer_id',
                                                                                             'customer_id__City').distinct()
    elif request.user.is_staff:
        user = request.user
        comp_names_meters = Meters.objects.filter(customer_id__Engg_Assign=user).select_related('customer_id').values(
            'comp_name', 'customer_id', 'customer_id__City').distinct()
        comp_names_generation_meter = GenerationMeter.objects.filter(customer_id__Engg_Assign=user).select_related(
            'customer_id').values('comp_name', 'customer_id', 'customer_id__City').distinct()
        comp_names_generation_ct = GenerationCT.objects.filter(customer_id__Engg_Assign=user).select_related(
            'customer_id').values('comp_name', 'customer_id', 'customer_id__City').distinct()

    # Ensure the set contains (comp_name, customer_id, city)
    comp_names = {(item['comp_name'], item['customer_id'], item['customer_id__City']) for item in comp_names_meters} | \
                 {(item['comp_name'], item['customer_id'], item['customer_id__City']) for item in
                  comp_names_generation_meter} | \
                 {(item['comp_name'], item['customer_id'], item['customer_id__City']) for item in
                  comp_names_generation_ct}

    # Sort the comp_names by comp_name case-insensitively
    comp_names = sorted(comp_names, key=lambda x: x[0].lower())


    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            selected_comp_name = form.cleaned_data['comp_name']
            selected_customer_id = form.cleaned_data['customer_id']

            meters_records = Meters.objects.filter(comp_name=selected_comp_name, customer_id=selected_customer_id)
            generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name,
                                                                      customer_id=selected_customer_id)
            generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name,
                                                                customer_id=selected_customer_id)

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
        # print(f"Got Meters instance: {instance}")
        return instance

    elif model_name == 'generation_meters':
        instance = get_object_or_404(GenerationMeter, id=record_id)
        # print(f"Got GenerationMeter instance: {instance}")
        return instance
    elif model_name == 'generation_cts':
        instance = get_object_or_404(GenerationCT, id=record_id)
        # print(f"Got GenerationCT instance: {instance}")
        return instance
    else:
        return None


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
            status_filter = request.POST.get('status_filter', '')  # Get status_filter for consumer search
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

@login_required(login_url='user-login')
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
        # print(filtered_customers)

        return render(request, 'customer/change_staff.html', {'filtered_customers': filtered_customers, 'unique_departments': unique_departments, 'employees': employees, 'all_users': all_users, 'unique_departments1': unique_departments1, 'employees1': employees1, 'all_users1': all_users1, 'notification1': notification1,
                'count1': count1,})

    return render(request, 'customer/change_staff.html', {'unique_departments': unique_departments, 'employees': employees, 'all_users': all_users, 'notification1': notification1,
                'count1': count1,})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer
from django.contrib.auth.models import User


@login_required(login_url='user-login')
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

            # Convert customer ID to integer
            try:
                customer_id_int = int(customer_id)
                # print("Converted customer ID to int:", customer_id_int)  # Print converted ID for debugging
                customer = Customer.objects.get(Cust_id=customer_id_int)
                # print("Found customer:", customer)  # Print customer object for debugging

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


from django.core.serializers import serialize
from django.http import JsonResponse
from .models import MSEB

from django.http import JsonResponse
from .models import MSEB


import pytz
from django.utils import timezone

import pytz
from django.utils import timezone
# from datetime import datetime


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import make_aware

import pytz

# Allowed MSEB workflow step fields (must match MSEB model + template fieldNames)
MSEB_STEP_FIELD_NAMES = frozenset({
    'load_extension', 'flisibility', 'quotation', 'sent_to_bill', 'net_meter',
    'flexibility', 'approval', 'meter_testing', 'agreement', 'release', 'installation_date',
})

# Ordered workflow booleans (for filters / tracking JSON)
MSEB_WORKFLOW_BOOL_ORDER = (
    'load_extension', 'flisibility', 'quotation', 'sent_to_bill', 'net_meter',
    'flexibility', 'approval', 'meter_testing', 'agreement', 'release', 'installation_date',
)


def _mseb_q_all_workflow_false():
    q = Q()
    for f in MSEB_WORKFLOW_BOOL_ORDER:
        q &= Q(**{f'mseb_data__{f}': False})
    return q


def _mseb_q_any_workflow_true():
    q = Q()
    for f in MSEB_WORKFLOW_BOOL_ORDER:
        q |= Q(**{f'mseb_data__{f}': True})
    return q


def get_mseb_customers_for_mode(mode: str):
    """Return ValuesListQuerySet (Cust_id, Comp_name, City) for unified MSEB page modes."""
    from django.db.models import Exists, OuterRef

    mode = (mode or 'new').lower().replace('-', '_')
    if mode in ('new', 'new_entry'):
        mode = 'new'
    base = Customer.objects.exclude(project_type='Water Pump').annotate(
        comp_name_clean=Trim(Lower('Comp_name'))
    )
    # Use Exists, not Count('mseb_data'): PostgreSQL rejects non-aggregated columns when
    # Count on a joined reverse FK implies GROUP BY.

    if mode == 'new':
        no_mseb_q = ~Exists(
            MSEB.objects.filter(customer_id=OuterRef('Cust_id'))
        )
        all_false = base.filter(_mseb_q_all_workflow_false()).distinct()
        pks = set(base.filter(no_mseb_q).values_list('Cust_id', flat=True)) | set(
            all_false.values_list('Cust_id', flat=True)
        )
        qs = base.filter(Cust_id__in=pks).order_by('comp_name_clean')
    elif mode == 'in_progress':
        not_completed = (
            Q(mseb_data__installation_date_date__isnull=True)
            | Q(mseb_data__installation_date=False)
        )
        qs = (
            base.filter(_mseb_q_any_workflow_true())
            .filter(not_completed)
            .distinct()
            .order_by('comp_name_clean')
        )
    elif mode == 'update':
        qs = base.filter(
            Exists(MSEB.objects.filter(customer_id=OuterRef('Cust_id')))
        ).order_by('comp_name_clean')
    elif mode == 'completed':
        qs = (
            base.filter(
                mseb_data__installation_date=True,
                mseb_data__installation_date_date__isnull=False,
            )
            .distinct()
            .order_by('comp_name_clean')
        )
    else:
        qs = get_mseb_customers_for_mode('new')
    return qs.values_list('Cust_id', 'Comp_name', 'City')


def _mseb_merge_duplicate_rows_for_customer(customer):
    """
    If multiple MSEB rows exist for the same customer, merge into the lowest id row
    and delete the rest. Prevents MultipleObjectsReturned from get_or_create(customer=...).
    """
    rows = list(MSEB.objects.filter(customer=customer).order_by('id'))
    if len(rows) <= 1:
        return rows[0] if rows else None
    primary = rows[0]
    for other in rows[1:]:
        for fn in MSEB_STEP_FIELD_NAMES:
            if getattr(other, fn, False):
                setattr(primary, fn, True)
            pdt = getattr(primary, f'{fn}_date', None)
            odt = getattr(other, f'{fn}_date', None)
            if odt is not None and (pdt is None or odt > pdt):
                setattr(primary, f'{fn}_date', odt)
        if getattr(other, 'comp_name', None) and not primary.comp_name:
            primary.comp_name = other.comp_name
    primary.save()
    MSEB.objects.filter(pk__in=[r.pk for r in rows[1:]]).delete()
    return primary


def _mseb_get_or_create_singleton(customer, comp_name=None):
    """
    Return a single MSEB instance for this customer (same as get_or_create semantics).
    Merges duplicate rows if the DB has more than one (no unique constraint on customer).
    """
    comp = (comp_name if comp_name is not None else customer.Comp_name) or ''
    if MSEB.objects.filter(customer=customer).count() > 1:
        _mseb_merge_duplicate_rows_for_customer(customer)
    inst = MSEB.objects.filter(customer=customer).order_by('id').first()
    if inst is not None:
        return inst, False
    return MSEB.objects.create(customer=customer, comp_name=comp), True


def _mseb_step_save_post(request):
    """Shared AJAX save for MSEB workflow step (checkbox + date)."""
    cust_id = request.POST.get('cust_id')
    customer = get_object_or_404(Customer, Cust_id=cust_id)
    comp_name = customer.Comp_name

    completion_date = request.POST.get('createdAt')
    if completion_date:
        completion_datetime = make_aware(
            datetime.strptime(completion_date, '%Y-%m-%d'),
            timezone=pytz.UTC
        )
    else:
        completion_datetime = timezone.now()

    field_name = request.POST.get('fieldName')
    if not field_name or field_name not in MSEB_STEP_FIELD_NAMES:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid or missing field name'},
            status=400,
        )

    mseb_instance, created = _mseb_get_or_create_singleton(customer, comp_name)
    mseb_instance.customer = customer
    raw_checked = request.POST.get('isChecked', '')
    field_value = str(raw_checked).lower() in ('true', '1', 'on', 'yes')
    setattr(mseb_instance, field_name, field_value)
    setattr(mseb_instance, f"{field_name}_date", completion_datetime)
    mseb_instance.AssignBy = request.user
    mseb_instance.comp_name = comp_name
    mseb_instance.save()

    return JsonResponse({'status': 'success', 'message': 'Record saved successfully'})


def _mseb_post_is_ajax(request):
    """Django 4+ removed request.is_ajax(); jQuery may omit X-Requested-With if misconfigured."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return True
    # Accept explicit MSEB save payload without header (same-origin form posts)
    if request.POST.get('fieldName') and request.POST.get('cust_id') is not None:
        return True
    return False


def _mseb_date_for_json(dt):
    """MSEB *_date fields may be datetime, date, or str — ISO-style string browsers parse reliably."""
    if dt is None:
        return None
    if hasattr(dt, 'isoformat'):
        try:
            return dt.isoformat()
        except (TypeError, ValueError):
            return str(dt)
    s = str(dt).strip()
    # "YYYY-MM-DD HH:MM:SS" → ISO (Safari rejects space separator in Date.parse)
    m = re.match(r'^(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})(\.\d+)?', s)
    if m:
        return f'{m.group(1)}T{m.group(2)}{m.group(3) or ""}'
    return s


def _mseb_tracking_steps_payload(customer, mseb_data):
    """Ordered steps for timeline JSON (matches former MSEB_tracking field order)."""
    if not mseb_data:
        return []
    cl = int(customer.current_load or 0)
    ls = int(customer.loadsancution or 0)
    if cl == ls:
        order = [
            ('net_meter', 'Net Metering'),
            ('flexibility', 'Technical Feasibility'),
            ('approval', 'Approval'),
            ('meter_testing', 'Meter Testing'),
            ('agreement', 'NetMeter Agreement.'),
            ('release', 'Meter Release'),
            ('installation_date', 'Meter Installation Date'),
        ]
    else:
        order = [
            ('load_extension', 'Load Extension'),
            ('flisibility', 'Off-Line Feasibility'),
            ('quotation', 'Firm Quotation Gen.'),
            ('sent_to_bill', 'Sent to Bill'),
            ('net_meter', 'Net Metering'),
            ('flexibility', 'Technical Feasibility'),
            ('approval', 'Approval'),
            ('meter_testing', 'Meter Testing'),
            ('agreement', 'NetMeter Agreement.'),
            ('release', 'Meter Release'),
            ('installation_date', 'Meter Installation Date'),
        ]
    out = []
    for field, label in order:
        val = getattr(mseb_data, field, False)
        dt = getattr(mseb_data, f'{field}_date', None)
        out.append({
            'field': field,
            'label': label,
            'value': bool(val),
            'date': _mseb_date_for_json(dt),
        })
    return out


@login_required(login_url='user-login')
def mseb_customer_list(request):
    """JSON list of customers for unified MSEB page mode (New / In Progress / Update / Completed)."""
    mode = request.GET.get('mode', 'new')
    rows = list(get_mseb_customers_for_mode(mode))
    return JsonResponse({
        'mode': mode,
        'customers': [[r[0], r[1], r[2] or ''] for r in rows],
    })


@login_required(login_url='user-login')
def mseb_tracking_json(request):
    """Merged MSEB tracking timeline as JSON for the unified MSEB page."""
    cust_id = request.GET.get('cust_id')
    if not cust_id:
        return JsonResponse({'error': 'cust_id required'}, status=400)
    customer = get_object_or_404(Customer, Cust_id=cust_id)
    mseb_data = MSEB.objects.filter(customer=customer).first()
    return JsonResponse({
        'consumer': customer.Comp_name or '',
        'steps': _mseb_tracking_steps_payload(customer, mseb_data),
    })


@login_required(login_url='user-login')
def mseb_view(request):
    if request.method == 'POST' and _mseb_post_is_ajax(request):
        return _mseb_step_save_post(request)
    mode = request.GET.get('mode', 'new')
    customers = list(get_mseb_customers_for_mode(mode))
    return render(request, 'customer/MSEB.html', {
        'customers': customers,
        'mseb_initial_mode': mode,
    })


@login_required(login_url='user-login')
def complete_mseb_view(request):
    if request.method == 'POST' and _mseb_post_is_ajax(request):
        return _mseb_step_save_post(request)
    from django.urls import reverse
    return redirect(f"{reverse('customer-MSEB')}?mode=completed")


import json
# import datetime
import pytz
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import Lower, Trim
from .models import Customer, MSEB
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import MSEB, Customer
# import datetime
from django.utils import timezone

from django.http import JsonResponse
import json
from django.shortcuts import get_object_or_404
from django.utils import timezone
# import datetime


import json
# import datetime
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.utils import timezone

@login_required(login_url='user-login')
def update_mseb_view(request):
    """Bulk update JSON API; GET redirects to unified MSEB page (Update mode)."""
    if request.method == 'POST' and (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or 'application/json' in (request.content_type or '')
    ):
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        updates = data.get('updates')

        if updates:
            for update in updates:
                cust_id = update.get('cust_id')
                field_name = update.get('fieldName')
                completion_date = update.get('createdAt')

                if not field_name or field_name not in MSEB_STEP_FIELD_NAMES:
                    return JsonResponse(
                        {'status': 'error', 'message': 'Invalid or missing field name'},
                        status=400,
                    )

                customer = get_object_or_404(Customer, Cust_id=cust_id)
                comp_name = customer.Comp_name

                if completion_date:
                    completion_datetime = timezone.make_aware(
                        datetime.strptime(completion_date, '%Y-%m-%d'),
                        timezone=timezone.get_current_timezone()
                    )
                else:
                    completion_datetime = timezone.now()

                mseb_instance, created = _mseb_get_or_create_singleton(customer, comp_name)
                mseb_instance.customer = customer
                setattr(mseb_instance, field_name, True)
                setattr(mseb_instance, f"{field_name}_date", completion_datetime)
                mseb_instance.comp_name = comp_name
                mseb_instance.AssignBy = request.user
                mseb_instance.save()

            return JsonResponse({'status': 'success', 'message': 'Records saved successfully'})
        return JsonResponse({'status': 'error', 'message': 'No data received for updates'})

    from django.urls import reverse
    return redirect(f"{reverse('customer-MSEB')}?mode=update")


from django.shortcuts import render

from django.http import JsonResponse

from django.http import JsonResponse
from .models import MSEB, Customer

def _mseb_field_value_as_bool(raw):
    """Normalize DB value to JSON boolean (handles bool, 0/1, legacy strings, PG bytea)."""
    if raw is None:
        return False
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)):
        return raw != 0
    if isinstance(raw, (bytes, bytearray, memoryview)):
        if len(raw) == 0:
            return False
        return raw[0] not in (0, ord('0'), ord('f'), ord('F'))
    if isinstance(raw, str):
        s = raw.strip().lower()
        if s in ('false', '0', 'f', 'no', ''):
            return False
        return s in ('true', '1', 't', 'yes')
    return bool(raw)


def get_mseb_data(request):
    # comp_name = request.GET.get('comp_name')
    # mseb_instance = MSEB.objects.filter(comp_name=comp_name).first()
    # customer = Customer.objects.get(Comp_name=comp_name)
    cust_id = request.GET.get('cust_id')
    mseb_instance = MSEB.objects.filter(customer_id=cust_id).first()
    customer = Customer.objects.get(Cust_id=cust_id)
    if mseb_instance:
        mseb_data = {}

        current_load = customer.current_load
        loadsancution = customer.loadsancution

        # Add current_load and loadsancution to mseb_data (must match JS getMsebFieldsOrder)
        mseb_data['current_load'] = current_load
        mseb_data['loadsancution'] = loadsancution

        # Same rule as template: parseInt equality (handles None / type mismatch)
        try:
            loads_equal = int(current_load or 0) == int(loadsancution or 0)
        except (TypeError, ValueError):
            loads_equal = current_load == loadsancution

        if loads_equal:
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
            date_value = getattr(mseb_instance, created_at_field, None)
            formatted_date = _mseb_date_for_json(date_value) if date_value else None

            raw_bool = getattr(mseb_instance, field, None)
            mseb_data[field_name] = {
                'value': _mseb_field_value_as_bool(raw_bool),
                'created_at': formatted_date,
            }


        return JsonResponse(mseb_data)
    else:
        return JsonResponse({'error': 'No data found for the selected company', 'current_load': customer.current_load, 'loadsancution': customer.loadsancution})



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
    current_date = datetime.now().date()

    remaining_days_inv_warranty = None  # Initialize with None
    remaining_days_sol_warranty = None
    remaining_days_com_warranty = None
    installation_date1 = None  # Initialize with None

    items = []
    solar_items = []
    inverter_items = []
    replace_items = []
    waterpump_items = []
    solar_panel_total_quantity = 0
    solar_panel_quantity_by_wattage = []
    unique_wattages = []
    inverter_wattages = []
    inverter_panel_quantity_by_wattage = []
    inverter_panel_total_quantity = 0
    replace_wattages = []
    replace_panel_quantity_by_wattage = []
    replace_panel_total_quantity = 0
    waterpump_wattages = []
    waterpump_panel_quantity_by_wattage = []
    waterpump_panel_total_quantity = 0
    user_record = Customer.objects.get(Cust_id=Cust_id)
    selected_company = user_record.new_customer
    items = BarcodeImage.objects.filter(AssignTo=selected_company)
    items_pump = SolarPump.objects.filter(AssignTo=selected_company)
    solar_items = items.filter(product_name='SolarPanel')
    inverter_items = items.filter(product_name='Inverter')
    replace_items = items.filter(product_name='Replace')
    waterpump_items = items_pump.filter(item_type='Water Pump')
    solar_panel_total_quantity = solar_items.count()
    solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
    inverter_panel_total_quantity = inverter_items.count()
    inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
    replace_panel_total_quantity = replace_items.count()
    replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
    waterpump_panel_total_quantity = waterpump_items.count()
    waterpump_panel_quantity_by_wattage = waterpump_items.values('pump_hp').annotate(total_quantity=Count('id'))


    unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
    inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
    replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
    waterpump_wattages = {item['pump_hp'] for item in waterpump_panel_quantity_by_wattage}

    # Generation Meter Details
    user_record = Customer.objects.get(Cust_id=Cust_id)
    selected_comp_name = user_record.Comp_name
    # print(selected_comp_name)

    meters_records = Meters.objects.filter(comp_name=selected_comp_name)
    generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
    generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)

    # CODE FOR MSEB Status — select_related so Assoc_Assign / Engg_Assign / profile show on template
    customer = get_object_or_404(
        Customer.objects.select_related(
            "Assoc_Assign",
            "Assoc_Assign__profile",
            "Engg_Assign",
            "Engg_Assign__profile",
            "Emp_id",
            "Emp_id__profile",
            "new_customer",
        ),
        Cust_id=Cust_id,
    )
    mseb_data = MSEB.objects.filter(customer=customer).first()
    records = mseb_data
    
    # Initialize variables
    installation_date1 = False
    progress_data = {}
    progress_warranty = {}
    remaining_days_inv_warranty = None
    current_date = date.today()

    if mseb_data is not None:
        # Check if installation_date_date exists (the actual date field) to determine if MSEB is completed
        # MSEB is completed if either the boolean field is True OR the date field is not None
        # Prioritize checking installation_date_date first, as it's the actual completion indicator
        installation_date1 = (mseb_data.installation_date_date is not None) or bool(mseb_data.installation_date)
        progress_data = {}
        try:
            current_load = int(customer.current_load) if customer.current_load is not None else 0
        except ValueError:
            current_load = 0

        try:
            loadsancution = int(customer.loadsancution) if customer.loadsancution is not None else 0
        except ValueError:
            loadsancution = 0

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

        # Helper function to safely convert date values
        def safe_get_date(date_value):
            """Safely convert date value to date object or return None"""
            if date_value is None:
                return None
            if isinstance(date_value, str):
                try:
                    return datetime.strptime(date_value, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        return datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').date()
                    except ValueError:
                        return None
            elif hasattr(date_value, 'date'):
                return date_value.date()
            elif isinstance(date_value, date):
                return date_value
            else:
                return None
        
        # Constructing progress data with display names
        # Use getattr to access fields directly instead of __dict__ to handle case-sensitivity
        for field in field_mapping:
            value = getattr(mseb_data, field, None)
            date_value = getattr(mseb_data, f"{field}_date", None)
            # Ensure boolean values are properly converted (handle case where value might be string 'True'/'False')
            if isinstance(value, str):
                value = value.lower() in ('true', '1', 'yes')
            elif value is None:
                value = False
            progress_data[field_mapping[field]] = {
                'value': bool(value),  # Ensure it's a boolean
                'date': safe_get_date(date_value)
            }
        
        # Calculate warranty end dates (outside the loop)
        installation_date = mseb_data.installation_date_date
        if installation_date:
            # Helper function to safely convert installation_date_date to date object
            def get_installation_date_as_date(date_value):
                """Convert installation_date_date to datetime.date, handling both string and datetime objects"""
                if date_value is None:
                    return None
                if isinstance(date_value, str):
                    # Parse string to datetime, then convert to date
                    try:
                        # Use the datetime module's strptime
                        dt = datetime.strptime(date_value, '%Y-%m-%d')
                        return dt.date()
                    except (ValueError, AttributeError):
                        try:
                            dt = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
                            return dt.date()
                        except (ValueError, AttributeError):
                            return None
                elif isinstance(date_value, datetime):
                    # It's a datetime object, convert to date
                    return date_value.date()
                elif isinstance(date_value, date):
                    # It's already a date object
                    return date_value
                else:
                    # For any other type, try to convert if it has a date method
                    # But NEVER call .date() on strings - they have a 'date' attribute but it's not what we want
                    if isinstance(date_value, str):
                        return None  # Already handled above, but double-check
                    try:
                        # Only try .date() if it's definitely not a string
                        if hasattr(date_value, 'date') and callable(getattr(date_value, 'date', None)):
                            # Double-check it's not a string before calling
                            if not isinstance(date_value, str):
                                return date_value.date()
                    except (AttributeError, TypeError):
                        pass
                    return None
            
            installation_date_date = get_installation_date_as_date(mseb_data.installation_date_date)
            
            if installation_date_date:
                inv_warranty_years = customer.inv_warranty
                sol_warranty_years = customer.sol_warranty
                com_warranty_years = customer.com_warranty
                waterpump_warranty_years = customer.pump_warranty

                if inv_warranty_years:
                    inv_warranty_end_date = installation_date_date + timedelta(days=365 * inv_warranty_years) - timedelta(days=1)
                    remaining_days_inv_warranty = (inv_warranty_end_date - current_date).days
                    progress_warranty['Inverter Warranty'] = {
                        'value': True,
                        'date': inv_warranty_end_date,
                        'remaining_days': remaining_days_inv_warranty
                    }

                if sol_warranty_years:
                    sol_warranty_end_date = installation_date_date + timedelta(days=365 * sol_warranty_years) - timedelta(days=1)
                    remaining_days_sol_warranty = (sol_warranty_end_date - current_date).days
                    progress_warranty['Solar Module Warranty'] = {
                        'value': True,
                        'date': sol_warranty_end_date,
                        'remaining_days': remaining_days_sol_warranty
                    }

                if waterpump_warranty_years:
                    waterpump_warranty_end_date = installation_date_date + timedelta(days=365 * waterpump_warranty_years) - timedelta(days=1)
                    remaining_days_waterpump_warranty = (waterpump_warranty_end_date - current_date).days
                    progress_warranty['Solar Pump Warranty'] = {
                        'value': True,
                        'date': waterpump_warranty_end_date,
                        'remaining_days': remaining_days_waterpump_warranty
                    }

                if com_warranty_years:
                    com_warranty_end_date = installation_date_date + timedelta(days=365 * com_warranty_years) - timedelta(days=1)
                    remaining_days_com_warranty = (com_warranty_end_date - current_date).days + 1
                    progress_warranty['O & M Warranty'] = {
                        'value': True,
                        'date': com_warranty_end_date,
                        'remaining_days': remaining_days_com_warranty
                    }




    else:
        records = None
        progress_data = {}


    return render(request, 'customer/customer_updatepage.html',
                  {'companies': companies, 'product_names': product_names, 'items': items,
                   'solar_items': solar_items, 'inverter_items': inverter_items, 'replace_items': replace_items,
                   'waterpump_items': waterpump_items,
                   'solar_panel_total_quantity': solar_panel_total_quantity,
                   'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
                   'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
                   'inverter_panel_total_quantity': inverter_panel_total_quantity,
                   'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,
                   'replace_panel_total_quantity': replace_panel_total_quantity,
                   'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
                   'replace_wattages': replace_wattages,
                   'waterpump_panel_total_quantity': waterpump_panel_total_quantity,
                   'waterpump_panel_quantity_by_wattage': waterpump_panel_quantity_by_wattage,
                   'waterpump_wattages': waterpump_wattages,
                   'notification1': notification1,
                   'count1': count1,
                   'user_record': user_record,
                   'meters_records': meters_records,
                   'generation_meter_records': generation_meter_records,
                   'generation_ct_records': generation_ct_records,
                   'selected_comp_name': selected_comp_name,
                   'customer': customer, 'progress_data': progress_data, 'records': records,
                   'progress_warranty': progress_warranty,
                   'mseb_installation_date': str(installation_date1).lower(),  # Convert to lowercase string for template JavaScript
                   'remaining_days_inv_warranty': remaining_days_inv_warranty,

                   })


from django.shortcuts import redirect

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

from django.shortcuts import render
from .forms import CustomerSelectForm
from .models import MSEB

from django.shortcuts import render, get_object_or_404
from .models import MSEB
from .forms import CustomerSelectForm

from django.shortcuts import render, get_object_or_404
from .forms import CustomerSelectForm
from .models import MSEB


from django.core.serializers.json import DjangoJSONEncoder
import json


@login_required(login_url='user-login')
def MSEB_tracking_view(request, customer_id):
    """Legacy URL: open unified MSEB page with consumer pre-selected (timeline loads on Fetch)."""
    from django.urls import reverse
    return redirect(f"{reverse('customer-MSEB')}?cust_id={customer_id}")


from django.shortcuts import render, redirect
from .forms import UpdateCompanyNameForm
from .models import Customer, Meters, GenerationMeter, MSEB, InspectionDetail
from detect_barcodes.models import BarcodeImage
from firereport.models import Firereport
from django.utils.safestring import mark_safe


@login_required(login_url='user-login')
def update_company_name(request):
    if request.method == 'POST':
        form = UpdateCompanyNameForm(request.POST)
        if form.is_valid():
            selected_customer = form.cleaned_data['comp_name']
            new_comp_name = form.cleaned_data['new_comp_name']

            # Update the Comp_name in Customer table
            selected_customer.Comp_name = new_comp_name
            selected_customer.save()

            # Update Comp_name in related tables
            Meters.objects.filter(customer=selected_customer).update(comp_name=new_comp_name)
            GenerationMeter.objects.filter(customer=selected_customer).update(comp_name=new_comp_name)
            MSEB.objects.filter(customer=selected_customer).update(comp_name=new_comp_name)
            InspectionDetail.objects.filter(customer=selected_customer).update(company_name=new_comp_name)
            BarcodeImage.objects.filter(AssignTo=selected_customer.new_customer).update(company=new_comp_name)

            Controller.objects.filter(consumer_id=selected_customer).update(consumer=new_comp_name)
            SolarPump.objects.filter(consumer_id=selected_customer).update(consumer=new_comp_name)
            Result.objects.filter(consumer_id=selected_customer).update(consumer=new_comp_name)

            Firereport.objects.filter(Account_id=selected_customer.new_customer_id).update(FullName=new_comp_name)
            # Display a success message with the new company name in bold
            message = f'Company Name {new_comp_name} updated successfully.'
            messages.success(request, mark_safe(message))

        return redirect('customer-update_company_name')  # Redirect to a success page after saving the record

    else:
        form = UpdateCompanyNameForm()

    return render(request, 'customer/update_company_name.html', {'form': form})


from django.shortcuts import render, get_object_or_404
from .models import Meters, GenerationMeter, Customer


@login_required(login_url='user-login')
def search_barcode(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    meters = None
    customer = None
    matched_field = None
    generation_meter = None

    if request.method == 'POST':
        barcode_value = request.POST.get('barcode_value', '')

        # Check Meters table for serial_no or transformer_serial_number match
        meters = Meters.objects.filter(
            serial_no=barcode_value
        ).first() or Meters.objects.filter(
            transformer_serial_number=barcode_value
        ).first()

        if meters:
            matched_field = 'serial_no' if meters.serial_no == barcode_value else 'transformer_serial_number'

        # If not found in Meters, check GenerationMeter table
        if not meters:
            generation_meter = GenerationMeter.objects.filter(
                serial_no=barcode_value
            ).first() or GenerationMeter.objects.filter(
                CT_serial_no=barcode_value
            ).first()

            if generation_meter:
                matched_field = 'serial_no' if generation_meter.serial_no == barcode_value else 'CT_serial_no'

        # If we found a meter, fetch the related customer
        if meters or generation_meter:
            meter_obj = meters or generation_meter
            try:
                customer = Customer.objects.get(Cust_id=meter_obj.customer_id)
            except Customer.DoesNotExist:
                customer = None

    return render(request, 'customer/search_results.html', {
        'meters': meters,
        'generation_meter': generation_meter,
        'customer': customer,
        'count1': count1,
        'notification1': notification1,
        'matched_field': matched_field,
    })


from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import Customer, SolarPump
from .forms import SolarPumpForm
from django.contrib import messages

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import Customer, SolarPump, Result, Controller
from .forms import SolarPumpForm, ControllerForm
from django.contrib import messages



from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.shortcuts import render
import json


from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Count
from .models import Customer, SolarPump, Result
from .forms import SolarPumpForm
from django.contrib.auth.decorators import login_required

@login_required(login_url='user-login')
def solar_pump_entry(request):
    all_customers = Customer.objects.filter(project_type='Water Pump')
    filtered_customers = []
    exact_match_customers = []

    for customer in all_customers:
        existing_count = SolarPump.objects.filter(consumer_id=customer).count()
        if customer.pump_qunt > existing_count:
            filtered_customers.append(customer)
        elif customer.pump_qunt == existing_count:
            exact_match_customers.append(customer)

    customers = filtered_customers  # Default dropdown list
    solar_pumps = None
    form = None
    selected_customer = None
    error = None
    allow_new_records = False
    solar_pumps_list = None  # For List view

    # Determine entity type from POST or default to "customer"
    entity_type = request.POST.get("entity_type", "customer")

    if request.method == 'POST':
        if entity_type == "list":
            # For List view, aggregate solar pump records by company
            # solar_pumps_list = SolarPump.objects.values('consumer_id', 'consumer__Comp_name').annotate(total=Count('id'))
            solar_pumps_list = SolarPump.objects.values('consumer_id', 'consumer_id__Comp_name').annotate(
                total=Count('id'))

        elif 'comp_name' in request.POST:  # Handling company selection
            comp_id = request.POST.get('comp_name')
            if comp_id:
                try:
                    selected_customer = Customer.objects.get(Cust_id=int(comp_id))
                    solar_pumps = SolarPump.objects.filter(consumer_id=selected_customer)
                    if selected_customer.pump_qunt > solar_pumps.count():
                        allow_new_records = True
                        form = SolarPumpForm()
                        customers = filtered_customers
                    else:
                        allow_new_records = False
                        customers = exact_match_customers
                except (ObjectDoesNotExist, ValueError):
                    error = 'Invalid company selected. Please try again.'
            else:
                error = 'No company selected. Please select a company.'
        elif 'serial_no[]' in request.POST:  # Handling new solar pump entries via AJAX
            comp_id = request.POST.get('consumer_id')
            if comp_id:
                try:
                    # Convert comp_id to integer, handle ValueError if conversion fails
                    try:
                        comp_id_int = int(comp_id)
                    except ValueError:
                        return JsonResponse({
                            "success": False,
                            "error": f"Invalid company ID format: '{comp_id}'. Please select a valid company."
                        })
                    
                    # Get the customer object
                    selected_customer = Customer.objects.get(Cust_id=comp_id_int)
                    
                    # Fix: consumer_id is a ForeignKey, so use the Customer object, not Cust_id
                    solar_pumps = SolarPump.objects.filter(consumer_id=selected_customer)
                    
                    if selected_customer.pump_qunt > solar_pumps.count():
                        # Check if user is authenticated (additional safety check)
                        if not request.user.is_authenticated:
                            return JsonResponse({
                                "success": False,
                                "error": "You must be logged in to perform this action."
                            })
                        
                        serial_no = request.POST.getlist('serial_no[]')
                        model_numbers = request.POST.getlist('pump_company[]')
                        capacities = request.POST.getlist('pump_hp[]')
                        # Use individual save() instead of bulk_create to ensure database generates id
                        # bulk_create doesn't always respect database defaults for primary keys
                        for i in range(len(serial_no)):
                            if serial_no[i]:
                                SolarPump.objects.create(
                                    consumer_id=selected_customer,
                                    serial_no=serial_no[i],
                                    pump_company=model_numbers[i] if i < len(model_numbers) else "",
                                    pump_hp=capacities[i] if i < len(capacities) else "",
                                    consumer=selected_customer.Comp_name,
                                    item_type='Water Pump',
                                    AssignTo=selected_customer.new_customer,
                                    AssignBy=request.user,  # Now safe because @login_required ensures authenticated user
                                    created_at=timezone.now()
                                )
                        # Fix: consumer_id is a ForeignKey, so use the Customer object, not Cust_id
                        total_pumps = SolarPump.objects.filter(consumer_id=selected_customer).count()
                        result_entry, created = Result.objects.get_or_create(
                            consumer_id=selected_customer,
                            defaults={
                                'consumer': selected_customer.Comp_name,
                                'AssignTo': request.user,
                            }
                        )
                        result_entry.solar_pump = (total_pumps == selected_customer.pump_qunt)
                        result_entry.save()
                        # Fix: consumer_id is a ForeignKey, so use the Customer object, not Cust_id
                        updated_solar_pumps = list(SolarPump.objects.filter(consumer_id=selected_customer).values())
                        return JsonResponse({
                            "success": True,
                            "message": "Solar pump entries saved successfully!",
                            "solar_pumps": updated_solar_pumps
                        })
                    else:
                        return JsonResponse({
                            "success": False,
                            "error": "Cannot add more pumps. Maximum limit reached."
                        })
                except Customer.DoesNotExist:
                    return JsonResponse({
                        "success": False,
                        "error": f"Company with ID {comp_id} not found. Please select a valid company."
                    })
                except Exception as e:
                    # Log the actual error for debugging
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error in solar_pump_entry: {str(e)}")
                    return JsonResponse({
                        "success": False,
                        "error": f"An error occurred: {str(e)}"
                    })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "No company ID provided. Please select a company."
                })

    return render(request, 'customer/solar_pump_new.html', {
        'customers': customers,
        'solar_pumps': solar_pumps,
        'form': form,
        'selected_customer': selected_customer,
        'error': error,
        'allow_new_records': allow_new_records,
        "filtered_customers": filtered_customers,
        "exact_match_customers": exact_match_customers,
        "entity_type": entity_type,
        "solar_pumps_list": solar_pumps_list,
    })


@csrf_exempt
def update_solar_pump(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            updates = data.get("updates", [])
            deletes = data.get("deletes", [])
            consumer_id = data.get("consumer_id")  # Should be a number if passed from client

            # Process record updates
            for record in updates:
                pump_id = record.get("id")
                pump_company = record.get("pump_company")
                pump_hp = record.get("pump_hp")
                serial_no = record.get("serial_no")
                pump = SolarPump.objects.get(id=pump_id)
                pump.pump_company = pump_company
                pump.pump_hp = pump_hp
                pump.serial_no = serial_no
                pump.save()

            # Process deletions
            if deletes:
                SolarPump.objects.filter(id__in=deletes).delete()

            # Determine the customer
            if not consumer_id:
                if updates:
                    pump = SolarPump.objects.get(id=updates[0]['id'])
                    # Use the ForeignKey field 'customer' to get the Customer instance
                    customer = pump.consumer_id
                    consumer_id = customer.Cust_id
                else:
                    return JsonResponse({"success": False, "message": "Consumer ID not provided."})
            else:
                customer = Customer.objects.get(Cust_id=consumer_id)

            # Count current SolarPump records for this customer using the customer object
            current_pump_count = SolarPump.objects.filter(consumer_id=customer).count()

            # Compare the count with pump_qunt from the customer table
            solar_pump_status = (current_pump_count == customer.pump_qunt)

            # Update the corresponding Result record's solar_pump field using customer object
            Result.objects.filter(consumer_id=customer).update(solar_pump=solar_pump_status)

            return JsonResponse({"success": True, "message": "Records updated successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method!"})


import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # Use with caution in production!

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import SolarPump, Customer, Result


@require_POST
@csrf_exempt  # Remove this in production if CSRF token is handled properly in AJAX
def delete_solar_pump_records(request):
    try:
        data = json.loads(request.body)
        company_id = data.get('company_id')

        if not company_id:
            return JsonResponse({'success': False, 'error': 'No company_id provided.'})

        # Get the customer
        customer = Customer.objects.filter(Cust_id=company_id).first()
        if not customer:
            return JsonResponse({'success': False, 'error': 'Customer not found.'})

        # Count SolarPump entries before deletion using customer object
        pump_count = SolarPump.objects.filter(consumer_id=customer).count()

        # Delete the SolarPump records using customer object
        deleted_count, _ = SolarPump.objects.filter(consumer_id=customer).delete()

        # Compare and update Result table if condition matched
        if pump_count == customer.pump_qunt:
            Result.objects.filter(consumer_id=customer).update(solar_pump=False)
        else:
            Result.objects.filter(consumer_id=customer).update(solar_pump=False)

        return JsonResponse({
            'success': True,
            # 'message': f'{deleted_count} SolarPump record(s) deleted.',
            'message': f'Successfully deleted {deleted_count} SolarPump records for company id {company_id}.',
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required(login_url='user-login')
def controller_entry(request):
    all_customers = Customer.objects.filter(project_type='Water Pump')

    # Filter customers based on pump_qunt vs. existing records
    filtered_customers = []
    exact_match_customers = []

    for customer in all_customers:
        existing_count = Controller.objects.filter(consumer_id=customer).count()
        if customer.qunt_inv > existing_count:
            filtered_customers.append(customer)
        elif customer.qunt_inv == existing_count:
            exact_match_customers.append(customer)

    customers = filtered_customers  # Default dropdown list

    solar_pumps = None
    form = None
    selected_customer = None
    error = None
    allow_new_records = False

    solar_pumps_list = None  # For List view

    # Determine entity type from POST or default to "customer"
    entity_type = request.POST.get("entity_type", "customer")

    if request.method == 'POST':
        if entity_type == "list":
            # For List view, aggregate solar pump records by company
            # solar_pumps_list = SolarPump.objects.values('consumer_id', 'consumer__Comp_name').annotate(total=Count('id'))
            solar_pumps_list = Controller.objects.values('consumer_id', 'consumer_id__Comp_name').annotate(
                total=Count('id'))

        elif 'comp_name' in request.POST:  # Handling company selection
            comp_id = request.POST.get('comp_name')
            if comp_id:
                try:
                    selected_customer = Customer.objects.get(Cust_id=int(comp_id))
                    solar_pumps = Controller.objects.filter(consumer_id=selected_customer)

                    if selected_customer.qunt_inv > solar_pumps.count():
                        allow_new_records = True
                        form = ControllerForm()
                        customers = filtered_customers
                    else:
                        allow_new_records = False
                        customers = exact_match_customers

                except (ObjectDoesNotExist, ValueError):
                    error = 'Invalid company selected. Please try again.'
            else:
                error = 'No company selected. Please select a company.'

        elif 'serial_no[]' in request.POST:  # Handling new controller entries via AJAX
            comp_id = request.POST.get('consumer_id')
            if comp_id:
                try:
                    # Check if user is authenticated (additional safety check)
                    if not request.user.is_authenticated:
                        return JsonResponse({
                            "success": False,
                            "error": "You must be logged in to perform this action."
                        })
                    
                    # Convert comp_id to integer, handle ValueError if conversion fails
                    try:
                        comp_id_int = int(comp_id)
                    except ValueError:
                        return JsonResponse({
                            "success": False,
                            "error": f"Invalid company ID format: '{comp_id}'. Please select a valid company."
                        })
                    
                    # Get the customer object
                    selected_customer = Customer.objects.get(Cust_id=comp_id_int)
                    solar_pumps = Controller.objects.filter(consumer_id=selected_customer)

                    if selected_customer.qunt_inv > solar_pumps.count():
                        serial_no = request.POST.getlist('serial_no[]')
                        model_numbers = request.POST.getlist('pump_company[]')
                        capacities = request.POST.getlist('pump_hp[]')
                        # Use individual create() instead of bulk_create to ensure database generates id
                        # bulk_create doesn't always respect database defaults for primary keys
                        for i in range(len(serial_no)):
                            if serial_no[i]:
                                Controller.objects.create(
                                    consumer_id=selected_customer,
                                    serial_no=serial_no[i],
                                    pump_company=model_numbers[i] if i < len(model_numbers) else "",
                                    pump_hp=capacities[i] if i < len(capacities) else "",
                                    consumer=selected_customer.Comp_name,
                                    item_type='Controller',
                                    AssignTo=selected_customer.new_customer,
                                    AssignBy=request.user,  # Now safe because @login_required ensures authenticated user
                                    created_at=timezone.now()
                                )

                        # Recalculate counts and update result entry using customer object
                        total_controllers = Controller.objects.filter(consumer_id=selected_customer).count()

                        result_entry, created = Result.objects.get_or_create(
                            consumer_id=selected_customer,
                            defaults={
                                'consumer': selected_customer.Comp_name,
                                'AssignTo': request.user,
                            }
                        )
                        if total_controllers == selected_customer.qunt_inv:
                            result_entry.inverter = 1
                        else:
                            result_entry.inverter = 0
                        result_entry.save()

                        updated_solar_pumps = list(Controller.objects.filter(consumer_id=selected_customer).values())
                        return JsonResponse({
                            "success": True,
                            "message": "Solar Controller entries saved successfully!",
                            "solar_pumps": updated_solar_pumps
                        })
                    else:
                        return JsonResponse({
                            "success": False,
                            "error": "Cannot add more Controller. Maximum limit reached."
                        })

                except Customer.DoesNotExist:
                    return JsonResponse({
                        "success": False,
                        "error": f"Company with ID {comp_id} not found. Please select a valid company."
                    })
                except Exception as e:
                    # Log the actual error for debugging
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error in controller_entry: {str(e)}")
                    return JsonResponse({
                        "success": False,
                        "error": f"An error occurred: {str(e)}"
                    })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "No company ID provided. Please select a company."
                })

    return render(request, 'customer/controller_new.html', {
        'customers': customers,
        'solar_pumps': solar_pumps,
        'form': form,
        'selected_customer': selected_customer,
        'error': error,
        'allow_new_records': allow_new_records,
        "filtered_customers": filtered_customers,
        "exact_match_customers": exact_match_customers,
        "entity_type": entity_type,
        "solar_pumps_list": solar_pumps_list,
    })


@csrf_exempt
def update_controller(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            updates = data.get("updates", [])
            deletes = data.get("deletes", [])
            consumer_id = data.get("consumer_id")  # Should be a number if passed from client

            # Process record updates
            for record in updates:
                pump_id = record.get("id")
                pump_company = record.get("pump_company")
                pump_hp = record.get("pump_hp")
                serial_no = record.get("serial_no")
                pump = Controller.objects.get(id=pump_id)
                pump.pump_company = pump_company
                pump.pump_hp = pump_hp
                pump.serial_no = serial_no
                pump.save()

            # Process deletions
            if deletes:
                Controller.objects.filter(id__in=deletes).delete()

            # Determine the customer
            if not consumer_id:
                if updates:
                    pump = Controller.objects.get(id=updates[0]['id'])
                    # Using the ForeignKey field to get the Customer instance
                    customer = pump.consumer_id
                    consumer_id = customer.Cust_id
                else:
                    return JsonResponse({"success": False, "message": "Consumer ID not provided."})
            else:
                customer = Customer.objects.get(Cust_id=consumer_id)

            # Count current Controller records (for qunt_inv comparison) using customer object
            current_controller_count = Controller.objects.filter(consumer_id=customer).count()

            # Determine solar pump status:
            # Set status to 1 only if both conditions are met; otherwise, 0.
            if current_controller_count == customer.qunt_inv:
                solar_pump_status = 1
            else:
                solar_pump_status = 0

            # Update the corresponding Result record's solar_pump field using customer object
            Result.objects.filter(consumer_id=customer).update(inverter=solar_pump_status)

            return JsonResponse({"success": True, "message": "Records updated successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method!"})



@require_POST
@csrf_exempt  # Remove this in production if CSRF token is handled properly in AJAX
def delete_controller_records(request):
    try:
        data = json.loads(request.body)
        company_id = data.get('company_id')

        if not company_id:
            return JsonResponse({'success': False, 'error': 'No company_id provided.'})

        # Get the customer
        customer = Customer.objects.filter(Cust_id=company_id).first()
        if not customer:
            return JsonResponse({'success': False, 'error': 'Customer not found.'})

        # Count Controller entries before deletion using customer object
        pump_count = Controller.objects.filter(consumer_id=customer).count()

        # Delete the Controller records using customer object
        deleted_count, _ = Controller.objects.filter(consumer_id=customer).delete()

        # Compare and update Result table if condition matched
        if pump_count == customer.qunt_inv:
            Result.objects.filter(consumer_id=customer).update(inverter=False)
        else:
            Result.objects.filter(consumer_id=customer).update(inverter=False)

        return JsonResponse({
            'success': True,
            # 'message': f'{deleted_count} SolarPump record(s) deleted.',
            'message': f'Successfully deleted {deleted_count} Controller records for company id {company_id}.',
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
