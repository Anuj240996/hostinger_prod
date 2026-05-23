from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from django.contrib.auth import get_user, logout, login
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

import customer
import user
from customer.decorators import allowed_users
from customer.models import Customer
from dashboard.models import staff_Notification
from .models import User, Profile
from .forms import CreateUserForm, UserUpdateForm, ProfileUpdateForm, UserLoginForm, PermissionForm
from django.contrib import messages


from .models import *

# Create your views here.

from django.contrib.auth.decorators import login_required
from user.permissions import has_portal_access, has_nav_url_access


@method_decorator([never_cache, ensure_csrf_cookie], name="dispatch")
class StableLoginView(LoginView):
    """
    Login view with anti-cache headers and guaranteed CSRF cookie emission.
    Helps avoid stale-token POST failures across tabs/retries.
    """
    template_name = "user/login.html"
    authentication_form = UserLoginForm


@login_required(login_url="user-login")
def post_login_redirect(request):
    """
    Single landing route after authentication.
    Sends the user to the first portal they are allowed to access.
    """
    u = request.user

    # Superuser -> Admin dashboard
    if getattr(u, "is_superuser", False):
        return redirect("dashboard-index")

    # Vendor user -> Vendor portal
    if hasattr(u, "vendor_account") and has_portal_access(u, "vendor"):
        return redirect("user:vendor-dashboard")

    # Default landing follows Portal Access order below (do not short-circuit associates to
    # Consumer Dashboard—that ignored complaint_dashboard when both portals were granted).

    portal_to_url = [
        ("staff", "dashboard-index1"),
        ("complaint_dashboard", "firereport-dashboard"),
        ("stock_dashboard", "home"),
        ("admin", "dashboard-index"),
        ("customer", "customer-view_all"),
    ]

    for portal_name, url_name in portal_to_url:
        if has_portal_access(u, portal_name) and has_nav_url_access(u, url_name):
            return redirect(url_name)

    for url_name in ("dashboard-index1", "firereport-dashboard", "home", "customer-view_all"):
        if has_nav_url_access(u, url_name):
            return redirect(url_name)

    return redirect("user:no_access")


@login_required(login_url="user-login")
def logout_view(request):
    """
    Logout handler that supports GET (menu link) and POST.

    Django 5+ defaults to POST-only for LogoutView; this project uses many
    `<a href="/logout/">` links, so we provide a safe fallback here.
    """
    # Allow both GET and POST to avoid HTTP 405.
    logout(request)
    try:
        messages.success(request, "Logged out successfully.")
    except Exception:
        pass
    return redirect("user-login")


@login_required(login_url="user-login")
def no_access(request):
    return render(request, "user/no_access.html")


@login_required(login_url="user-login")
def vendor_dashboard(request):
    # Only vendor-linked users may access vendor portal
    if not hasattr(request.user, "vendor_account"):
        messages.error(request, "Vendor portal is only available for vendor accounts.")
        return redirect("user:no_access")

    if not has_portal_access(request.user, "vendor") and not request.user.is_superuser:
        messages.error(request, "Access denied: Vendor dashboard not permitted.")
        return redirect("user:no_access")

    return render(request, "vendor/dashboard.html", {"vendor_account": request.user.vendor_account})


# views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .forms import PDFGenerationForm
from .models import User, Profile

from django.http import HttpResponse
from django.shortcuts import render
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.pdfgen import canvas
from .forms import PDFGenerationForm
from .models import User, Profile
from django.db.models import F



from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO


from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO

from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings


from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

from django.http import HttpResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import render
from .forms import PDFGenerationForm
from .models import User

from django.http import HttpResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import render
from .forms import PDFGenerationForm
from .models import User
from django.db.models import Q

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
from django.db.models import Q


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.http import HttpResponse
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.http import HttpResponse
from io import BytesIO

from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from django.db.models import Q
from .models import User  # Import your User model here

from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from django.db.models import Q
from .models import User  # Import your User model here


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.http import HttpResponse
from io import BytesIO


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, Frame, Image
from reportlab.lib import units
from django.http import HttpResponse
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, Frame, Image
from reportlab.lib import units
from django.http import HttpResponse
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, PageBreak, Image
from reportlab.lib import units
from django.http import HttpResponse
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, PageBreak, Frame, Image
from reportlab.lib import units
from django.http import HttpResponse
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, PageBreak, Image, Frame
from reportlab.lib import units
from django.http import HttpResponse
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, PageBreak, Image, Frame
from reportlab.lib import units
from django.http import HttpResponse
from io import BytesIO


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, Frame, Flowable, Spacer
from reportlab.lib import colors
from reportlab.platypus import Image
from django.http import HttpResponse
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.platypus import Image
from django.http import HttpResponse
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.platypus import Image, PageBreak
from django.http import HttpResponse
from io import BytesIO
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet


