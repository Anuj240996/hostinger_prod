# from decimal import Decimal
#
# from django.db import models
# from django.contrib.auth.models import User
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.utils import timezone
# from apps.core.models import TimeStampedModel
# import uuid
#
#
# class LeadSource(models.Model):
#     name = models.CharField(max_length=100)
#     is_active = models.BooleanField(default=True)
#     cost_per_lead = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#
#     class Meta:
#         verbose_name = "Lead Source"
#         verbose_name_plural = "Lead Sources"
#
#     def __str__(self):
#         return self.name
#
#
# class Campaign(models.Model):
#     name = models.CharField(max_length=200)
#     source = models.ForeignKey(LeadSource, on_delete=models.CASCADE)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     is_active = models.BooleanField(default=True)
#
#     class Meta:
#         verbose_name = "Campaign"
#         verbose_name_plural = "Campaigns"
#
#     def __str__(self):
#         return self.name
#
#
# class Lead(TimeStampedModel):
#     STAGE_CHOICES = (
#         ('new', 'New Lead'),
#         ('qualified', 'Qualified'),
#         ('survey', 'Survey'),
#         ('quote', 'Quote Sent'),
#         ('negotiation', 'Negotiation'),
#         ('won', 'Won'),
#         ('lost', 'Lost'),
#     )
#
#     SCORE_CHOICES = (
#         ('high', 'High'),
#         ('medium', 'Medium'),
#         ('low', 'Low'),
#     )
#
#     PROPERTY_TYPES = (
#         ('residential', 'Residential'),
#         ('commercial', 'Commercial'),
#         ('industrial', 'Industrial'),
#     )
#
#     ROOF_TYPES = (
#         ('flat', 'Flat'),
#         ('sloped', 'Sloped'),
#         ('metal', 'Metal'),
#         ('tile', 'Tile'),
#         ('other', 'Other'),
#     )
#
#     # Basic Information
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=200)
#     phone = models.CharField(max_length=20)
#     email = models.EmailField(blank=True)
#     alternate_phone = models.CharField(max_length=20, blank=True)
#
#     # Location
#     address = models.TextField()
#     city = models.CharField(max_length=100)
#     state = models.CharField(max_length=50)
#     pincode = models.CharField(max_length=10)
#     latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#
#     # Property Details
#     property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='residential')
#     roof_type = models.CharField(max_length=20, choices=ROOF_TYPES, default='flat')
#     electricity_bill = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     monthly_consumption = models.IntegerField(null=True, blank=True, help_text="kWh per month")
#
#     # Lead Details
#     source = models.ForeignKey(LeadSource, on_delete=models.SET_NULL, null=True)
#     campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
#     stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='new')
#     score = models.CharField(max_length=10, choices=SCORE_CHOICES, default='medium')
#
#     # Assignment
#     assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_leads')
#     assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_by_leads')
#     assigned_date = models.DateTimeField(null=True, blank=True)
#
#     # Budget & Value
#     budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
#     estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
#     probability = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
#
#     # Dates
#     next_followup = models.DateTimeField(null=True, blank=True)
#     last_contacted = models.DateTimeField(null=True, blank=True)
#     converted_at = models.DateTimeField(null=True, blank=True)
#     lost_at = models.DateTimeField(null=True, blank=True)
#
#     # Notes
#     notes = models.TextField(blank=True)
#     internal_notes = models.TextField(blank=True)
#
#     # Lost Reason
#     lost_reason = models.CharField(max_length=200, blank=True)
#     competitor = models.CharField(max_length=200, blank=True)
#
#     class Meta:
#         ordering = ['-created']
#         indexes = [
#             models.Index(fields=['stage']),
#             models.Index(fields=['assigned_to']),
#             models.Index(fields=['created']),
#         ]
#
#     def __str__(self):
#         return self.name
#
#     def save(self, *args, **kwargs):
#         if not self.assigned_date and self.assigned_to:
#             self.assigned_date = timezone.now()
#         super().save(*args, **kwargs)
#
#     # @property
#     # def weighted_value(self):
#     #     return (self.estimated_value or 0) * (self.probability / 100)
#
#     from decimal import Decimal
#
#     @property
#     def weighted_value(self):
#         if self.estimated_value is None:
#             return Decimal('0')
#         # Convert probability to Decimal
#         prob = Decimal(str(self.probability)) / Decimal('100')
#         return self.estimated_value * prob
#
#     @property
#     def age_in_days(self):
#         return (timezone.now().date() - self.created.date()).days
#
#
# class LeadActivity(TimeStampedModel):
#     ACTIVITY_TYPES = (
#         ('call', 'Call'),
#         ('whatsapp', 'WhatsApp'),
#         ('email', 'Email'),
#         ('note', 'Note'),
#         ('followup', 'Follow-up'),
#         ('stage_change', 'Stage Change'),
#         ('quotation', 'Quotation'),
#         ('survey', 'Survey'),
#     )
#
#     lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
#     description = models.TextField()
#     metadata = models.JSONField(default=dict, blank=True)
#
#     class Meta:
#         ordering = ['-created']
#         verbose_name = "Lead Activity"
#         verbose_name_plural = "Lead Activities"
#
#     def __str__(self):
#         return f"{self.lead.name} - {self.get_activity_type_display()}"
#
#
# class FollowUp(TimeStampedModel):
#     STATUS_CHOICES = (
#         ('scheduled', 'Scheduled'),
#         ('completed', 'Completed'),
#         ('missed', 'Missed'),
#         ('rescheduled', 'Rescheduled'),
#     )
#
#     lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='followups')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     scheduled_date = models.DateTimeField()
#     completed_date = models.DateTimeField(null=True, blank=True)
#     notes = models.TextField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
#     reminder_sent = models.BooleanField(default=False)
#
#     class Meta:
#         ordering = ['scheduled_date']
#
#     def __str__(self):
#         return f"{self.lead.name} - {self.scheduled_date}"

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.core.models import TimeStampedModel, TenantAwareModel
import uuid

