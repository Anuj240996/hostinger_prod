# # from django.db import models
# # from django.contrib.auth.models import User
# # from django.utils import timezone
# # import uuid
# #
# #
# # class TimeStampedModel(models.Model):
# #     """
# #     An abstract base class model that provides self-updating
# #     'created' and 'modified' fields.
# #     """
# #     created = models.DateTimeField(auto_now_add=True)
# #     modified = models.DateTimeField(auto_now=True)
# #
# #     class Meta:
# #         abstract = True
# #
# #
# # class Organization(TimeStampedModel):
# #     name = models.CharField(max_length=200)
# #     address = models.TextField(blank=True)
# #     phone = models.CharField(max_length=20, blank=True)
# #     email = models.EmailField(blank=True)
# #     website = models.URLField(blank=True)
# #     logo = models.ImageField(upload_to='organizations/', blank=True, null=True)
# #
# #     class Meta:
# #         verbose_name = "Organization"
# #         verbose_name_plural = "Organizations"
# #
# #     def __str__(self):
# #         return self.name
# #
# #
# # class Team(TimeStampedModel):
# #     name = models.CharField(max_length=100)
# #     description = models.TextField(blank=True)
# #     members = models.ManyToManyField(User, related_name='teams', blank=True)
# #     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
# #
# #     class Meta:
# #         verbose_name = "Team"
# #         verbose_name_plural = "Teams"
# #
# #     def __str__(self):
# #         return self.name
# #
# #
# # class Notification(TimeStampedModel):
# #     NOTIFICATION_TYPES = (
# #         ('followup', 'Follow-up Due'),
# #         ('lead', 'New Lead'),
# #         ('stage', 'Stage Changed'),
# #         ('quotation', 'Quotation Sent'),
# #         ('survey', 'Survey Scheduled'),
# #         ('revenue', 'Revenue Recorded'),
# #     )
# #
# #     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
# #     notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
# #     title = models.CharField(max_length=200)
# #     message = models.TextField()
# #     link = models.CharField(max_length=500, blank=True)
# #     is_read = models.BooleanField(default=False)
# #     created = models.DateTimeField(auto_now_add=True)
# #
# #     class Meta:
# #         ordering = ['-created']
# #
# #     def __str__(self):
# #         return f"{self.user.username} - {self.title}"
#
#
# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone
# from .utils import get_current_organization
# import uuid
#
# class TimeStampedModel(models.Model):
#     """Abstract base with created/modified timestamps."""
#     created = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         abstract = True
#
# #
# # class Organization(TimeStampedModel):
# #     """Represents a tenant (company)."""
# #     name = models.CharField(max_length=200)
# #     # subdomain = models.SlugField(unique=True)
# #     subdomain = models.CharField(unique=True, default="default")
# #     address = models.TextField(blank=True)
# #     phone = models.CharField(max_length=20, blank=True)
# #     email = models.EmailField(blank=True)
# #     website = models.URLField(blank=True)
# #     logo = models.ImageField(upload_to='organizations/', blank=True, null=True)
# #
# #     class Meta:
# #         verbose_name = "Organization"
# #         verbose_name_plural = "Organizations"
# #
# #     def __str__(self):
# #         return self.name
#
# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone
# from django.core.validators import validate_email
# import uuid
#
# class Organization(models.Model):
#     BUSINESS_TYPES = (
#         ('sole', 'Sole Proprietor'),
#         ('partnership', 'Partnership'),
#         ('llp', 'LLP'),
#         ('pvt', 'Pvt Ltd'),
#         ('ltd', 'Public Ltd'),
#         ('ngo', 'NGO'),
#         ('other', 'Other'),
#     )
#
#     # Step 1 – Business Details
#     legal_name = models.CharField(max_length=200)
#     trade_name = models.CharField(max_length=200, blank=True)
#     business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES)
#     industry = models.CharField(max_length=100, blank=True)
#     gst_number = models.CharField(max_length=50, blank=True)
#     pan_tax_id = models.CharField(max_length=50, blank=True)
#     registration_number = models.CharField(max_length=50, blank=True)
#
#     # Step 2 – Registered Address
#     address_line1 = models.CharField(max_length=255)
#     address_line2 = models.CharField(max_length=255, blank=True)
#     city = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     country = models.CharField(max_length=100)
#     postal_code = models.CharField(max_length=20)
#
#     # Step 3 – Contact & Billing
#     official_email = models.EmailField(unique=True)
#     phone = models.CharField(max_length=20)
#     alternate_phone = models.CharField(max_length=20, blank=True)
#     billing_email = models.EmailField(blank=True)
#     website = models.URLField(blank=True)
#     timezone = models.CharField(max_length=100, default='UTC')
#     currency = models.CharField(max_length=10, default='INR')
#
#
#     # Step 4 – Branding & Documents
#     logo = models.ImageField(upload_to='org_logos/', blank=True)
#     digital_signature = models.ImageField(upload_to='org_signatures/', blank=True)
#     company_stamp = models.ImageField(upload_to='org_stamps/', blank=True)
#     primary_color = models.CharField(max_length=7, default='#007bff')  # hex color
#     secondary_color = models.CharField(max_length=7, default='#6c757d')
#
#     # Multi-tenant fields
#     subdomain = models.SlugField(unique=True, max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.legal_name
#
#
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
#     phone = models.CharField(max_length=20, blank=True)
#     # Add other profile fields as needed
#
#     def __str__(self):
#         return f"{self.user.username} - {self.organization.legal_name}"
#
# #
# # class UserProfile(TimeStampedModel):
# #     """Extend User with organization and other profile fields."""
# #     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
# #     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
# #     phone = models.CharField(max_length=20, blank=True)
# #     department = models.CharField(max_length=100, blank=True)
# #
# #     class Meta:
# #         verbose_name = "User Profile"
# #         verbose_name_plural = "User Profiles"
# #
# #     def __str__(self):
# #         return f"{self.user.username} - {self.organization.name}"
#
#
# class Team(TimeStampedModel):
#     """Team belonging to an organization."""
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     members = models.ManyToManyField(User, related_name='teams', blank=True)
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
#
#     class Meta:
#         verbose_name = "Team"
#         verbose_name_plural = "Teams"
#         unique_together = ['organization', 'name']
#
#     def __str__(self):
#         return self.name
#
#
# class Notification(TimeStampedModel):
#     NOTIFICATION_TYPES = (
#         ('followup', 'Follow-up Due'),
#         ('lead', 'New Lead'),
#         ('stage', 'Stage Changed'),
#         ('quotation', 'Quotation Sent'),
#         ('survey', 'Survey Scheduled'),
#         ('revenue', 'Revenue Recorded'),
#     )
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
#     notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
#     title = models.CharField(max_length=200)
#     message = models.TextField()
#     link = models.CharField(max_length=500, blank=True)
#     is_read = models.BooleanField(default=False)
#     # Optional organization field for filtering (can be null for system-wide notifications)
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
#
#     class Meta:
#         ordering = ['-created']
#
#     def __str__(self):
#         return f"{self.user.username} - {self.title}"
#
#
# # Tenant-aware manager and base model for other apps
# class TenantAwareManager(models.Manager):
#     """Manager that filters queryset by the current organization."""
#     def get_queryset(self):
#         qs = super().get_queryset()
#         org = get_current_organization()
#         if org:
#             return qs.filter(organization=org)
#         # If no organization (e.g., during setup), return empty to avoid cross-tenant data leaks
#         return qs.none()
#
#
# class TenantAwareModel(models.Model):
#     """Abstract base for all models that belong to an organization."""
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
#     objects = TenantAwareManager()
#
#     class Meta:
#         abstract = True


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# from .utils import get_current_organization
import uuid

