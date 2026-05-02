
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
from django.db import connection
from django.db.models import Max
from product.models import (
    SubCategory,
    Category,
    Unit,
    Product,
    category_for_fk_id,
    subcategory_for_fk_id,
    unit_for_fk_id,
)


class StockQuerySet(models.QuerySet):
    """
    Dropdown / form querysets only.

    Some PostgreSQL databases use ``BIT VARYING`` (legacy) for fields Django maps as
    ``BooleanField``. Then Django emits ``NOT column`` or ``column::boolean``, which
    PostgreSQL rejects. We filter with a text-based predicate that works for both
    real booleans and bit strings (e.g. ``B'0'`` / ``B'1'``).
    """

    def for_forms_dropdown(self):
        if connection.vendor != "postgresql":
            return self.filter(is_deleted=False)
        tbl = self.model._meta.db_table
        # "Not deleted": false, 0, empty, or legacy bit zero — exclude truthy tokens only.
        clause = (
            f"lower(btrim(COALESCE({tbl}.is_deleted::text, ''))) "
            f"NOT IN ('1', 'true', 't', 'yes', 'on')"
        )
        # extra() is deprecated but avoids invalid ::boolean casts on varbit columns.
        return self.extra(where=[clause])


class StockManager(models.Manager.from_queryset(StockQuerySet)):
    pass


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

    objects = StockManager()

    @property
    def safe_category(self):
        return category_for_fk_id(self.category_id)

    @property
    def safe_subcategory(self):
        return subcategory_for_fk_id(self.subcategory_id)

    @property
    def safe_purchase(self):
        return unit_for_fk_id(self.purchase_id)

    @property
    def safe_sales(self):
        return unit_for_fk_id(self.sales_id)

    def save(self, *args, **kwargs):
        # Same pattern as product.Product: DB sequence can lag behind max(id) and cause
        # duplicate-PK IntegrityError on insert.
        if self._state.adding:
            mx = Stock.objects.aggregate(m=Max("id"))["m"]
            self.pk = (mx or 0) + 1
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        # PostgreSQL: sequence/default missing → NULL id on INSERT (same as Stock).
        if self._state.adding:
            mx = FavoriteList.objects.aggregate(m=Max("id"))["m"]
            self.pk = (mx or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FavoriteListStock(models.Model):
    favorite_list = models.ForeignKey(FavoriteList, on_delete=models.CASCADE)
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self._state.adding:
            mx = FavoriteListStock.objects.aggregate(m=Max("id"))["m"]
            self.pk = (mx or 0) + 1
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('favorite_list', 'stock')

#
# class FavoriteList(models.Model):
#     # user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
#     name = models.CharField(max_length=255)
#     stocks = models.ManyToManyField(Stock)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True)



