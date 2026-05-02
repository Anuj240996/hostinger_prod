"""
Complaint (Consumer Complaint) Portal — ORM models for the `firereport` app only.

Domain: complaint tickets (`Firereport`), team metadata (`Teams`), and per-ticket
history (`Firetequesthistory`). Schema changes for this portal belong here — not in
other apps (transactions, customer, quotation, etc.).
"""
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


class ServiceRequest(models.Model):
    FullName = models.CharField(max_length=250, null=True, db_column='fullname')
    MobileNumber = models.CharField(max_length=12, null=True, db_column='mobilenumber')
    Location = models.CharField(max_length=200, null=True, db_column='Location')
    Message = models.TextField(null=True, db_column='message')
    AssignTo = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='assignto_id')
    Status = models.CharField(max_length=150, null=True, blank=True, default="In Process", db_column='status')
    Postingdate = models.DateTimeField(auto_now_add=True, db_column='postingdate')
    AssignedTime = models.DateTimeField(null=True, db_column='assignedtime')
    UpdationDate = models.DateTimeField(null=True, db_column='updationdate')
    complete_date = models.DateTimeField(null=True, db_column='complete_date')
    Account_id = models.IntegerField(default=0, db_column='account_id')
    AssignBy = models.IntegerField(default=0, db_column='assignby')

    def save(self, *args, **kwargs):
        if not self.Status:
            self.Status = "In Process"
        if not self.pk and self.Postingdate is None:
            self.Postingdate = timezone.localtime(timezone.now())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.FullName or f"ServiceRequest#{self.pk}"


class ServiceRequestHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=200, null=True)
    remark = models.CharField(max_length=250, null=True)
    postingDate = models.DateTimeField(auto_now_add=True)
    AssignTo = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='assignto_id')
    AssignBy = models.IntegerField(default=0, db_column='assignby')

    def save(self, *args, **kwargs):
        if not self.pk and getattr(self, 'postingDate', None) is None:
            self.postingDate = timezone.localtime(timezone.now())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.status or "In Process"


class ServiceRemarkMaster(models.Model):
    remark = models.CharField(max_length=250, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["remark"]

    def __str__(self):
        return self.remark


class ServiceReport(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='service_report')
    report_date = models.DateField(null=True, blank=True)
    report_time = models.TimeField(null=True, blank=True)

    consumer_name = models.CharField(max_length=250, null=True, blank=True)
    consumer_address = models.CharField(max_length=300, null=True, blank=True)
    consumer_phone = models.CharField(max_length=20, null=True, blank=True)

    plant_capacity = models.CharField(max_length=100, null=True, blank=True)
    load_sanction = models.CharField(max_length=100, null=True, blank=True)
    phase_type = models.CharField(max_length=20, null=True, blank=True, default='single')
    solar_module_make = models.CharField(max_length=150, null=True, blank=True)
    solar_module_quantity = models.CharField(max_length=50, null=True, blank=True)
    solar_module_capacity = models.CharField(max_length=100, null=True, blank=True)
    inverter_make = models.CharField(max_length=150, null=True, blank=True)
    inverter_quantity = models.CharField(max_length=50, null=True, blank=True)
    inverter_capacity = models.CharField(max_length=100, null=True, blank=True)

    ac_voltage_rn = models.CharField(max_length=50, null=True, blank=True)
    ac_voltage_yn = models.CharField(max_length=50, null=True, blank=True)
    ac_voltage_bn = models.CharField(max_length=50, null=True, blank=True)
    ac_current_r = models.CharField(max_length=50, null=True, blank=True)
    ac_current_y = models.CharField(max_length=50, null=True, blank=True)
    ac_current_b = models.CharField(max_length=50, null=True, blank=True)

    dc_rows_json = models.TextField(null=True, blank=True)

    acdb_pn = models.CharField(max_length=50, null=True, blank=True)
    acdb_ne = models.CharField(max_length=50, null=True, blank=True)
    acdb_pn2 = models.CharField(max_length=50, null=True, blank=True)

    generation_today = models.CharField(max_length=100, null=True, blank=True)
    generation_yesterday = models.CharField(max_length=100, null=True, blank=True)
    generation_monthly = models.CharField(max_length=100, null=True, blank=True)
    generation_yearly = models.CharField(max_length=100, null=True, blank=True)

    remarks_text = models.TextField(null=True, blank=True)

    import_units = models.CharField(max_length=100, null=True, blank=True)
    export_units = models.CharField(max_length=100, null=True, blank=True)
    meter_generation_units = models.CharField(max_length=100, null=True, blank=True)

    consumer_sign_name = models.CharField(max_length=200, null=True, blank=True)
    engg_sign_name = models.CharField(max_length=200, null=True, blank=True)
    engg_id = models.CharField(max_length=100, null=True, blank=True)
    engg_sign_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ServiceReport#{self.service_request_id}"

