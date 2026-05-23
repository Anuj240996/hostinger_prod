# from django.db import models
# from django.contrib.auth.models import User
# from apps.core.models import TimeStampedModel
#
#
# class SalesTarget(TimeStampedModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_targets')
#     year = models.IntegerField()
#     month = models.IntegerField()
#     lead_target = models.IntegerField(default=0)
#     revenue_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#
#     class Meta:
#         unique_together = ['user', 'year', 'month']
#
#     def __str__(self):
#         return f"{self.user.get_full_name()} - {self.month}/{self.year}"
#
#
# class SalesAchievement(TimeStampedModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
#     date = models.DateField()
#     leads_acquired = models.IntegerField(default=0)
#     revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#
#     class Meta:
#         ordering = ['-date']
#
#     def __str__(self):
#         return f"{self.user.get_full_name()} - {self.date}"

from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel, TenantAwareModel

class SalesTarget(TenantAwareModel, TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_targets')
    year = models.IntegerField()
    month = models.IntegerField()
    lead_target = models.IntegerField(default=0)
    revenue_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ['organization', 'user', 'year', 'month']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.month}/{self.year}"


class SalesAchievement(TenantAwareModel, TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    date = models.DateField()
    leads_acquired = models.IntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date}"