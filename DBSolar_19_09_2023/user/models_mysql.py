from django.db import models
from django.contrib.auth.models import User, Permission

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

    #customer = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    #customer = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='profile')
    address = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=50, null=True)
    DOB = models.DateField(null=True)
    department = models.CharField(choices=[('Administration', 'Administration'), ('Stockist', 'Stockist'), ('Engineers', 'Engineers'), ('Finance', 'Finance')],max_length=50)
    image = models.ImageField(default='profile_images/default.png',upload_to='profile_pics', null=True, blank=True)
    designation = models.CharField(choices=[('Admin', 'Admin'), ('Sr.Cleark', 'Sr.Cleark'), ('Jr.Cleark', 'Jr.Cleark'), ('Accountant', 'Accountant'), ('Sr.Engg', 'Sr.Engg'), ('Jr.Engg', 'Jr.Engg')] , max_length=50,  null=True)
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
    emraddress = models.CharField(max_length=255, null=True)
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
