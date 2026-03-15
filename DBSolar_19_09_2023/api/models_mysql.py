# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ApiProject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        # managed = False
        db_table = 'api_project'



class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Customer(models.Model):
    comp_name = models.CharField(db_column='Comp_name', max_length=200, blank=True, null=True)  # Field name made lowercase.
    consumer = models.CharField(db_column='Consumer', max_length=100, blank=True, null=True)  # Field name made lowercase.
    current_load = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(db_column='Address', max_length=100, blank=True, null=True)  # Field name made lowercase.
    department = models.CharField(max_length=200, blank=True, null=True)
    plant_capacity = models.IntegerField(db_column='Plant_Capacity', blank=True)  # Field name made lowercase.
    ups_soft = models.CharField(db_column='Ups_Soft', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cust_type = models.CharField(db_column='Cust_type', max_length=100, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=100, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    solar_comp = models.CharField(max_length=100, blank=True, null=True)
    upsc = models.CharField(db_column='UPSC', max_length=100, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.IntegerField(db_column='Pincode',blank=True, null=True)  # Field name made lowercase.
    phase = models.IntegerField(blank=True, null=True)
    loadsancution = models.IntegerField(blank=True, null=True)
    po_date = models.DateField(blank=True, null=True)
    po_order = models.CharField(max_length=50, blank=True, null=True)
    qunt_solar = models.IntegerField(blank=True, null=True)
    qunt_inv = models.IntegerField(blank=True, null=True)
    gender = models.CharField(db_column='Gender', max_length=1, blank=True, null=True)  # Field name made lowercase.
    emp_id = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Emp_id_id')  # Field name made lowercase.
    engg_assign = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Engg_Assign_id', related_name='customer_engg_assign_set', blank=True, null=True)  # Field name made lowercase.
    new_customer = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='customer_new_customer_set', blank=True, null=True)
    cust_id = models.AutoField(db_column='Cust_id', primary_key=True)  # Field name made lowercase.
    com_warranty = models.IntegerField(blank=True, null=True)
    inv_warranty = models.IntegerField(blank=True, null=True)
    sol_warranty = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer'


class CustomerCustomerTechnicalDetails(models.Model):
    company_name = models.CharField(max_length=100)
    meter_image = models.CharField(max_length=100)
    netmeter_image = models.CharField(max_length=100)
    abt_meter_image = models.CharField(max_length=100)
    ct_cubic_image = models.CharField(max_length=100)
    assignby = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignBy_id', blank=True, null=True)  # Field name made lowercase.
    assignto = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignTo_id', related_name='customercustomertechnicaldetails_assignto_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'customer_customer_technical_details'


class CustomerDepartment(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'customer_department'


class CustomerEmpId(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'customer_emp_id'


class CustomerEmployee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    salary = models.IntegerField()
    bonus = models.IntegerField()
    phone = models.IntegerField()
    hire_date = models.DateField()
    dept = models.ForeignKey(CustomerDepartment, models.DO_NOTHING)
    role = models.ForeignKey('CustomerRole', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'customer_employee'


class CustomerGenerationct(models.Model):
    comp_name = models.CharField(max_length=255)
    make = models.CharField(max_length=255)
    capacity = models.CharField(max_length=255)
    serial_no = models.CharField(max_length=255)
    required = models.BooleanField()
    customer = models.ForeignKey(Customer, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'customer_generationct'


class CustomerGenerationmeter(models.Model):
    comp_name = models.CharField(max_length=255)
    make = models.CharField(max_length=255)
    serial_no = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    capacity = models.CharField(max_length=255)
    ct_make = models.CharField(db_column='CT_make', blank=True, null=True ,max_length=255)  # Field name made lowercase.
    ct_capacity = models.CharField(db_column='CT_capacity', blank=True, null=True,max_length=255)  # Field name made lowercase.
    ct_serial_no = models.CharField(db_column='CT_serial_no', blank=True, null=True,max_length=255)  # Field name made lowercase.
    assignby = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignBy_id', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'customer_generationmeter'


class CustomerInspectiondetail(models.Model):
    company_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    solar_module_completed = models.BooleanField(db_column='solar_Module_Completed')  # Field name made lowercase.
    solar_module_reason = models.CharField(db_column='solar_Module_Reason', blank=True, null=True,max_length=255)  # Field name made lowercase.
    solar_module_reason_other = models.CharField(db_column='solar_Module_Reason_other', blank=True, null=True, max_length=255)  # Field name made lowercase.
    inverter_completed = models.BooleanField(db_column='inverter_Completed')  # Field name made lowercase.
    inverter_reason = models.CharField(db_column='inverter_Reason', blank=True, null=True, max_length=255)  # Field name made lowercase.
    inverter_reason_other = models.CharField(db_column='inverter_Reason_other', blank=True, null=True, max_length=255)  # Field name made lowercase.
    net_meter_completed = models.BooleanField(db_column='net_Meter_Completed')  # Field name made lowercase.
    net_meter_reason = models.CharField(db_column='net_Meter_Reason', blank=True, null=True, max_length=255)  # Field name made lowercase.
    net_meter_reason_other = models.CharField(db_column='net_Meter_Reason_other', blank=True, null=True, max_length=255)  # Field name made lowercase.
    ct_completed = models.BooleanField(db_column='ct_Completed')  # Field name made lowercase.
    ct_reason = models.CharField(db_column='ct_Reason', blank=True, null=True, max_length=255)  # Field name made lowercase.
    ct_checkmark_other = models.CharField(db_column='ct_Checkmark_other', blank=True, null=True, max_length=255)  # Field name made lowercase.
    generation_meters_completed = models.BooleanField(db_column='generation_Meters_Completed')  # Field name made lowercase.
    generation_meters_reason = models.CharField(db_column='generation_Meters_Reason', blank=True, null=True, max_length=255)  # Field name made lowercase.
    generation_meters_reason_other = models.CharField(db_column='generation_Meters_Reason_other', blank=True, null=True,max_length=255)  # Field name made lowercase.
    gen_ct_meters_completed = models.BooleanField(db_column='gen_CT_Meters_Completed')  # Field name made lowercase.
    gen_ct_meters_reason = models.CharField(db_column='gen_CT_Meters_Reason', blank=True, null=True,max_length=255)  # Field name made lowercase.
    gen_ct_meters_reason_other = models.CharField(db_column='gen_CT_Meters_Reason_other', blank=True, null=True,max_length=255)  # Field name made lowercase.
    ac_panel_cabling_completed = models.BooleanField(db_column='ac_Panel_Cabling_Completed')  # Field name made lowercase.
    ac_panel_cabling_reason = models.CharField(db_column='ac_Panel_Cabling_Reason', blank=True, null=True,max_length=255)  # Field name made lowercase.
    ac_panel_cabling_reason_other = models.CharField(db_column='ac_Panel_Cabling_Reason_other', blank=True, null=True,max_length=255)  # Field name made lowercase.
    dc_panel_cabling_completed = models.BooleanField(db_column='dc_Panel_Cabling_Completed')  # Field name made lowercase.
    dc_panel_cabling_reason = models.CharField(db_column='dc_Panel_Cabling_Reason', blank=True, null=True,max_length=255)  # Field name made lowercase.
    dc_panel_cabling_reason_other = models.CharField(db_column='dc_Panel_Cabling_Reason_other', blank=True, null=True,max_length=255)  # Field name made lowercase.
    fabrication_completed = models.BooleanField(db_column='fabrication_Completed')  # Field name made lowercase.
    fabrication_reason = models.CharField(db_column='fabrication_Reason', blank=True, null=True,max_length=255)  # Field name made lowercase.
    fabrication_reason_other = models.CharField(db_column='fabrication_Reason_other', blank=True, null=True,max_length=255)  # Field name made lowercase.
    walkway_completed = models.BooleanField(db_column='walkway_Completed')  # Field name made lowercase.
    walkway_reason = models.CharField(db_column='walkway_Reason', blank=True, null=True,max_length=255)  # Field name made lowercase.
    walkway_reason_other = models.CharField(db_column='walkway_Reason_other', blank=True, null=True,max_length=255)  # Field name made lowercase.
    pipeline_completed = models.BooleanField(db_column='pipeline_Completed')  # Field name made lowercase.
    pipeline_reason = models.CharField(db_column='pipeline_Reason', blank=True, null=True,max_length=255)  # Field name made lowercase.
    pipeline_reason_other = models.CharField(db_column='pipeline_Reason_other', blank=True, null=True,max_length=255)  # Field name made lowercase.
    ropeway_completed = models.BooleanField(db_column='ropeway_Completed')  # Field name made lowercase.
    ropeway_reason = models.CharField(db_column='ropeway_Reason', blank=True, null=True,max_length=255)  # Field name made lowercase.
    ropeway_reason_other = models.CharField(db_column='ropeway_Reason_other', blank=True, null=True,max_length=255)  # Field name made lowercase.
    rolling_completed = models.BooleanField(db_column='rolling_Completed')  # Field name made lowercase.
    rolling_reason = models.CharField(db_column='rolling_Reason', blank=True, null=True,max_length=255)  # Field name made lowercase.
    rolling_reason_other = models.CharField(db_column='rolling_Reason_other', blank=True, null=True,max_length=255)  # Field name made lowercase.
    overall_details = models.TextField(db_column='overall_Details', blank=True, null=True,max_length=255)  # Field name made lowercase.
    info_correct = models.BooleanField(db_column='info_Correct')  # Field name made lowercase.
    assignby = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignBy_id', blank=True, null=True)  # Field name made lowercase.
    customer = models.ForeignKey(Customer, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer_inspectiondetail'


class CustomerMeter(models.Model):
    comp_name = models.CharField(db_column='Comp_name', max_length=255)  # Field name made lowercase.
    meters = models.CharField(max_length=50)
    m_meters_make = models.CharField(max_length=255)
    meters_capacity = models.CharField(max_length=255)
    meters_serial = models.CharField(max_length=255)
    meter_type = models.CharField(max_length=50)
    meter_make = models.CharField(max_length=255)
    meter_capacity = models.CharField(max_length=255)
    meter_serial = models.CharField(max_length=255)
    generation_meter_make = models.CharField(max_length=255)
    generation_meter_capacity = models.CharField(max_length=255)
    generation_meter_serial = models.CharField(max_length=255)
    generation_ct = models.CharField(max_length=50)
    generation_ct_make = models.CharField(max_length=255)
    generation_ct_capacity = models.CharField(max_length=255)
    generation_ct_serial = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'customer_meter'


class CustomerMeters(models.Model):
    comp_name = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    capacity = models.CharField(max_length=100)
    serial_no = models.CharField(max_length=20)
    transformer_type = models.CharField(max_length=50)
    meter_type = models.CharField(max_length=50)
    transformer_make = models.CharField(max_length=255)
    transformer_capacity = models.CharField(max_length=255)
    transformer_serial_number = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    assignby = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignBy_id', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'customer_meters'


class CustomerMseb(models.Model):
    comp_name = models.CharField(max_length=255)
    load_extension = models.BooleanField()
    flisibility = models.BooleanField()
    quotation = models.BooleanField()
    sent_to_bill = models.BooleanField()
    net_meter = models.BooleanField()
    flexibility = models.BooleanField()
    approval = models.BooleanField()
    meter_testing = models.BooleanField()
    agreement = models.BooleanField()
    release = models.BooleanField()
    installation_date = models.BooleanField()
    load_extension_date = models.DateTimeField(blank=True, null=True)
    flisibility_date = models.DateTimeField(blank=True, null=True)
    quotation_date = models.DateTimeField(blank=True, null=True)
    sent_to_bill_date = models.DateTimeField(blank=True, null=True)
    net_meter_date = models.DateTimeField(blank=True, null=True)
    flexibility_date = models.DateTimeField(blank=True, null=True)
    approval_date = models.DateTimeField(blank=True, null=True)
    meter_testing_date = models.DateTimeField(blank=True, null=True)
    agreement_date = models.DateTimeField(blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    installation_date_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING, blank=True, null=True)
    assignby = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignBy_id', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'customer_mseb'


class CustomerRole(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'customer_role'


class DashboardOrder(models.Model):
    name = models.ForeignKey('DashboardProduct', models.DO_NOTHING, blank=True, null=True)
    order_quantity = models.PositiveIntegerField(blank=True, null=True)
    date = models.DateTimeField()
    customer = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dashboard_order'


class DashboardProduct(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dashboard_product'


class DashboardStaffNotification(models.Model):
    message = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    staff_id = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)
    read = models.BooleanField()
    is_current = models.BooleanField()
    sender = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='dashboardstaffnotification_sender_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dashboard_staff_notification'


class DetectBarcodesBarcodeimage(models.Model):
    barcode_data = models.CharField(max_length=255)
    file_saved_at = models.DateTimeField()
    image = models.CharField(max_length=100)
    barcode_type = models.CharField(max_length=50)
    company = models.CharField(max_length=255, blank=True, null=True)
    wattage = models.CharField(max_length=50, blank=True, null=True)
    barcode_path = models.CharField(max_length=100)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    assignto = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignTo_id', blank=True, null=True)  # Field name made lowercase.
    assignby = models.IntegerField(db_column='AssignBy')  # Field name made lowercase.
    product_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detect_barcodes_barcodeimage'


class DetectBarcodesInverterimage(models.Model):
    barcode_data = models.CharField(max_length=255)
    file_saved_at = models.DateTimeField()
    image = models.CharField(max_length=100)
    barcode_type = models.CharField(max_length=50)
    company = models.CharField(max_length=255, blank=True, null=True)
    wattage = models.CharField(max_length=50, blank=True, null=True)
    barcode_path = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    assignby = models.IntegerField(db_column='AssignBy')  # Field name made lowercase.
    assignto = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignTo_id', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'detect_barcodes_inverterimage'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_flag = models.PositiveSmallIntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class FirereportFirereport(models.Model):
    fullname = models.CharField(db_column='FullName', blank=True, null=True,max_length=255)  # Field name made lowercase.
    mobilenumber = models.CharField(db_column='MobileNumber', blank=True, null=True,max_length=255)  # Field name made lowercase.
    location = models.CharField(db_column='Location', blank=True, null=True,max_length=255)  # Field name made lowercase.
    message = models.CharField(db_column='Message', blank=True, null=True,max_length=255)  # Field name made lowercase.
    status = models.CharField(db_column='Status', blank=True, null=True,max_length=255)  # Field name made lowercase.
    postingdate = models.DateTimeField(db_column='Postingdate')  # Field name made lowercase.
    assignedtime = models.CharField(db_column='AssignedTime', blank=True, null=True,max_length=255)  # Field name made lowercase.
    assignto = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignTo_id', blank=True, null=True)  # Field name made lowercase.
    assignby = models.IntegerField(db_column='AssignBy')  # Field name made lowercase.
    account_id = models.IntegerField(db_column='Account_id')  # Field name made lowercase.
    updationdate = models.DateTimeField(db_column='UpdationDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'firereport_firereport'


class FirereportFiretequesthistory(models.Model):
    status = models.CharField(blank=True, null=True,max_length=255)
    remark = models.CharField(blank=True, null=True,max_length=255)
    postingdate = models.DateTimeField(db_column='postingDate')  # Field name made lowercase.
    firereport = models.ForeignKey(FirereportFirereport, models.DO_NOTHING, blank=True, null=True)
    assignto = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='AssignTo_id', blank=True, null=True)  # Field name made lowercase.
    assignby = models.IntegerField(db_column='AssignBy')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'firereport_firetequesthistory'


class FirereportTeams(models.Model):
    teamname = models.CharField(db_column='teamName', max_length=200, blank=True, null=True)  # Field name made lowercase.
    teamleadername = models.CharField(db_column='teamLeaderName', max_length=250, blank=True, null=True)  # Field name made lowercase.
    teamleadmobno = models.CharField(db_column='teamLeadMobno', max_length=15, blank=True, null=True)  # Field name made lowercase.
    teammembers = models.CharField(db_column='teamMembers', max_length=300, blank=True, null=True)  # Field name made lowercase.
    postingdate = models.DateTimeField(db_column='postingDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'firereport_teams'


class InventoryFavoritelist(models.Model):
    name = models.CharField(unique=True, blank=True, null=True,max_length=100)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'inventory_favoritelist'


class InventoryFavoritelistStocks(models.Model):
    favoritelist = models.ForeignKey(InventoryFavoritelist, models.DO_NOTHING)
    stock = models.ForeignKey('InventoryStock', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inventory_favoritelist_stocks'


class InventoryStock(models.Model):
    name = models.CharField(unique=True, max_length=100)
    quantity = models.IntegerField()
    is_deleted = models.BooleanField()
    stock_alert = models.IntegerField()
    gst = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    status = models.BooleanField(blank=True, null=True)
    category = models.ForeignKey('ProductCategory', models.DO_NOTHING)
    product = models.ForeignKey('ProductProduct', models.DO_NOTHING, blank=True, null=True)
    purchase = models.ForeignKey('ProductUnit', models.DO_NOTHING, blank=True, null=True)
    sales = models.ForeignKey('ProductUnit', models.DO_NOTHING, related_name='inventorystock_sales_set', blank=True, null=True)
    subcategory = models.ForeignKey('ProductSubcategory', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inventory_stock'


class ProductBrand(models.Model):
    name = models.CharField(unique=True,max_length=255)
    status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'product_brand'


class ProductCategory(models.Model):
    name = models.CharField(unique=True, max_length=100, blank=True, null=True)
    short_name = models.CharField(unique=True, max_length=10, blank=True, null=True)
    status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'product_category'


class ProductProduct(models.Model):
    name = models.CharField(unique=True, max_length=100)
    prod_description = models.TextField(blank=True, null=True)
    stock_alert = models.IntegerField()
    gst = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    status = models.BooleanField()
    category = models.ForeignKey(ProductCategory, models.DO_NOTHING)
    purchase = models.ForeignKey('ProductUnit', models.DO_NOTHING, blank=True, null=True)
    sales = models.ForeignKey('ProductUnit', models.DO_NOTHING, related_name='productproduct_sales_set', blank=True, null=True)
    subcategory = models.ForeignKey('ProductSubcategory', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_product'


class ProductSubcategory(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(unique=True, max_length=10, blank=True, null=True)
    status = models.BooleanField()
    category = models.ForeignKey(ProductCategory, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_subcategory'


class ProductSupplier(models.Model):
    supplier_id = models.CharField(unique=True, max_length=20)
    supplier_name = models.CharField(unique=True, max_length=100)
    contact_person = models.CharField(max_length=100)
    contact_email = models.CharField(max_length=254)
    contact_phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    post_code = models.CharField(max_length=10)
    gst_no = models.CharField(max_length=15)
    status = models.BooleanField()
    category = models.ForeignKey(ProductCategory, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_supplier'


class ProductUnit(models.Model):
    name = models.CharField(unique=True, max_length=100)
    short_name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'product_unit'


class TransactionsFinalbilldetails(models.Model):
    eway = models.CharField(blank=True, null=True,max_length=255)
    veh = models.CharField(blank=True, null=True,max_length=255)
    destination = models.CharField(blank=True, null=True,max_length=255)
    po = models.CharField(blank=True, null=True,max_length=255)
    cgst = models.CharField(blank=True, null=True,max_length=255)
    sgst = models.CharField(blank=True, null=True,max_length=255)
    igst = models.CharField(blank=True, null=True,max_length=255)
    cess = models.CharField(blank=True, null=True,max_length=255)
    tcs = models.CharField(blank=True, null=True,max_length=255)
    total = models.CharField(blank=True, null=True,max_length=255)
    gst_value = models.CharField(blank=True, null=True,max_length=255)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    final_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    round_off = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    billno = models.ForeignKey('TransactionsFinalsale', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'transactions_finalbilldetails'


class TransactionsFinalsale(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    is_deleted = models.BooleanField()
    update_time = models.DateTimeField(blank=True, null=True)
    return_bill = models.BooleanField()
    return_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_finalsale'


class TransactionsFinalsaleitem(models.Model):
    unit_price = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total_price = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    final_bill = models.ForeignKey(TransactionsFinalsale, models.DO_NOTHING)
    stock = models.ForeignKey(InventoryStock, models.DO_NOTHING)
    total_quantity = models.IntegerField()
    r_quantity = models.IntegerField(blank=True, null=True)
    final_quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_finalsaleitem'


class TransactionsPurchasebill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField()
    supplier = models.ForeignKey('TransactionsSupplier', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'transactions_purchasebill'


class TransactionsPurchasebilldetails(models.Model):
    eway = models.CharField(blank=True, null=True,max_length=255)
    veh = models.CharField(blank=True, null=True,max_length=255)
    destination = models.CharField(blank=True, null=True,max_length=255)
    po = models.CharField(blank=True, null=True,max_length=255)
    cgst = models.CharField(blank=True, null=True,max_length=255)
    sgst = models.CharField(blank=True, null=True,max_length=255)
    igst = models.CharField(blank=True, null=True,max_length=255)
    cess = models.CharField(blank=True, null=True,max_length=255)
    tcs = models.CharField(blank=True, null=True,max_length=255)
    total = models.CharField(blank=True, null=True,max_length=255)
    billno = models.ForeignKey(TransactionsPurchasebill, models.DO_NOTHING)
    final_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    gst_value = models.CharField(blank=True, null=True,max_length=255)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    round_off = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        managed = False
        db_table = 'transactions_purchasebilldetails'


class TransactionsPurchaseitem(models.Model):
    quantity = models.IntegerField()
    perprice = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    billno = models.ForeignKey(TransactionsPurchasebill, models.DO_NOTHING)
    stock = models.ForeignKey(InventoryStock, models.DO_NOTHING)
    purchase = models.ForeignKey(ProductUnit, models.DO_NOTHING, blank=True, null=True)
    totalprice = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        managed = False
        db_table = 'transactions_purchaseitem'


class TransactionsPurchaseserial(models.Model):
    billno = models.ForeignKey(TransactionsPurchasebill, models.DO_NOTHING)
    purchase = models.ForeignKey(ProductUnit, models.DO_NOTHING)
    stock = models.ForeignKey(InventoryStock, models.DO_NOTHING)
    serialno = models.CharField(db_column='serialNo', blank=True, null=True,max_length=255)  # Field name made lowercase.
    item = models.ForeignKey(TransactionsPurchaseitem, models.DO_NOTHING, blank=True, null=True)
    sales_billno = models.ForeignKey('TransactionsSalebill', models.DO_NOTHING, blank=True, null=True)
    final_salebill = models.ForeignKey(TransactionsFinalsale, models.DO_NOTHING, blank=True, null=True)
    return_bill = models.ForeignKey('TransactionsReturnsale', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_purchaseserial'


class TransactionsReturnbilldetails(models.Model):
    eway = models.CharField(blank=True, null=True,max_length=255)
    veh = models.CharField(blank=True, null=True,max_length=255)
    destination = models.CharField(blank=True, null=True,max_length=255)
    po = models.CharField(blank=True, null=True,max_length=255)
    cgst = models.CharField(blank=True, null=True,max_length=255)
    sgst = models.CharField(blank=True, null=True,max_length=255)
    igst = models.CharField(blank=True, null=True,max_length=255)
    cess = models.CharField(blank=True, null=True,max_length=255)
    tcs = models.CharField(blank=True, null=True,max_length=255)
    total = models.CharField(blank=True, null=True,max_length=255)
    gst_value = models.CharField(blank=True, null=True,max_length=255)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    final_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    round_off = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    billno = models.ForeignKey('TransactionsReturnsale', models.DO_NOTHING)
    final_bill = models.ForeignKey(TransactionsFinalsale, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_returnbilldetails'


class TransactionsReturnsale(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    is_deleted = models.BooleanField()
    update_time = models.DateTimeField(blank=True, null=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    final_bill = models.ForeignKey(TransactionsFinalsale, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_returnsale'


class TransactionsReturnsaleitem(models.Model):
    unit_price = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total_price = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    return_bill = models.ForeignKey(TransactionsReturnsale, models.DO_NOTHING)
    stock = models.ForeignKey(InventoryStock, models.DO_NOTHING)
    final_bill = models.ForeignKey(TransactionsFinalsale, models.DO_NOTHING, blank=True, null=True)
    total_quantity = models.IntegerField()
    r_quantity = models.IntegerField(blank=True, null=True)
    final_quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_returnsaleitem'


class TransactionsSalebill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=255)
    email = models.CharField(max_length=30)
    gstin = models.CharField(max_length=255)
    cust_id = models.ForeignKey(Customer, models.DO_NOTHING, db_column='Cust_id_id')  # Field name made lowercase.
    final_salebill = models.ForeignKey(TransactionsFinalsale, models.DO_NOTHING, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'transactions_salebill'


class TransactionsSalebilldetails(models.Model):
    eway = models.CharField(blank=True, null=True,max_length=255)
    veh = models.CharField(blank=True, null=True,max_length=255)
    destination = models.CharField(blank=True, null=True,max_length=255)
    po = models.CharField(blank=True, null=True,max_length=255)
    cgst = models.CharField(blank=True, null=True,max_length=255)
    sgst = models.CharField(blank=True, null=True,max_length=255)
    igst = models.CharField(blank=True, null=True,max_length=255)
    cess = models.CharField(blank=True, null=True,max_length=255)
    tcs = models.CharField(blank=True, null=True,max_length=255)
    total = models.CharField(blank=True, null=True,max_length=255)
    billno = models.ForeignKey(TransactionsSalebill, models.DO_NOTHING)
    final_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    gst_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    gst_value = models.CharField(blank=True, null=True,max_length=255)
    round_off = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total_amount = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        managed = False
        db_table = 'transactions_salebilldetails'


class TransactionsSaleitem(models.Model):
    quantity = models.IntegerField()
    perprice = models.IntegerField(blank=True, null=True)
    totalprice = models.IntegerField(blank=True, null=True)
    billno = models.ForeignKey(TransactionsSalebill, models.DO_NOTHING)
    stock = models.ForeignKey(InventoryStock, models.DO_NOTHING)
    sale = models.ForeignKey(ProductUnit, models.DO_NOTHING, blank=True, null=True)
    r_quantity = models.IntegerField(blank=True, null=True)
    total_quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_saleitem'


class TransactionsSupplier(models.Model):
    phone = models.CharField(unique=True,max_length=255)
    address = models.CharField(max_length=255)
    email = models.CharField(unique=True,max_length=255)
    gstin = models.CharField(unique=True,max_length=255)
    is_deleted = models.BooleanField()
    category = models.ForeignKey(ProductCategory, models.DO_NOTHING)
    city = models.CharField(blank=True, null=True,max_length=255)
    contact_person = models.CharField(blank=True, null=True,max_length=255)
    post_code = models.CharField(blank=True, null=True,max_length=255)
    state = models.CharField(blank=True, null=True,max_length=255)
    status = models.BooleanField(blank=True, null=True)
    supplier_id = models.CharField(unique=True,max_length=255)
    name = models.CharField(unique=True,max_length=255)

    class Meta:
        managed = False
        db_table = 'transactions_supplier'


class UserPermission(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'user_permission'


class UserProfile(models.Model):
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    dob = models.DateField(db_column='DOB', blank=True, null=True)  # Field name made lowercase.
    department = models.CharField(max_length=50)
    image = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    last_updated_by = models.PositiveIntegerField(blank=True, null=True)
    workphone = models.CharField(max_length=50, blank=True, null=True)
    bg = models.CharField(max_length=50)
    city = models.CharField(max_length=50, blank=True, null=True)
    taluka = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    pg = models.CharField(max_length=50, blank=True, null=True)
    institution = models.CharField(max_length=50, blank=True, null=True)
    yop = models.DateField(blank=True, null=True)
    specili = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    emraddress = models.CharField(max_length=50, blank=True, null=True)
    customer = models.OneToOneField(AuthUser, models.DO_NOTHING, blank=True, null=True)
    rejoin_date = models.DateField(blank=True, null=True)
    rejoin_reason = models.CharField(max_length=150, blank=True, null=True)
    resign_date = models.DateField(blank=True, null=True)
    resign_reason = models.CharField(max_length=150, blank=True, null=True)
    resign_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_profile'


class UserProfilePermissions(models.Model):
    profile = models.ForeignKey(UserProfile, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_profile_permissions'
        unique_together = (('profile', 'permission'),)
