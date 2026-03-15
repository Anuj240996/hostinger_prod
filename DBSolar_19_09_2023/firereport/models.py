from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Teams(models.Model):
    teamName = models.CharField(max_length=200, null=True)
    teamLeaderName = models.CharField(max_length=250, null=True)
    teamLeadMobno = models.CharField(max_length=15, null=True)
    teamMembers = models.CharField(max_length=300, null=True)
    postingDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.teamName

class Firereport(models.Model):
    FullName = models.CharField(max_length=250, null=True, db_column='fullname')
    MobileNumber = models.CharField(max_length=12, null=True, db_column='mobilenumber')
    Location = models.CharField(max_length=200, null=True, db_column='Location')
    # Complaint description is user-entered and can exceed 200 chars.
    # Store as TEXT to avoid "value too long" errors.
    Message = models.TextField(null=True, db_column='message')
    AssignTo = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='assignto_id')
    Status = models.CharField(max_length=150, null=True, blank=True, default="Pending", db_column='status')
    Postingdate = models.DateTimeField(auto_now_add=True, db_column='postingdate')
    AssignedTime = models.DateTimeField(null=True, db_column='assignedtime')
    UpdationDate = models.DateTimeField(null=True, db_column='updationdate')
    progress_date = models.DateTimeField(null=True, db_column='progress_date')
    working_date = models.DateTimeField(null=True, db_column='working_date')
    complete_date = models.DateTimeField(null=True, db_column='complete_date')
    Account_id = models.IntegerField(default=0, db_column='account_id')
    AssignBy = models.IntegerField(default=0, db_column='assignby')

    def save(self, *args, **kwargs):
        # Guarantee "Pending" if callers pass NULL/blank.
        if not self.Status:
            self.Status = "Pending"
        # Use IST (Asia/Kolkata) for Postingdate when creating new records
        if not self.pk and self.Postingdate is None:
            self.Postingdate = timezone.localtime(timezone.now())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.FullName

class Firetequesthistory(models.Model):
    id = models.BigAutoField(primary_key=True)  # ✅ FIX
    firereport = models.ForeignKey(Firereport, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=200, null=True)
    remark = models.CharField(max_length=250, null=True)
    postingDate = models.DateTimeField(auto_now_add=True)
    AssignTo = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='assignto_id')
    AssignBy = models.IntegerField(default=0, db_column='assignby')

    def save(self, *args, **kwargs):
        # Use IST for postingDate when creating new records
        if not self.pk and getattr(self, 'postingDate', None) is None:
            self.postingDate = timezone.localtime(timezone.now())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.status

