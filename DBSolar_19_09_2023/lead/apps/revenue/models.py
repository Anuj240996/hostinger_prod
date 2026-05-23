# from django.db import models
# from django.contrib.auth.models import User
# from apps.core.models import TimeStampedModel
# from apps.leads.models import Lead
# from apps.quotations.models import Quotation
#
#
# class Revenue(TimeStampedModel):
#     PAYMENT_STATUS = (
#         ('pending', 'Pending'),
#         ('partial', 'Partially Paid'),
#         ('paid', 'Paid'),
#         ('overdue', 'Overdue'),
#     )
#
#     lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='revenues')
#     quotation = models.ForeignKey(Quotation, on_delete=models.SET_NULL, null=True, blank=True)
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     date = models.DateField()
#     payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
#     payment_method = models.CharField(max_length=50, blank=True)
#     transaction_id = models.CharField(max_length=100, blank=True)
#     notes = models.TextField(blank=True)
#
#     # Commission
#     commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
#     commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#
#     class Meta:
#         ordering = ['-date']
#
#     def __str__(self):
#         return f"{self.lead.name} - ₹{self.amount} - {self.date}"
#
#
# class RevenueTarget(TimeStampedModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenue_targets')
#     year = models.IntegerField()
#     month = models.IntegerField()
#     target_amount = models.DecimalField(max_digits=12, decimal_places=2)
#     achieved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#
#     class Meta:
#         unique_together = ['user', 'year', 'month']
#
#     def __str__(self):
#         return f"{self.user.get_full_name()} - {self.month}/{self.year}"
#
#     @property
#     def achievement_percentage(self):
#         if self.target_amount > 0:
#             return (self.achieved_amount / self.target_amount) * 100
#         return 0

from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel, TenantAwareModel
from apps.leads.models import Lead
from apps.quotations.models import Quotation

class Revenue(TenantAwareModel, TimeStampedModel):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='revenues')
    # Legacy CRM quotation (apps.quotations); optional for older rows.
    quotation = models.ForeignKey(Quotation, on_delete=models.SET_NULL, null=True, blank=True)
    # ERP quotation (quotation.Quotation / quotation_quotation) — use this for CRM flows on merged project.
    erp_quotation = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crm_revenue_rows',
        # Some merged DBs lack a PK/unique usable for FK targets on quotation_quotation; ORM link only.
        db_constraint=False,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.lead.name} - ₹{self.amount} - {self.date}"


class RevenueTarget(TenantAwareModel, TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenue_targets')
    year = models.IntegerField()
    month = models.IntegerField()
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    achieved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ['organization', 'user', 'year', 'month']  # unique per org and user

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.month}/{self.year}"

    @property
    def achievement_percentage(self):
        if self.target_amount > 0:
            return (self.achieved_amount / self.target_amount) * 100
        return 0