class LeadSource(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    cost_per_lead = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Lead Source"
        verbose_name_plural = "Lead Sources"

    def __str__(self):
        return self.name


class Campaign(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=200)
    source = models.ForeignKey(LeadSource, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"

    def __str__(self):
        return self.name


class Lead(TenantAwareModel, TimeStampedModel):
    STAGE_CHOICES = (
        ('new', 'New Lead'),
        ('qualified', 'Qualified'),
        ('survey', 'Survey'),
        ('quote', 'Quote Sent'),
        ('negotiation', 'Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    )
    SCORE_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    PROPERTY_TYPES = (
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
    )
    ROOF_TYPES = (
        ('flat', 'Flat'),
        ('sloped', 'Sloped'),
        ('metal', 'Metal'),
        ('tile', 'Tile'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    alternate_phone = models.CharField(max_length=20, blank=True)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='residential')
    roof_type = models.CharField(max_length=20, choices=ROOF_TYPES, default='flat')
    electricity_bill = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monthly_consumption = models.IntegerField(null=True, blank=True, help_text="kWh per month")

    source = models.ForeignKey(LeadSource, on_delete=models.SET_NULL, null=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='new')
    score = models.CharField(max_length=10, choices=SCORE_CHOICES, default='medium')

    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_leads')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='crm_assigned_by_leads')
    assigned_date = models.DateTimeField(null=True, blank=True)

    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    probability = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    next_followup = models.DateTimeField(null=True, blank=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    lost_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    lost_reason = models.CharField(max_length=200, blank=True)
    competitor = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['stage']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['created']),
        ]



    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.assigned_date and self.assigned_to:
            self.assigned_date = timezone.now()
        super().save(*args, **kwargs)

    @property
    def weighted_value(self):
        from decimal import Decimal
        return (self.estimated_value or Decimal('0')) * (Decimal(self.probability) / Decimal('100'))

    @property
    def age_in_days(self):
        return (timezone.now().date() - self.created.date()).days


class LeadActivity(TimeStampedModel):
    ACTIVITY_TYPES = (
        ('created', 'Lead Created'),
        ('assignment', 'Assigned'),
        ('call', 'Call'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('note', 'Note'),
        ('followup', 'Follow-up'),
        ('stage_change', 'Stage Change'),
        ('quotation', 'Quotation'),
        ('survey', 'Survey'),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='crm_lead_activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = "Lead Activity"
        verbose_name_plural = "Lead Activities"

    def __str__(self):
        return f"{self.lead.name} - {self.get_activity_type_display()}"


class FollowUp(TimeStampedModel):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('rescheduled', 'Rescheduled'),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='followups')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.lead.name} - {self.scheduled_date}"
