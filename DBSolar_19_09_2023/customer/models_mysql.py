from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+?\d{10,12}$',
    message="Phone number must be 10 to 12 digits long and may start with '+'.")



#Create your models here.


class Department(models.Model):
    name = models.CharField(max_length=100,null=False)
    location = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100, null=False)
    def __str__(self):
        return self.name

class Employee(models.Model):
   # Emp_id= models.IntegerField(unique=True)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    salary = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    phone = models.CharField(validators=[phone_regex],max_length=13,blank=True,null=True)

#    phone = models.IntegerField(default=0)
    hire_date = models.DateField()

    def __str__(self):
        return "%s %s %s" %(self.first_name, self.last_name, self.phone)



class Emp_id(models.Model):
    name = models.CharField(max_length=100, null=False)
    def __str__(self):
        return self.name


class Customer(models.Model):
    #new_customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    new_customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='new_customer_customers')
    Engg_Assign = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='engg_assign_customers')
    Cust_id = models.IntegerField(primary_key=True, null=False, default=uuid.uuid4())
    Comp_name = models.CharField(max_length=200, null=True)
    Consumer = models.CharField(max_length=100, null=True)
    current_load = models.IntegerField(default=0, null=True)
    first_name = models.CharField(max_length=100, null=True)
    middle_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    Address = models.CharField(max_length=255, null=True)
    department = models.CharField(max_length=200, null=True)
    Plant_Capacity = models.IntegerField(default=0)
    Ups_Soft = models.CharField(max_length=100, null=True)
    #Cust_type = models.ForeignKey(Department, on_delete=models.CASCADE)
    Cust_type = models.CharField(max_length=100, null=True)
    City = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(validators=[phone_regex],max_length=13,blank=True,null=True)
    # phone = models.IntegerField(default=0)
    # Cus_Act_Date = models.DateField(null=True, default=None)
    solar_comp = models.CharField(max_length=100, null=True)
    UPSC = models.CharField(max_length=100, null=True)
    # Emp_id = models.IntegerField(default=0)
    Emp_id = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=100, null=True)
    Pincode = models.IntegerField(default=0)
    phase = models.IntegerField(default=1, null=True)
    loadsancution = models.IntegerField(default=0, null=True)
    po_date = models.DateField(null=True, default=None)
    po_order = models.CharField(max_length=100, null=True)


    qunt_solar = models.IntegerField(default=0)
    qunt_inv = models.IntegerField(default=0)
    inv_warranty = models.IntegerField(default=0, null=True)
    sol_warranty = models.IntegerField(default=0, null=True)
    com_warranty = models.IntegerField(default=0, null=True)
    project_type = models.CharField(max_length=100, null=True)
    solar_pump = models.CharField(max_length=100, null=True)
    pump_qunt = models.IntegerField(default=0, null=True)
    pump_warranty = models.IntegerField(default=0, null=True)
    advance_paid = models.CharField(max_length=10,default='not_paid')

    Gender = models.CharField(max_length=1, null=True)
    class Meta:
        db_table ="customer"
    def __str__(self):
        return "%s %s %s %s" %(self.first_name, self.last_name, self.phone,self.Cust_id)



class customer_technical_Details(models.Model):
        company_name = models.CharField(max_length=100)
        #solar_panel_no = models.IntegerField()
        #detected_barcode = models.CharField(max_length=100)
        #detected_inverter = models.CharField(max_length=100)
        meter_image = models.ImageField(upload_to='meter_images/')
        netmeter_image = models.ImageField(upload_to='netmeter_images/')
        abt_meter_image = models.ImageField(upload_to='abt_meter_images/')
        ct_cubic_image = models.ImageField(upload_to='ct_cubic_images/')
        AssignTo = models.ForeignKey(User, related_name='assign_to', on_delete=models.SET_NULL, null=True)
        AssignBy = models.ForeignKey(User, related_name='assign_by', on_delete=models.SET_NULL, null=True)

class Meter(models.Model):
    Comp_name = models.CharField(max_length=255)
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

class Meters(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='meters')
    comp_name = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    capacity = models.CharField(max_length=50)
    serial_no = models.CharField(max_length=20)
    transformer_type = models.CharField(max_length=50)
    meter_type = models.CharField(max_length=50)
    transformer_make = models.CharField(max_length=255)
    transformer_capacity = models.CharField(max_length=255)
    transformer_serial_number = models.CharField(max_length=255)
    AssignBy = models.ForeignKey(User, related_name='meters_assigned_by', on_delete=models.SET_NULL, null=True)


class GenerationMeter(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='generation_meters')
    comp_name = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    capacity = models.CharField(max_length=50)
    serial_no = models.CharField(max_length=20)
    CT_make = models.CharField(max_length=100, null=True)
    CT_capacity = models.CharField(max_length=50, null=True)
    CT_serial_no = models.CharField(max_length=20, null=True)
    AssignBy = models.ForeignKey(User, related_name='generation_meters_assigned_by', on_delete=models.SET_NULL, null=True)


class GenerationCT(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='generation_cts')
    comp_name = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    capacity = models.CharField(max_length=50)
    serial_no = models.CharField(max_length=20)
    required = models.BooleanField()