from apps.core.utils import get_current_organization


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Organization(models.Model):
    BUSINESS_TYPES = (
        ('sole', 'Sole Proprietor'),
        ('partnership', 'Partnership'),
        ('llp', 'LLP'),
        ('pvt', 'Pvt Ltd'),
        ('ltd', 'Public Ltd'),
        ('ngo', 'NGO'),
        ('other', 'Other'),
    )

    # Business Details
    legal_name = models.CharField(max_length=200)
    trade_name = models.CharField(max_length=200, blank=True)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES)
    industry = models.CharField(max_length=100, blank=True)
    gst_number = models.CharField(max_length=50, blank=True)
    pan_tax_id = models.CharField(max_length=50, blank=True)
    registration_number = models.CharField(max_length=50, blank=True)

    # Address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    # Contact
    official_email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)
    billing_email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    timezone = models.CharField(max_length=100, default='UTC')
    currency = models.CharField(max_length=10, default='INR')

    # Branding
    logo = models.ImageField(upload_to='org_logos/', blank=True)
    digital_signature = models.ImageField(upload_to='org_signatures/', blank=True)
    company_stamp = models.ImageField(upload_to='org_stamps/', blank=True)
    primary_color = models.CharField(max_length=7, default='#007bff')
    secondary_color = models.CharField(max_length=7, default='#6c757d')

    # Multi‑tenant & subscription
    subdomain = models.SlugField(unique=True, max_length=100, db_index=True)
    is_active = models.BooleanField(default=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Limits (to be enforced by subscription)
    max_users = models.IntegerField(default=5)
    max_storage_mb = models.IntegerField(default=100)
    api_rate_limit = models.IntegerField(default=60)  # requests per minute
    leads_limit = models.IntegerField(default=100, help_text="Maximum number of leads allowed")
    quotations_limit = models.IntegerField(default=50, help_text="Maximum number of quotations allowed")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.legal_name

    class Meta:
        indexes = [
            models.Index(fields=['subdomain']),
            models.Index(fields=['is_active', 'created_at']),
        ]

        permissions = [
            ("view_platform_dashboard", "Can view platform dashboard"),
            ("manage_organizations", "Can create/suspend/edit organizations"),
            ("manage_subscriptions", "Can manage subscription plans and assignments"),
            ("view_all_organizations_data", "Can view any organization's data"),
        ]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='core_profile')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
    phone = models.CharField(max_length=20, blank=True)
    is_tenant_admin = models.BooleanField(default=False)  # can manage intra‑org users
    title = models.CharField(max_length=100, blank=True, help_text="Job title")
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.organization.legal_name}"