from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Spacer, Paragraph
from datetime import datetime

@login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])

def generate_pdf(request, user_fields, profile_fields, data, logo_path, top_margin_height=0.25, user_type_filter=""):
    buffer = BytesIO()

    # Determine the page size based on the number of fields
    if len(user_fields) + len(profile_fields) > 4:
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
    if user_type_filter == "all":
        caption_text = "List Type: All Employee List"
    elif user_type_filter == "superuser":
        caption_text = "List Type: Admin List"
    elif user_type_filter == "staff":
        caption_text = "List Type: Staff List"
    elif user_type_filter == "active":
        caption_text = "List Type: Consumer List"
    else:
        caption_text = "Unknown List"  # Add a default caption for unknown options

    caption = Paragraph(caption_text, caption_style)

    # Create table data for all user data
    table_data = [['Sr No', 'Emp ID'] + user_fields + profile_fields]

    for index, user_data in enumerate(data, start=1):
        row = [index, user_data['user_fields'].get('ID')]

        row.extend([user_data['user_fields'].get(field, "") for field in user_fields if field != 'ID'])
        row.extend([user_data['profile_fields'].get(field, "") for field in profile_fields if field != 'customer_id'])
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
    response['Content-Disposition'] = f'attachment; filename ={user_type_filter}_pdf.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response


@login_required(login_url='user-login')
# @allowed_users(allowed_roles=['Admin'])
def emp_pdf(request):
    if request.method == 'POST':
        form = PDFGenerationForm(request.POST)
        if form.is_valid():
            user_type_filter = request.POST.get('userType')

            # Define the base queryset
            base_queryset = User.objects.all()

            # Apply filters based on the selected user type
            if user_type_filter == 'superuser':
                base_queryset = base_queryset.filter(Q(is_superuser=True) & Q(is_staff=True) & Q(is_active=True) & Q(groups=2))
            elif user_type_filter == 'staff':
                base_queryset = base_queryset.filter(Q(is_superuser=False) & Q(is_staff=True) & Q(is_active=True) & Q(groups=2))
            elif user_type_filter == 'active':
                base_queryset = base_queryset.filter(Q(is_superuser=False) & Q(is_staff=False) & Q(is_active=True) & Q(groups=2))
            elif user_type_filter == 'all':
               # base_queryset = base_queryset.filter((Q(is_superuser=True) & Q(is_staff=True) & Q(is_active=True))&(Q(is_superuser=False) & Q(is_staff=True) & Q(is_active=True)))
               base_queryset = base_queryset.filter(
                                                        (Q(is_superuser=True) & Q(is_active=True) & Q(groups=2)) |
                                                        (Q(is_staff=True) & Q(is_active=True) & Q(groups=2))
                                                    )

            selected_user_fields = form.cleaned_data['user_fields']
            selected_profile_fields = form.cleaned_data['profile_fields']

            # Check if at least one field from either User or Profile is selected
            if not (selected_user_fields or selected_profile_fields):
                return HttpResponse("Please select at least one field from User or Profile to generate the PDF.")

            # Fetch the filtered users based on the selected user type
            users = base_queryset

            # Define custom field names
            field_display_names = {
                'email': 'Email',
                'username': 'Username',
                'id': 'ID',  # Map 'id' field to 'ID'
                'workphone': 'Contact No',
                'bg': 'Blood Group',
                'DOB': 'Date of Birth',
                'designation': 'Designation',
                'department': 'Department',
                'address': 'Address',
                'city': 'City',
                'taluka': 'Taluka',
                'district': 'District',
                # Add more mappings as needed
            }

            custom_user_fields = ['Full Name'] if 'full_name' in selected_user_fields else []

            for field in selected_user_fields:
                if field in field_display_names and field != 'full_name':
                    custom_user_fields.append(field_display_names[field])

            custom_profile_fields = [field_display_names.get(field, field) for field in selected_profile_fields]

            data = []
            for user in users:
                user_profile = user.profile if hasattr(user, 'profile') else None
                #print(f'User ID: {user.id}, Customer ID: {user_profile.customer_id if user_profile else "N/A"}')

                #user_profile = user.profile if hasattr(user, 'profile') else None
                full_name = f"{user.first_name} {user.last_name}" if 'full_name' in selected_user_fields else ""
                user_fields_data = {
                    'ID': user_profile.customer_id if user_profile else '',  # Access 'customer_id' from profile
                    'Full Name': full_name,
                }
                user_fields_data.update({field_display_names.get(field, field): getattr(user, field, "") for field in selected_user_fields if field != 'full_name'})
                profile_fields_data = {field_display_names.get(field, field): getattr(user_profile, field, "") for field in selected_profile_fields} if user_profile else {}
                user_data = {
                    'user_fields': user_fields_data,
                    'profile_fields': profile_fields_data,
                }
                data.append(user_data)
            logo_path = "static/images/dblogo2001.png"  # Replace with the actual path to your logo image
            top_margin_height = 0.25  # Adjust this value as needed

            # Call the PDF generation function with the data
            return generate_pdf(request, custom_user_fields, custom_profile_fields, data, logo_path, top_margin_height, user_type_filter)
    else:
        form = PDFGenerationForm()

    return render(request, 'user/edit_pdf.html', {'form': form})


