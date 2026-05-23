# from django.db import models
# from django.contrib.auth.models import User
# from apps.core.models import TimeStampedModel
# from apps.leads.models import Lead
# from django.utils import timezone
#
#
# class Survey(TimeStampedModel):
#     STATUS_CHOICES = (
#         ('scheduled', 'Scheduled'),
#         ('in_progress', 'In Progress'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     )
#
#     FEASIBILITY_CHOICES = (
#         ('high', 'High'),
#         ('medium', 'Medium'),
#         ('low', 'Low'),
#     )
#
#     lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='surveys')
#     engineer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_surveys')
#     scheduled_date = models.DateTimeField()
#     completed_date = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
#
#     # Survey Details
#     feasibility = models.CharField(max_length=10, choices=FEASIBILITY_CHOICES, null=True, blank=True)
#     recommended_size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kW")
#     panel_count = models.IntegerField(null=True, blank=True)
#     inverter_capacity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kW")
#     estimated_generation = models.IntegerField(null=True, blank=True, help_text="kWh/day")
#     roof_area_required = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, help_text="sq.ft")
#
#     # Analysis
#     has_shadow_issues = models.BooleanField(default=False)
#     structural_feasible = models.BooleanField(default=True)
#     technical_notes = models.TextField(blank=True)
#
#     # Metadata
#     created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_surveys')
#     assigned_date = models.DateTimeField(null=True, blank=True)
#
#     class Meta:
#         ordering = ['-scheduled_date']
#
#     def __str__(self):
#         return f"Survey for {self.lead.name} - {self.scheduled_date.date()}"
#
#     @property
#     def is_today(self):
#         return self.scheduled_date.date() == timezone.now().date()
#
#     # @property
#     # def has_quotation(self):
#     #     return hasattr(self, 'quotation')
#
#     # @property
#     # def has_quotation(self):
#     #     from apps.quotations.models import Quotation
#     #     return Quotation.objects.filter(survey=self).exists()
#
#     @property
#     def has_quotation(self):
#         from apps.quotations.models import Quotation
#         return Quotation.objects.filter(survey=self).exists()
#
#
#
# class SurveyImage(TimeStampedModel):
#     survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='roof_images')
#     image = models.ImageField(upload_to='survey_images/')
#     caption = models.CharField(max_length=200, blank=True)
#     is_primary = models.BooleanField(default=False)
#
#     class Meta:
#         ordering = ['-is_primary', 'created']
#
#     def __str__(self):
#         return f"Image for {self.survey.lead.name}"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import TimeStampedModel, TenantAwareModel
from apps.leads.models import Lead

class Survey(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    FEASIBILITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='surveys')
    engineer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_surveys')
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    feasibility = models.CharField(max_length=10, choices=FEASIBILITY_CHOICES, null=True, blank=True)
    recommended_size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kW")
    panel_count = models.IntegerField(null=True, blank=True)
    inverter_capacity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kW")
    estimated_generation = models.IntegerField(null=True, blank=True, help_text="kWh/day")
    roof_area_required = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, help_text="sq.ft")

    has_shadow_issues = models.BooleanField(default=False)
    structural_feasible = models.BooleanField(default=True)
    technical_notes = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_surveys')
    assigned_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"Survey for {self.lead.name} - {self.scheduled_date.date()}"

    @property
    def is_today(self):
        return self.scheduled_date.date() == timezone.now().date()

    @property
    def has_quotation(self):
        from apps.quotations.models import Quotation
        return Quotation.objects.filter(survey=self).exists()


class SurveyImage(TimeStampedModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='roof_images')
    image = models.ImageField(upload_to='survey_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'created']

    def __str__(self):
        return f"Image for {self.survey.lead.name}"