class Team(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')

    class Meta:
        unique_together = ['organization', 'name']

    def __str__(self):
        return self.name

class Notification(TimeStampedModel):
    NOTIFICATION_TYPES = (
        ('followup', 'Follow-up Due'),
        ('lead', 'New Lead'),
        ('stage', 'Stage Changed'),
        ('quotation', 'Quotation Sent'),
        ('survey', 'Survey Scheduled'),
        ('revenue', 'Revenue Recorded'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

# ---------- Tenant‑Aware Base ----------
class TenantAwareManager(models.Manager):
    """Automatically filters queryset by the current organization."""

    def get_queryset(self):
        qs = super().get_queryset()
        org = get_current_organization()
        if org:
            return qs.filter(organization=org)
        # For superuser access (control panel), we return unfiltered.
        # Use a separate manager for unfiltered access if needed.
        return qs

    def bulk_create(self, objs, **kwargs):
        org = get_current_organization()
        if org:
            for obj in objs:
                if not obj.organization_id:
                    obj.organization = org
        return super().bulk_create(objs, **kwargs)

class TenantAwareModel(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        db_index=True,
        editable=False   # never set via user input
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    objects = TenantAwareManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.organization_id:
            org = get_current_organization()
            if not org:
                raise ValueError("Cannot save tenant model without an organization.")
            self.organization = org
        super().save(*args, **kwargs)