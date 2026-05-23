# from django.db import models
# from django.contrib.auth.models import User
# from apps.core.models import TimeStampedModel
# from apps.leads.models import Lead
#
#
# class PipelineStage(TimeStampedModel):
#     name = models.CharField(max_length=100)
#     order = models.IntegerField(default=0)
#     color = models.CharField(max_length=20, default='#0d6efd')
#     probability = models.IntegerField(default=0, help_text="Default probability %")
#     is_active = models.BooleanField(default=True)
#
#     class Meta:
#         ordering = ['order']
#
#     def __str__(self):
#         return self.name
#
#
# class PipelineHistory(TimeStampedModel):
#     lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='pipeline_history')
#     from_stage = models.CharField(max_length=50)
#     to_stage = models.CharField(max_length=50)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     notes = models.TextField(blank=True)
#
#     class Meta:
#         ordering = ['-created']
#
#     def __str__(self):
#         return f"{self.lead.name}: {self.from_stage} -> {self.to_stage}"

from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel, TenantAwareModel
from apps.leads.models import Lead

class PipelineStage(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    color = models.CharField(max_length=20, default='#0d6efd')
    probability = models.IntegerField(default=0, help_text="Default probability %")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = ['organization', 'name']  # stage names unique per org

    def __str__(self):
        return self.name


class PipelineHistory(TimeStampedModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='pipeline_history')
    from_stage = models.CharField(max_length=50)
    to_stage = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.lead.name}: {self.from_stage} -> {self.to_stage}"