from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login


def register(request):
    if request.method == 'POST':
        # Fetch data submitted in the form
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        password1 = request.POST.get('password2')

        # Perform basic validation, you may need to do more checks as needed

        if password != password1:
            messages.error(request, 'Passwords do not match')
            return redirect('user-login')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already Exist')
            return redirect('user-login')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered')
            return redirect('user-login')

        # Create the user
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email,
                                        password=password)
        user.save()

        # Add the user to the 'Customers' group
        group = Group.objects.get(name='Customers')
        user.groups.add(group)

        # Log the user in after registration
        authenticated_user = authenticate(username=username, password=password)
        login(request, authenticated_user)

        # Redirect to a success page or any other page after successful registration
        messages.success(request, 'You have been successfully registered!')
        return redirect('user-login')  # Change 'success-page' to the appropriate URL

    return render(request, 'user/login.html')


@login_required(login_url='user-login')

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
@permission_required('auth.change_user', raise_exception=True)
def add(request):
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(request.POST.get('password1'))
            is_associate = form.cleaned_data.get('is_associate')
            # Associate users must be staff as requested.
            user.is_staff = True if is_associate else form.cleaned_data.get('is_staff', True)
            user.is_active = True
            user.save()

            # Add the user to the 'Customers' group
            group = Group.objects.get(name='Customers')
            user.groups.add(group)

            if form.cleaned_data.get('is_superuser'):
                # If 'is_superuser' is checked, also add to the 'Admin' group
                admin_group = Group.objects.get(name='Admin')
                user.groups.add(admin_group)
            if is_associate:
                associate_group, _ = Group.objects.get_or_create(name='Associate')
                user.groups.add(associate_group)

            username = form.cleaned_data.get('username')
            messages.success(request, f'{username} Account Created Successfully!!')
            return redirect('user-profile-update', user.id)
    else:
        form = CreateUserForm()

    context = {
        'form': form,
        'count1': count1,
        'notification1': notification1,
    }
    return render(request, 'user/add.html', context)


from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Permission
from django.shortcuts import render, redirect
from .forms import PermissionForm

from django.contrib.auth.models import User, Permission
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.forms import ValidationError
import json


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
@csrf_exempt  # Disable CSRF for API requests
def permission_form(request):
    if request.method == 'POST':
        # Check if the request is JSON (API request)
        if request.content_type == 'application/json':
            try:
                # Parse JSON data
                data = json.loads(request.body)
                user_id = data.get('user_id')
                permissions = data.get('permissions', [])

                if not user_id or not permissions:
                    return JsonResponse({'success': False, 'message': 'Fail'}, status=400)

                # Fetch user and permissions
                user = User.objects.get(pk=user_id)
                permission_objs = Permission.objects.filter(id__in=permissions)

                # Update user permissions
                user.user_permissions.set(permission_objs)
                return JsonResponse({'success': True, 'message': 'Permissions updated successfully'})

            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'}, status=500)

        # If the request is not JSON, handle it as a regular form submission
        else:
            form = PermissionForm(request.POST)
            if form.is_valid():
                user_id = form.cleaned_data['user']
                permissions = form.cleaned_data['permissions']
                user = User.objects.get(pk=user_id.id)
                user.user_permissions.set(permissions)
                return redirect('user-permission_form')

    else:
        # Handle GET request for standard form rendering
        user_id = request.GET.get('user_id')
        initial_user = User.objects.get(pk=user_id) if user_id else None
        form = PermissionForm(initial={'user': initial_user}, initial_user=initial_user)

    return render(request, 'user/permission_form.html', {'form': form})


