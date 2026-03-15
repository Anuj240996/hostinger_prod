from django.db import models
from django.contrib.auth.models import User
#
# # Create your models here.
# CATEGORY = (
#     ('Stationary', 'Stationary'),
#     ('Electronics', 'Electronics'),
#     ('Food', 'Food'),
# )
#
#
# class Product(models.Model):
#     name = models.CharField(max_length=100, null=True)
#     quantity = models.PositiveIntegerField(null=True)
#     #price = models.PositiveIntegerField(null=True)
#     category = models.CharField(max_length=50, choices=CATEGORY, null=True)
#
#     class Meta:
#         verbose_name_plural = 'Product'
#
#     def __str__(self):
#         return f'{self.name}-{self.quantity}'
#
#
# class Order(models.Model):
#     name = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
#     customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     order_quantity = models.PositiveIntegerField(null=True)
#     date = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         verbose_name_plural = 'Order'
#     def __str__(self):
#         return f'{self.customer}-{self.name}'
#
#
#     # product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
#     # staff = models.ForeignKey(User, models.CASCADE, null=True)
#     # order_quantity = models.PositiveIntegerField(null=True)
#     # date = models.DateTimeField(auto_now_add=True)
#     #
#     # class Meta:
#     #     verbose_name_plural = 'Order'
#     #
#     # def __str__(self):
#     #   return f'{self.product} ordered by {self.staff.username}'


#Create your models here.
import uuid

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
    phone = models.IntegerField(default=0)
    hire_date = models.DateField()

    def __str__(self):
        return "%s %s %s" %(self.first_name, self.last_name, self.phone)



class Emp_id(models.Model):
    name = models.CharField(max_length=100, null=False)
    def __str__(self):
        return self.name


class Customer(models.Model):
    new_customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    Cust_id = models.IntegerField(primary_key=True, null=False, default=uuid.uuid4())
    Comp_name = models.CharField(max_length=200, null=True)
    Consumer = models.CharField(max_length=100, null=True)
    Bill_unit = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    middle_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    Address = models.CharField(max_length=100, null=True)
    department = models.CharField(max_length=200, null=True)
    Plant_Capacity = models.IntegerField(default=0)
    Ups_Soft = models.CharField(max_length=100, null=True)
    #Cust_type = models.ForeignKey(Department, on_delete=models.CASCADE)
    Cust_type = models.CharField(max_length=100, null=True)
    City = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    phone = models.IntegerField(default=0)
    Cus_Act_Date = models.DateField()
    solar_comp = models.CharField(max_length=100, null=True)
    UPSC = models.CharField(max_length=100, null=True)
    Emp_id = models.IntegerField(default=0)
    state = models.CharField(max_length=100, null=True)
    Pincode = models.IntegerField(default=0)
    phase = models.IntegerField(default=1, null=True)
    loadsancution = models.IntegerField(default=0, null=True)

    # Gender = models.BooleanField("Gender",default=0)
    # Gender = (
    #     ('1', 'Male'),
    #     ('0', 'Female')
    # )
    Gender = models.CharField(max_length=1, null=True)
    class Meta:
        db_table ="customer"
    def __str__(self):
        return "%s %s %s %s" %(self.first_name, self.last_name, self.phone,self.Cust_id)

    # class Meta:
    #     verbose_name_plural = 'Customer'
    #
    # # def __str__(self):
    # #     return f'{self.name}-{self.quantity}'
    # def __str__(self):
    #     return "%s %s %s %s" %(self.first_name, self.last_name, self.phone,self.Cust_id)

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

