from django.contrib.auth.models import User
from django.db import models
from django.apps import apps

#
# from django.db import models
#
#
# class Category(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#
#     def __str__(self):
#         return self.name
#
# class SubCategory(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.name
#
# class Product(models.Model):
#     subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return self.name


from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=True)
    short_name = models.CharField(max_length=100, unique=True, null=True)  # Add this field for short names
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100, unique=True, null=True)  # Add this field for short names
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            last_subcategory = SubCategory.objects.all().order_by('id').last()
            if last_subcategory:
                self.id = last_subcategory.id + 1
            else:
                self.id = 101
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Unit(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    # status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='purchased_products', null=True)
    sales = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='sold_products', null=True)
    name = models.CharField(max_length=100, unique=True)
    prod_description = models.TextField(blank=True, null=True)
    stock_alert = models.IntegerField(default=0)
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            last_product = Product.objects.all().order_by('id').last()
            if last_product:
                self.id = last_product.id + 1
            else:
                self.id = 1001
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


#
# class Supplier(models.Model):
#     supplier_id = models.CharField(max_length=20, unique=True, blank=True)  # Custom ID field
#     supplier_name = models.CharField(max_length=100, unique=True)
#     contact_person = models.CharField(max_length=100)
#     contact_email = models.EmailField()
#     contact_phone = models.CharField(max_length=15)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     address = models.TextField()
#     city = models.CharField(max_length=50)
#     state = models.CharField(max_length=50)
#     post_code = models.CharField(max_length=10)
#     gst_no = models.CharField(max_length=15)
#     status = models.BooleanField(default=True)
#
#     def save(self, *args, **kwargs):
#         if not self.supplier_id:
#             last_supplier = Supplier.objects.filter(category=self.category).order_by('id').last()
#             if last_supplier:
#                 last_id = int(last_supplier.supplier_id.split('-')[1])
#                 self.supplier_id = f"{self.category.short_name.upper()}-{last_id + 1}"
#             else:
#                 self.supplier_id = f"{self.category.short_name.upper()}-101"
#         super(Supplier, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return self.supplier_name

class Supplier(models.Model):
    id = models.AutoField(primary_key=True)
    supplier_id = models.CharField(max_length=20, unique=True, blank=True)  # Custom ID field
    supplier_name = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    post_code = models.CharField(max_length=10)
    gst_no = models.CharField(max_length=15)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Check if the supplier exists and retrieve the previous category
        if self.pk:
            previous_supplier = Supplier.objects.get(pk=self.pk)
            previous_category = previous_supplier.category
        else:
            previous_category = None

        # Generate supplier_id if it's a new record or if the category has changed
        if not self.supplier_id or self.category != previous_category:
            # Loop until a unique supplier_id is generated
            unique_supplier_id = False
            suffix = 101
            while not unique_supplier_id:
                last_supplier = Supplier.objects.filter(category=self.category).order_by('id').last()
                if last_supplier:
                    last_id = int(last_supplier.supplier_id.split('-')[1])
                    proposed_supplier_id = f"{self.category.short_name.upper()}-{last_id + 1}"
                else:
                    proposed_supplier_id = f"{self.category.short_name.upper()}-{suffix}"

                # Check if this supplier_id already exists
                if not Supplier.objects.filter(supplier_id=proposed_supplier_id).exists():
                    self.supplier_id = proposed_supplier_id
                    unique_supplier_id = True
                else:
                    suffix += 1

        super(Supplier, self).save(*args, **kwargs)

    def __str__(self):
        return self.supplier_name



class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

