import secrets
import string
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from apps.core.models import UserProfile
from apps.control_panel.models import UserRole, Role
# from apps.audit.models import AuditLog  # if exists
from apps.control_panel.models import AuditLog
from django.conf import settings


def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))
#
# def create_organization_user(organization, created_by, user_data, role, send_email=True, manual_password=None):
#     """
#     Create a user within an organization, assign role, and send welcome email.
#     user_data: dict with keys first_name, last_name, email, phone, title, department, is_active.
#     """
#     # 1. Create Django User
#     username = user_data['email']  # or generate from email
#     user = User.objects.create_user(
#         username=username,
#         email=user_data['email'],
#         first_name=user_data['first_name'],
#         last_name=user_data['last_name'],
#         is_active=user_data.get('is_active', True)
#     )
#
#     # 2. Set password
#     if manual_password:
#         user.set_password(manual_password)
#         user.save()
#         password_plain = manual_password
#     else:
#         password_plain = generate_random_password()
#         user.set_password(password_plain)
#         user.save()
#
#     # 3. Create UserProfile
#     profile = UserProfile.objects.create(
#         user=user,
#         organization=organization,
#         phone=user_data.get('phone', ''),
#         title=user_data.get('title', ''),
#         department=user_data.get('department', '')
#     )
#
#     # 4. Assign role
#     if role:
#         UserRole.objects.create(user=user, role=role, organization=organization)
#
#     # 5. Audit log
#     AuditLog.objects.create(
#         user=created_by,
#         action='CREATE',
#         content_object=user,
#         object_repr=str(user),
#         changes={'created_user': user.email, 'role': role.name if role else None}
#     )
#
#     # 6. Send welcome email if requested
#     if send_email:
#         # Prepare password reset link (or send plain password? better to send reset)
#         token = default_token_generator.make_token(user)
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         reset_url = f"{settings.SITE_URL}/reset-password/{uid}/{token}/"
#         context = {
#             'user': user,
#             'password': password_plain if not manual_password else None,
#             'reset_url': reset_url,
#             'created_by': created_by.get_full_name(),
#         }
#         html_message = render_to_string('team/emails/welcome_user.html', context)
#         plain_message = strip_tags(html_message)
#         send_mail(
#             subject='Welcome to Solar CRM',
#             message=plain_message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#             html_message=html_message,
#         )
#
#     return user

from django.core.exceptions import ValidationError

def create_organization_user(organization, created_by, user_data, role, send_email=True, manual_password=None):
    """
    Create a user within an organization, enforce user limit, assign role, and send welcome email.
    user_data: dict with keys first_name, last_name, email, phone, title, department, is_active.
    """
    # Check user limit
    current_users = UserProfile.objects.filter(organization=organization).count()
    if current_users >= organization.max_users:
        raise ValidationError(f"User limit reached ({organization.max_users} users). Cannot create new user.")

    # ... rest of the function unchanged ...
    # 1. Create Django User
    username = user_data['email']
    user = User.objects.create_user(
        username=username,
        email=user_data['email'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        is_active=user_data.get('is_active', True)
    )

    # 2. Set password (auto-generated or manual)
    if manual_password:
        user.set_password(manual_password)
        user.save()
        password_plain = manual_password
    else:
        password_plain = generate_random_password()
        user.set_password(password_plain)
        user.save()

    # 3. Create UserProfile
    profile = UserProfile.objects.create(
        user=user,
        organization=organization,
        phone=user_data.get('phone', ''),
        title=user_data.get('title', ''),
        department=user_data.get('department', '')
    )

    # 4. Assign role
    if role:
        UserRole.objects.create(user=user, role=role, organization=organization)

    # 5. Audit log
    AuditLog.objects.create(
        user=created_by,
        action='CREATE',
        content_object=user,
        object_repr=str(user),
        changes={'created_user': user.email, 'role': role.name if role else None}
    )

    # 6. Send welcome email if requested
    if send_email:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.SITE_URL}/reset-password/{uid}/{token}/"
        context = {
            'user': user,
            'password': password_plain if not manual_password else None,
            'reset_url': reset_url,
            'created_by': created_by.get_full_name(),
        }
        html_message = render_to_string('team/emails/welcome_user.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject='Welcome to Solar CRM',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
        )

    return user