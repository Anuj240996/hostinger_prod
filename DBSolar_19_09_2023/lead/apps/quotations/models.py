# from django.db import models
# from django.contrib.auth.models import User
# from apps.core.models import TimeStampedModel
# from apps.leads.models import Lead
# from apps.surveys.models import Survey
# from django.utils import timezone
#
# class Quotation(TimeStampedModel):
#     STATUS_CHOICES = (
#         ('draft', 'Draft'),
#         ('sent', 'Sent'),
#         ('viewed', 'Viewed'),
#         ('negotiating', 'Negotiating'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#         ('expired', 'Expired'),
#     )
#
#     quote_number = models.CharField(max_length=50, unique=True)
#     lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='quotations')
#     survey = models.ForeignKey(Survey, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotation')
#     version = models.IntegerField(default=1)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
#
#     # System Details
#     system_size = models.DecimalField(max_digits=5, decimal_places=2, help_text="kW")
#     panel_type = models.CharField(max_length=100)
#     panel_count = models.IntegerField()
#     inverter_type = models.CharField(max_length=100)
#     mounting_type = models.CharField(max_length=100)
#     warranty_years = models.IntegerField(default=5)
#     estimated_generation = models.IntegerField(help_text="kWh/year")
#
#     # Financial Details
#     subtotal = models.DecimalField(max_digits=12, decimal_places=2)
#     gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18)
#     gst_amount = models.DecimalField(max_digits=12, decimal_places=2)
#     total_cost = models.DecimalField(max_digits=12, decimal_places=2)
#     subsidy_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     net_cost = models.DecimalField(max_digits=12, decimal_places=2)
#
#     # Financial Analysis
#     roi = models.DecimalField(max_digits=5, decimal_places=2, help_text="%")
#     payback_years = models.DecimalField(max_digits=4, decimal_places=1)
#     monthly_emi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     monthly_savings = models.DecimalField(max_digits=10, decimal_places=2, help_text="Estimated monthly savings")
#
#     # Dates
#     valid_until = models.DateField()
#     sent_date = models.DateTimeField(null=True, blank=True)
#     approval_date = models.DateTimeField(null=True, blank=True)
#
#     # Notes
#     terms_conditions = models.TextField(blank=True)
#     negotiation_notes = models.TextField(blank=True)
#     internal_notes = models.TextField(blank=True)
#
#     # Approval
#     customer_approved = models.BooleanField(default=False)
#     internal_approved = models.BooleanField(default=False)
#     approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
#                                     related_name='approved_quotations')
#
#     # Metadata
#     created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_quotations')
#
#     class Meta:
#         ordering = ['-created']
#
#     def __str__(self):
#         return f"{self.quote_number} - {self.lead.name}"
#
#     def save(self, *args, **kwargs):
#         if not self.quote_number:
#             # Generate quote number
#             last_quote = Quotation.objects.order_by('-id').first()
#             if last_quote:
#                 last_number = int(last_quote.quote_number.split('-')[-1])
#                 self.quote_number = f"Q-{timezone.now().year}-{last_number + 1:04d}"
#             else:
#                 self.quote_number = f"Q-{timezone.now().year}-0001"
#         super().save(*args, **kwargs)
#
#
# class QuotationItem(TimeStampedModel):
#     quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
#     description = models.CharField(max_length=200)
#     quantity = models.IntegerField()
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2)
#     total_price = models.DecimalField(max_digits=12, decimal_places=2)
#
#     def __str__(self):
#         return f"{self.description} - {self.quotation.quote_number}"
#
#
# class QuotationRevision(TimeStampedModel):
#     quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='revisions')
#     version = models.IntegerField()
#     total_cost = models.DecimalField(max_digits=12, decimal_places=2)
#     notes = models.TextField(blank=True)
#     created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#
#     class Meta:
#         ordering = ['-version']
#
#     def __str__(self):
#         return f"{self.quotation.quote_number} - v{self.version}"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import TimeStampedModel, TenantAwareModel
from apps.leads.models import Lead
from apps.surveys.models import Survey

class QuoteNumberSequence(models.Model):
    """Stores the last used quote number per year for atomic increments."""
    year = models.IntegerField(unique=True)
    last_number = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.year}: {self.last_number}"

class Quotation(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('viewed', 'Viewed'),
        ('negotiating', 'Negotiating'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    )

    quote_number = models.CharField(max_length=50, unique=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='quotations')
    survey = models.ForeignKey(Survey, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotation')
    consumer_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional display name on the PDF; if empty, the selected lead's name is used.",
    )
    version = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    system_size = models.DecimalField(max_digits=5, decimal_places=2, help_text="kW")
    panel_type = models.CharField(max_length=100)
    panel_count = models.IntegerField()
    inverter_type = models.CharField(max_length=100)
    mounting_type = models.CharField(max_length=100)
    warranty_years = models.IntegerField(default=5)
    estimated_generation = models.IntegerField(help_text="kWh/year")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    subsidy_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_cost = models.DecimalField(max_digits=12, decimal_places=2)

    roi = models.DecimalField(max_digits=5, decimal_places=2, help_text="%")
    payback_years = models.DecimalField(max_digits=4, decimal_places=1)
    monthly_emi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monthly_savings = models.DecimalField(max_digits=10, decimal_places=2, help_text="Estimated monthly savings")

    valid_until = models.DateField()
    sent_date = models.DateTimeField(null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)

    terms_conditions = models.TextField(blank=True)
    negotiation_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    customer_approved = models.BooleanField(default=False)
    internal_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_quotations')

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_quotations')

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.quote_number} - {self.lead.name}"

    def get_customer_display_name(self):
        name = (self.consumer_name or '').strip()
        return name or self.lead.name

    # def save(self, *args, **kwargs):
    #     if not self.quote_number:
    #         last_quote = Quotation.objects.order_by('-id').first()
    #         if last_quote:
    #             last_number = int(last_quote.quote_number.split('-')[-1])
    #             self.quote_number = f"Q-{timezone.now().year}-{last_number + 1:04d}"
    #         else:
    #             self.quote_number = f"Q-{timezone.now().year}-0001"
    #     super().save(*args, **kwargs)
    def save(self, *args, **kwargs):
        if not self.quote_number:
            from django.db import transaction
            with transaction.atomic():
                year = timezone.now().year
                # Lock the row for this year to prevent race conditions
                sequence, created = QuoteNumberSequence.objects.select_for_update().get_or_create(year=year)
                next_number = sequence.last_number + 1
                sequence.last_number = next_number
                sequence.save()
                self.quote_number = f"Q-{year}-{next_number:04d}"
        super().save(*args, **kwargs)


class QuotationItem(TimeStampedModel):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.quotation.quote_number}"


class QuotationRevision(TimeStampedModel):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='revisions')
    version = models.IntegerField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-version']

    def __str__(self):
        return f"{self.quotation.quote_number} - v{self.version}"