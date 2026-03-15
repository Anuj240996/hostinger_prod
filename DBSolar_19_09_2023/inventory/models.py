
# from django.contrib.auth.models import User
# from django.db import models
# from django.apps import apps
# from django.db import models
# from django.contrib.auth.models import User
# from django.db import models
# from product.models import SubCategory, Category, Unit, Product

# class Stock(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100, unique=True)
#     quantity = models.IntegerField(default=1)
#     is_deleted = models.BooleanField(default=False)

#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
#     purchase = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='stock_purchased_products', null=True)
#     sales = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='stock_sold_products', null=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_products', null=True)
#     stock_alert = models.IntegerField(default=0)
#     gst = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
#     status = models.BooleanField(default=True, null=True)



#     def __str__(self):
#         return self.name


# class FavoriteList(models.Model):
#     name = models.CharField(max_length=100, unique=True, null=True)
#     stocks = models.ManyToManyField(Stock)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name






from django.contrib.auth.models import User
from django.db import models
from django.apps import apps
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from product.models import SubCategory, Category, Unit, Product

class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)  # Store final amount
    is_deleted = models.BooleanField(default=False)

#    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    purchase = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='stock_purchased_products', null=True)
    sales = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='stock_sold_products', null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_products', null=True)
    stock_alert = models.IntegerField(default=0)
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.BooleanField(default=True, null=True)



    def __str__(self):
        return self.name

#
# class FavoriteList(models.Model):
#     name = models.CharField(max_length=100, unique=True, null=True)
#     stocks = models.ManyToManyField(Stock)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.name



class FavoriteList(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=True)
    stocks = models.ManyToManyField('Stock', through='FavoriteListStock')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class FavoriteListStock(models.Model):
    favorite_list = models.ForeignKey(FavoriteList, on_delete=models.CASCADE)
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('favorite_list', 'stock')

#
# class FavoriteList(models.Model):
#     # user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
#     name = models.CharField(max_length=255)
#     stocks = models.ManyToManyField(Stock)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True)