class MSEB(models.Model):
    # customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='mseb_data', null=True)
    comp_name = models.CharField(max_length=100)
    load_extension = models.BooleanField(default=False)
    flisibility = models.BooleanField(default=False)
    quotation = models.BooleanField(default=False)
    sent_to_bill = models.BooleanField(default=False)
    net_meter = models.BooleanField(default=False)
    flexibility = models.BooleanField(default=False)
    approval = models.BooleanField(default=False)
    meter_testing = models.BooleanField(default=False)
    agreement = models.BooleanField(default=False)
    release = models.BooleanField(default=False)
    installation_date = models.BooleanField(default=False)

    load_extension_date = models.DateTimeField(null=True, blank=True)
    flisibility_date = models.DateTimeField(null=True)
    quotation_date = models.DateTimeField(null=True)
    sent_to_bill_date = models.DateTimeField(null=True)
    net_meter_date = models.DateTimeField(null=True)
    flexibility_date = models.DateTimeField(null=True)
    approval_date = models.DateTimeField(null=True)
    meter_testing_date = models.DateTimeField(null=True)
    agreement_date = models.DateTimeField(null=True)
    release_date = models.DateTimeField(null=True)
    installation_date_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(null=True)
    AssignBy = models.ForeignKey(User, related_name='MSEB_assigned_by', on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return self.comp_name


class SolarPump(models.Model):
    serial_no = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField()
    pump_company = models.CharField(max_length=255, null=True)
    pump_hp = models.CharField(max_length=50, null=True)
    item_type = models.CharField(max_length=100, null=True)
    consumer = models.CharField(max_length=255, null=True)
    consumer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, related_name='consumer_id')
    AssignTo = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='consumer')
    AssignBy = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='fillup_By')


    def __str__(self):
        return self.consumer


class Controller(models.Model):
    serial_no = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField()
    pump_company = models.CharField(max_length=255, null=True)
    pump_hp = models.CharField(max_length=50, null=True)
    item_type = models.CharField(max_length=100, null=True)
    consumer = models.CharField(max_length=255, null=True)
    consumer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, related_name='consumer_id_controller')
    AssignTo = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='consumer_controller')
    AssignBy = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='fillup_By_controller')


    def __str__(self):
        return self.consumer




class InspectionDetail(models.Model):
    company_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='data', null=True)
    AssignBy = models.ForeignKey(User, related_name='data_assigned_by', on_delete=models.SET_NULL,null=True)
    solar_Module_Completed = models.BooleanField(default=False)
    solar_Module_Reason = models.CharField(max_length=255, blank=True, null=True)
    solar_Module_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    inverter_Completed = models.BooleanField(default=False)
    inverter_Reason = models.CharField(max_length=255, blank=True, null=True)
    inverter_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    net_Meter_Completed = models.BooleanField(default=False)
    net_Meter_Reason = models.CharField(max_length=255, blank=True, null=True)
    net_Meter_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    ct_Completed = models.BooleanField(default=False)
    ct_Reason = models.CharField(max_length=255, blank=True, null=True)
    ct_Checkmark_other = models.CharField(max_length=255, blank=True, null=True)
    generation_Meters_Completed = models.BooleanField(default=False)
    generation_Meters_Reason = models.CharField(max_length=255, blank=True, null=True)
    generation_Meters_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    gen_CT_Meters_Completed = models.BooleanField(default=False)
    gen_CT_Meters_Reason = models.CharField(max_length=255, blank=True, null=True)
    gen_CT_Meters_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    ac_Panel_Cabling_Completed = models.BooleanField(default=False)
    ac_Panel_Cabling_Reason = models.CharField(max_length=255, blank=True, null=True)
    ac_Panel_Cabling_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    dc_Panel_Cabling_Completed = models.BooleanField(default=False)
    dc_Panel_Cabling_Reason = models.CharField(max_length=255, blank=True, null=True)
    dc_Panel_Cabling_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    fabrication_Completed = models.BooleanField(default=False)
    fabrication_Reason = models.CharField(max_length=255, blank=True, null=True)
    fabrication_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    walkway_Completed = models.BooleanField(default=False)
    walkway_Reason = models.CharField(max_length=255, blank=True, null=True)
    walkway_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    pipeline_Completed = models.BooleanField(default=False)
    pipeline_Reason = models.CharField(max_length=255, blank=True, null=True)
    pipeline_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    ropeway_Completed = models.BooleanField(default=False)
    ropeway_Reason = models.CharField(max_length=255, blank=True, null=True)
    ropeway_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    rolling_Completed = models.BooleanField(default=False)
    rolling_Reason = models.CharField(max_length=255, blank=True, null=True)
    rolling_Reason_other = models.CharField(max_length=255, blank=True, null=True)
    overall_Details = models.TextField(blank=True, null=True)
    info_Correct = models.BooleanField(default=False)


    def __str__(self):
        return self.company_name



class Result(models.Model):
    consumer = models.CharField(max_length=255, null=True)
    consumer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, related_name='consumer_id_result')
    AssignTo = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='consumer_userid')
    solar_panel = models.BooleanField(default=False)
    inverter = models.BooleanField(default=False)
    net_meter = models.BooleanField(default=False)
    mseb = models.BooleanField(default=False)
    solar_pump = models.BooleanField(default=False)
    controller = models.BooleanField(default=False)
    inspection_report = models.BooleanField(default=False)

    def __str__(self):
        return self.consumer


