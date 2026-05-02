from django.contrib.auth.models import User
from django.db import models
from django.apps import apps


from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


# from django.db import models
#
#
# class Category(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     status = models.BooleanField(default=True)
#
#     def __str__(self):
#         return self.name
#
#
# class SubCategory(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     status = models.BooleanField(default=True)
#
#     def save(self, *args, **kwargs):
#         if not self.id:
#             last_subcategory = SubCategory.objects.all().order_by('id').last()
#             if last_subcategory:
#                 self.id = last_subcategory.id + 1
#             else:
#                 self.id = 101
#         super(SubCategory, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return self.name
#
# #
# # class Product(models.Model):
# #     category = models.ForeignKey(Category, on_delete=models.CASCADE)
# #     subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
# #     name = models.CharField(max_length=100)
# #     prod_description = models.TextField(blank=True, null=True)
# #     stock_alert = models.IntegerField(default=0)
# #     status = models.BooleanField(default=True)
# #
# #     def save(self, *args, **kwargs):
# #         if not self.id:
# #             last_product = Product.objects.all().order_by('id').last()
# #             if last_product:
# #                 self.id = last_product.id + 1
# #             else:
# #                 self.id = 1001
# #         super(Product, self).save(*args, **kwargs)
#
#
#
#     # def __str__(self):
#     #     return self.name
