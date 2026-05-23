# from django.db import models
# from apps.core.models import TimeStampedModel
#
#
# class SystemSetting(TimeStampedModel):
#     key = models.CharField(max_length=100, unique=True)
#     value = models.TextField()
#     description = models.TextField(blank=True)
#
#     class Meta:
#         verbose_name = "System Setting"
#         verbose_name_plural = "System Settings"
#
#     def __str__(self):
#         return self.key
#
#
# class LostReason(TimeStampedModel):
#     name = models.CharField(max_length=100)
#     is_active = models.BooleanField(default=True)
#     order = models.IntegerField(default=0)
#
#     class Meta:
#         ordering = ['order']
#
#     def __str__(self):
#         return self.name
#
#
# class ScoringRule(TimeStampedModel):
#     CRITERIA_CHOICES = (
#         ('electricity_bill', 'Electricity Bill'),
#         ('property_type', 'Property Type'),
#         ('roof_type', 'Roof Type'),
#         ('location', 'Location'),
#         ('source', 'Lead Source'),
#         ('age', 'Lead Age'),
#     )
#
#     CONDITION_CHOICES = (
#         ('gt', 'Greater Than'),
#         ('lt', 'Less Than'),
#         ('eq', 'Equals'),
#         ('contains', 'Contains'),
#         ('in', 'In List'),
#     )
#
#     criteria = models.CharField(max_length=50, choices=CRITERIA_CHOICES)
#     condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
#     value = models.CharField(max_length=200)
#     points = models.IntegerField()
#     is_active = models.BooleanField(default=True)
#
#     class Meta:
#         ordering = ['-points']
#
#     def __str__(self):
#         return f"{self.get_criteria_display()} {self.get_condition_display()} {self.value} = {self.points} points"
#
# from django.db import models
# from apps.core.models import TimeStampedModel, TenantAwareModel
# from django.db import models
# from apps.core.models import TimeStampedModel, TenantAwareModel
# from apps.leads.models import LeadSource, Campaign  # already defined in leads app
#
# class SystemSetting(TenantAwareModel, TimeStampedModel):
#     key = models.CharField(max_length=100)
#     value = models.TextField()
#     description = models.TextField(blank=True)
#
#     class Meta:
#         unique_together = ['organization', 'key']
#         verbose_name = "System Setting"
#         verbose_name_plural = "System Settings"
#
#     def __str__(self):
#         return self.key
#
#
# class LeadSource(TenantAwareModel, TimeStampedModel):
#     name = models.CharField(max_length=100)
#     is_active = models.BooleanField(default=True)
#     cost_per_lead = models.IntegerField(default=0)
#
#
#     # class Meta:
#     #     ordering = ['order']
#     #     unique_together = ['organization', 'name']
#
#     class Meta:
#         verbose_name = "Lead Source"
#         verbose_name_plural = "Lead Sources"
#         unique_together = ['organization', 'name']  # Add this line
#
#     def __str__(self):
#         return self.name
#
#
# #
# #
# # class ScoringRule(TenantAwareModel, TimeStampedModel):
# #     CRITERIA_CHOICES = (
# #         ('electricity_bill', 'Electricity Bill'),
# #         ('property_type', 'Property Type'),
# #         ('roof_type', 'Roof Type'),
# #         ('location', 'Location'),
# #         ('source', 'Lead Source'),
# #         ('age', 'Lead Age'),
# #     )
# #     CONDITION_CHOICES = (
# #         ('gt', 'Greater Than'),
# #         ('lt', 'Less Than'),
# #         ('eq', 'Equals'),
# #         ('contains', 'Contains'),
# #         ('in', 'In List'),
# #     )
# #
# #     criteria = models.CharField(max_length=50, choices=CRITERIA_CHOICES)
# #     condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
# #     value = models.CharField(max_length=200)
# #     points = models.IntegerField()
# #     is_active = models.BooleanField(default=True)
# #
# #     class Meta:
# #         ordering = ['-points']
# #
# #     def __str__(self):
# #         return f"{self.get_criteria_display()} {self.get_condition_display()} {self.value} = {self.points} points"
# #
#
# # Note: PipelineStage is defined in pipeline app; we don't redefine it here.
# # LostReason and ScoringRule are defined here.
#
# class LostReason(TenantAwareModel, TimeStampedModel):
#     """Reasons for losing a lead."""
#     name = models.CharField(max_length=100)
#     is_active = models.BooleanField(default=True)
#     order = models.IntegerField(default=0)
#
#     class Meta:
#         ordering = ['order']
#         unique_together = ['organization', 'name']
#
#
#     def __str__(self):
#         return self.name
#
#
#
#
# class ScoringRule(TenantAwareModel, TimeStampedModel):
#     """Rules for automatic lead scoring."""
#     CRITERIA_CHOICES = (
#         ('electricity_bill', 'Electricity Bill (₹)'),
#         ('property_type', 'Property Type'),
#         ('roof_type', 'Roof Type'),
#         ('location', 'Location (City)'),
#         ('source', 'Lead Source'),
#         ('age', 'Lead Age (days)'),
#     )
#     CONDITION_CHOICES = (
#         ('gt', 'Greater Than'),
#         ('lt', 'Less Than'),
#         ('eq', 'Equals'),
#         ('contains', 'Contains'),
#         ('in', 'In List (comma-separated)'),
#     )
#
#     criteria = models.CharField(max_length=50, choices=CRITERIA_CHOICES)
#     condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
#     value = models.CharField(max_length=200, help_text="Value to compare against")
#     points = models.IntegerField(help_text="Points awarded when rule matches")
#     is_active = models.BooleanField(default=True)
#
#     class Meta:
#         ordering = ['-points']
#
#     def __str__(self):
#         return f"{self.get_criteria_display()} {self.get_condition_display()} {self.value} = {self.points} pts"

from django.db import models
from apps.core.models import TimeStampedModel, TenantAwareModel

class SystemSetting(TenantAwareModel, TimeStampedModel):
    key = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['organization', 'key']
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.key


class LostReason(TenantAwareModel, TimeStampedModel):
    """Reasons for losing a lead."""
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['organization', 'name']

    def __str__(self):
        return self.name


class ScoringRule(TenantAwareModel, TimeStampedModel):
    """Rules for automatic lead scoring."""
    CRITERIA_CHOICES = (
        ('electricity_bill', 'Electricity Bill (₹)'),
        ('property_type', 'Property Type'),
        ('roof_type', 'Roof Type'),
        ('location', 'Location (City)'),
        ('source', 'Lead Source'),
        ('age', 'Lead Age (days)'),
    )
    CONDITION_CHOICES = (
        ('gt', 'Greater Than'),
        ('lt', 'Less Than'),
        ('eq', 'Equals'),
        ('contains', 'Contains'),
        ('in', 'In List (comma-separated)'),
    )

    criteria = models.CharField(max_length=50, choices=CRITERIA_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    value = models.CharField(max_length=200, help_text="Value to compare against")
    points = models.IntegerField(help_text="Points awarded when rule matches")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-points']

    def __str__(self):
        return f"{self.get_criteria_display()} {self.get_condition_display()} {self.value} = {self.points} pts"