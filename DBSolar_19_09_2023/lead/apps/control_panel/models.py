from django.db import models
from apps.core.models import Organization, User

class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    def __str__(self):
        return self.codename

class Role(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    # null = platform‑wide role (super‑admin only)
    permissions = models.ManyToManyField(Permission, through='RolePermission')

    class Meta:
        unique_together = ['organization', 'name']
        indexes = [models.Index(fields=['organization', 'name'])]

    def __str__(self):
        return self.name

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['role', 'permission']

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)  # denormalised

    class Meta:
        unique_together = ['user', 'role', 'organization']
        indexes = [models.Index(fields=['user', 'organization'])]

class Feature(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    enabled_by_default = models.BooleanField(default=False)

    def __str__(self):
        return self.codename

class OrganizationFeature(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)

    class Meta:
        unique_together = ['organization', 'feature']

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_users = models.IntegerField()
    max_storage_mb = models.IntegerField()
    api_rate_limit = models.IntegerField(default=60)
    has_advanced_reports = models.BooleanField(default=False)
    has_automation = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PlanFeature(models.Model):
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ['plan', 'feature']

class OrganizationSubscription(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('trialing', 'Trialing'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
    ], default='active')
    stripe_subscription_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.organization.legal_name} - {self.plan.name}"


from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=200, help_text="String representation of the object")
    changes = models.JSONField(null=True, blank=True, help_text="JSON diff of changes (for updates)")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_display()} {self.object_repr} by {self.user} at {self.timestamp}"