def profile(request):
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    user = request.user
    employee = Profile.objects.get(customer=user)
    # Check if the current user is a customer and retrieve their associated object
    try:
        customer = Customer.objects.get(new_customer=user)
    except Customer.DoesNotExist:
        customer = None

    if request.method == "POST":
        old_password = request.POST['oldpassword']
        new_password = request.POST['newpassword']

        # Change the user's password if the old password is correct
        try:
            u = User.objects.get(id=request.user.id)
            if user.check_password(old_password):
                u.set_password(new_password)
                u.save()
                error = "no"
            else:
                error = 'not'
        except User.DoesNotExist:
            error = "yes"

    return render(request, 'user/profile.html', locals())



def edit_profile(request):
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    user = request.user
    employee = Profile.objects.get(customer=user)
    bgs = Profile._meta.get_field('bg').choices

    # Check if the current user is a customer and retrieve their associated object

    try:
        customer = Customer.objects.get(new_customer=user)
    except Customer.DoesNotExist:
        customer = None

    if request.method == "POST":
        em = request.POST.get('email')
        add = request.POST.get('address')
        dob = request.POST.get('DOB')
        ph = request.POST.get('ph')
        bg = request.POST.get('bg')
        city = request.POST.get('city')
        taluka = request.POST.get('taluka')
        district = request.POST.get('district')
        add1 = request.POST.get('address1')
        ph1 = request.POST.get('ph1')
        city1 = request.POST.get('city1')
        state1 = request.POST.get('state1')
        pincode1 = request.POST.get('pincode1')
        image = request.FILES.get('image')

        if image:
            employee.image = image
        if em:
          user.email = em
        if ph:
         employee.workphone = ph
        #employee.bg = bg
        if add:
         employee.address = add
        if city:
         employee.city = city
        if taluka:
         employee.taluka = taluka
        if district:
         employee.district = district

        if dob:
            employee.DOB = dob
        if bg:
            employee.bg = bg

        if customer is not None:
            if ph1:
             customer.phone = ph1
            #employee.bg = bg
            if add1:



             customer.Address = add1
            if city1:
             customer.City = city1
            if state1:
             customer.state = state1
            if pincode1:
             customer.Pincode = pincode1

        try:
            employee.save()
            user.save()
            error="no"
        except:
            error="yes"
    return render(request, 'user/edit_profile.html', locals())


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def profile_update(request,pk):
    error = ""
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    departments = Profile._meta.get_field('department').choices
    designations = Profile._meta.get_field('designation').choices
    bgs = Profile._meta.get_field('bg').choices
    user1 = User.objects.get(id=pk)
    # print(user1)
    employee = Profile.objects.get(customer_id=user1)
    is_associate_user = user1.groups.filter(name='Associate').exists()
    # print(user1)
    if request.method == "POST":
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        em = request.POST['email']
        add = request.POST['address']
        dob = request.POST['DOB']
        jod = request.POST['jod']
        dept = request.POST.get('dept')
        image = request.FILES.get('image')
        ph = request.POST['ph']
        desig = request.POST.get('desig')

        bg = request.POST.get('bg')
        city = request.POST['city']
        taluka = request.POST['taluka']
        district = request.POST['district']
        pg = request.POST['pg']
        institution = request.POST['institution']
        yop = request.POST['yop']
        specili = request.POST['specili']
        name = request.POST['name']
        phone = request.POST['phone']
        emremail = request.POST['emremail']
        emraddress = request.POST['emraddress']


        user1.first_name = fn
        user1.last_name = ln
        user1.email = em

        #employee.department = dept
        employee.phone = phone
        #employee.designation = desig
        employee.address = add

        #employee.bg = bg
        employee.city = city
        employee.taluka = taluka
        employee.district = district
        employee.pg = pg
        employee.institution = institution
        employee.specili = specili
        employee.name = name
        employee.workphone = ph
        employee.email = emremail
        employee.emraddress = emraddress

        if dept:
            employee.department = dept
        if desig:
            employee.designation = desig
        # Associate users must persist Associate values in DB.
        if is_associate_user:
            employee.department = 'Associate'
            employee.designation = 'Associate'
        if bg:
            employee.bg = bg
        if yop:
            employee.yop = yop

        if jod:
            user1.date_joined = jod

        if dob:
            employee.DOB = dob
        if image:
            employee.image = image

        try:
            user = get_user(request)
            employee.last_updated_by = user.id
            # print(user)
            employee.save()
            user1.save()
            logout(request)
            login(request, user)
            error="no"
        except:
            error="yes"
    return render(request, 'user/profile_update.html', locals())

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def profile_updatepage(request,pk):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    user1 = User.objects.get(id=pk)
    employee = Profile.objects.get(customer_id=pk)
    return render(request, 'user/profile_updatepage.html', locals())

from django.contrib.auth import views as auth_views
