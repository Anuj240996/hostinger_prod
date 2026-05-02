from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings

# Create your models here.
DEPARTMENT = (
    ('Administration','Administration'),
    ('Stockist','Stockist'),
    ('Finance','Finance'),
    ('Engineers','Engineers'),
)
desig = (
    ('Admin','Admin'),
    ('Staff','Staff'),

)



class Profile(models.Model):
    # customer = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    # address = models.CharField(max_length=200)
    # phone = models.CharField(max_length=50)
    # DOB = models.DateField(null=True)
    # department = models.CharField(max_length=50, choices=DEPARTMENT, null=True)
    # image = models.ImageField(default='default.png',
    #                           upload_to='profile_images')
    # customer = models.ForeignKey(User,on_delete=models.CASCADE,null=True)

    customer = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    #customer = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='profile')
    address = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=50, null=True)
    DOB = models.DateField(null=True, db_column='dob')
    department = models.CharField(choices=[('Administration', 'Administration'), ('Stockist', 'Stockist'), ('Engineers', 'Engineers'), ('Finance', 'Finance'), ('Associate', 'Associate')],max_length=50)
    image = models.ImageField(default='profile_images/default.png',upload_to='profile_pics', null=True, blank=True)
    designation = models.CharField(choices=[('Admin', 'Admin'), ('Sr.Cleark', 'Sr.Cleark'), ('Jr.Cleark', 'Jr.Cleark'), ('Accountant', 'Accountant'), ('Sr.Engg', 'Sr.Engg'), ('Jr.Engg', 'Jr.Engg'), ('Associate', 'Associate')] , max_length=50,  null=True)
    last_updated_by = models.PositiveIntegerField(null=True)
    workphone = models.CharField(max_length=50, null=True)
    bg = models.CharField(
        choices=[('O +ve', 'O +ve'), ('O -ve', 'O -ve'),('A +ve', 'A +ve'), ('A -ve', 'A -ve'),
                 ('B +ve', 'B +ve'), ('B -ve', 'B -ve'),('AB +ve', 'AB +ve'), ('AB -ve', 'AB -ve')], max_length=50)
    #bg = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    taluka = models.CharField(max_length=50, null=True)
    district = models.CharField(max_length=50, null=True)
    pg = models.CharField(max_length=50, null=True)
    institution = models.CharField(max_length=50, null=True)
    yop = models.DateField(null=True)
    specili = models.CharField(max_length=50, null=True)

    resign_reason = models.CharField(max_length=150, null=True)
    resign_type = models.CharField(max_length=50, null=True)
    resign_date = models.DateField(null=True)
    rejoin_reason = models.CharField(max_length=150, null=True)
    rejoin_date = models.DateField(null=True)

    name = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=50, null=True)
    emraddress = models.CharField(max_length=50, null=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    #last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    #last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_profiles')
    #joiningdate = models.DateField(null=True)

    def __str__(self):
        return f'{self.customer.username}-Profile'



class Permission(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ==================== CONTROL PANEL PERMISSION MANAGEMENT ====================

class Module(models.Model):
    """Defines modules in the system (Employee, Customer, Quotation, Dashboard, etc.)"""
    name = models.CharField(max_length=100, unique=True, help_text="Module name (e.g., Employee, Customer, Quotation)")
    display_name = models.CharField(max_length=100, help_text="Display name for the module")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order in control panel")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'display_name']

    def __str__(self):
        return self.display_name


class ModulePermission(models.Model):
    """Defines operations available for modules (Add, View, Edit, Delete, etc.)"""
    OPERATION_CHOICES = [
        ('add', 'Add'),
        ('view', 'View'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions')
    operation = models.CharField(max_length=50, choices=OPERATION_CHOICES)
    display_name = models.CharField(max_length=100, help_text="Display name for the operation")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['module', 'operation']
        ordering = ['module', 'order', 'operation']

    def __str__(self):
        return f"{self.module.display_name} - {self.display_name}"


class UserModulePermission(models.Model):
    """Links users to their module permissions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_permissions')
    module_permission = models.ForeignKey(ModulePermission, on_delete=models.CASCADE, related_name='user_permissions')
    granted = models.BooleanField(default=True, help_text="True if permission is granted, False if denied")
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about this permission")

    class Meta:
        unique_together = ['user', 'module_permission']
        ordering = ['user', 'module_permission__module', 'module_permission__operation']

    def __str__(self):
        status = "Granted" if self.granted else "Denied"
        return f"{self.user.username} - {self.module_permission} ({status})"


class ControlPanelAccess(models.Model):
    """Stores control panel password for security"""
    password_hash = models.CharField(max_length=255, help_text="Hashed password for control panel access")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    last_accessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Control Panel Access"
        verbose_name_plural = "Control Panel Access"

    def __str__(self):
        return "Control Panel Access Configuration"


# ==================== CONTROL PANEL (V2) PERMISSION MANAGEMENT ====================
#
# NOTE:
# This project already has a legacy `user_modulepermission` table with a different
# schema (columns like `can_add/can_view/...` and `module` instead of `module_id`).
# The newer control panel workflow (initialize modules/operations, per-operation
# permissions) needs a separate set of tables to avoid clashing with that legacy schema.


class CPModule(models.Model):
    """Control Panel module list (separate from legacy tables)."""

    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_cp_module"
        ordering = ["order", "display_name"]

    def __str__(self):
        return self.display_name


class CPModulePermission(models.Model):
    """Per-operation permissions for a CPModule (view/add/edit/etc.)."""

    OPERATION_CHOICES = [
        ("add", "Add"),
        ("view", "View"),
        ("edit", "Edit"),
        ("delete", "Delete"),
        ("export", "Export"),
        ("import", "Import"),
        ("approve", "Approve"),
        ("reject", "Reject"),
    ]

    module = models.ForeignKey(CPModule, on_delete=models.CASCADE, related_name="permissions")
    operation = models.CharField(max_length=50, choices=OPERATION_CHOICES)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_cp_modulepermission"
        unique_together = ["module", "operation"]
        ordering = ["module", "order", "operation"]

    def __str__(self):
        return f"{self.module.display_name} - {self.display_name}"


class CPUserModulePermission(models.Model):
    """Links a user to a CPModulePermission (granted/denied)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cp_module_permissions")
    module_permission = models.ForeignKey(
        CPModulePermission, on_delete=models.CASCADE, related_name="user_permissions"
    )
    granted = models.BooleanField(default=True)
    granted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="cp_granted_permissions"
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "user_cp_usermodulepermission"
        unique_together = ["user", "module_permission"]
        ordering = ["user", "module_permission__module", "module_permission__operation"]

    def __str__(self):
        status = "Granted" if self.granted else "Denied"
        return f"{self.user.username} - {self.module_permission} ({status})"


class CPPortal(models.Model):
    """
    High-level portal/dashboards grouping for permissions.
    Examples: Admin, Staff, Customer, Vendor.
    """

    name = models.CharField(max_length=50, unique=True)  # e.g. admin, staff, customer, vendor
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_cp_portal"
        ordering = ["order", "display_name"]

    def __str__(self):
        return self.display_name


class CPPortalModule(models.Model):
    """Assigns CPModules to a portal."""

    portal = models.ForeignKey(CPPortal, on_delete=models.CASCADE, related_name="portal_modules")
    module = models.ForeignKey(CPModule, on_delete=models.CASCADE, related_name="portals")
    order = models.IntegerField(default=0)

    class Meta:
        db_table = "user_cp_portal_module"
        unique_together = ["portal", "module"]
        ordering = ["portal", "order", "module__display_name"]

    def __str__(self):
        return f"{self.portal} -> {self.module}"


class CPUserPortalAccess(models.Model):
    """Per-user access to a portal/dashboard."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cp_portal_accesses")
    portal = models.ForeignKey(CPPortal, on_delete=models.CASCADE, related_name="user_accesses")
    granted = models.BooleanField(default=False)
    granted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="cp_portal_grants"
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_cp_userportalaccess"
        unique_together = ["user", "portal"]
        ordering = ["user", "portal"]

    def __str__(self):
        status = "Granted" if self.granted else "Denied"
        return f"{self.user} -> {self.portal} ({status})"


class VendorAccount(models.Model):
    """
    Links a `transactions.Vendor` to an `auth.User` so vendors can log in.
    """

    vendor = models.OneToOneField(
        "transactions.Vendor",
        on_delete=models.CASCADE,
        related_name="vendor_account",
        db_constraint=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_account",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VendorAccount({self.vendor_id_display()} -> {self.user})"

    def vendor_id_display(self):
        try:
            return self.vendor.vendor_id or str(self.vendor.pk)
        except Exception:
            return "unknown"


class CPNavItem(models.Model):
    """
    Menu/sub-module item under a portal, used to control sidebar visibility.

    Examples:
      - Dashboard -> Staff Dashboard (url_name='dashboard-index1')
      - Store Keeping -> Supplier List (url_name='suppliers-list')
    """

    key = models.CharField(max_length=150, unique=True)
    portal = models.ForeignKey(CPPortal, on_delete=models.CASCADE, related_name="nav_items")
    section = models.CharField(max_length=120)  # top-level menu name shown in UI
    label = models.CharField(max_length=150)  # sub-module label
    url_name = models.CharField(max_length=150, blank=True, default="")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_cp_navitem"
        ordering = ["portal__order", "section", "order", "label"]

    def __str__(self):
        return f"{self.portal.name}:{self.section}:{self.label}"


class CPUserNavAccess(models.Model):
    """Per-user access to a CPNavItem (sub-module/page link)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cp_nav_accesses")
    nav_item = models.ForeignKey(CPNavItem, on_delete=models.CASCADE, related_name="user_accesses")
    granted = models.BooleanField(default=False)
    granted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="cp_nav_grants"
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_cp_usernavaccess"
        unique_together = ["user", "nav_item"]
        ordering = ["user", "nav_item"]

    def __str__(self):
        status = "Granted" if self.granted else "Denied"
        return f"{self.user} -> {self.nav_item.key} ({status})"
