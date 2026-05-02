from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max

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


def _next_primary_key(model_class, *, empty_table_start=None):
    """
    Next integer primary key = max(existing id) + 1.

    Use on first insert so new rows continue after the highest current id
    (avoids restarting at 1 when the DB sequence is out of sync).

    If the table is empty:
    - ``empty_table_start`` is used when provided (e.g. 101 for SubCategory).
    - Otherwise the first id is 1.
    """
    mx = model_class.objects.aggregate(m=Max("id"))["m"]
    if mx is None:
        return empty_table_start if empty_table_start is not None else 1
    return mx + 1


class CategoryQuerySet(models.QuerySet):
    """Active categories only."""

    def active_only(self):
        return self.filter(status=True)


class CategoryManager(models.Manager.from_queryset(CategoryQuerySet)):
    pass


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    short_name = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    status = models.BooleanField(default=True)

    objects = CategoryManager()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.pk = _next_primary_key(Category)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


def category_for_fk_id(category_id):
    """
    Resolve Category for a FK id without using the ForwardManyToOne descriptor's .get().
    If the DB has multiple rows for the same id (corrupt / legacy data), return the
    lowest-id row so templates and saves do not raise MultipleObjectsReturned.
    """
    if category_id is None:
        return None
    return Category.objects.filter(pk=category_id).order_by("id").first()


def subcategory_for_fk_id(subcategory_id):
    """Same as category_for_fk_id for SubCategory FKs (legacy duplicate rows)."""
    if subcategory_id is None:
        return None
    return SubCategory.objects.filter(pk=subcategory_id).order_by("id").first()


def unit_for_fk_id(unit_id):
    """Same pattern for Unit FKs on Stock (purchase/sales)."""
    if unit_id is None:
        return None
    return Unit.objects.filter(pk=unit_id).order_by("id").first()


class SubCategoryQuerySet(models.QuerySet):
    def active_only(self):
        return self.filter(status=True)


class SubCategoryManager(models.Manager.from_queryset(SubCategoryQuerySet)):
    pass


class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100, unique=True, null=True)  # Add this field for short names
    status = models.BooleanField(default=True)

    objects = SubCategoryManager()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.pk = _next_primary_key(SubCategory, empty_table_start=101)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def safe_category(self):
        return category_for_fk_id(self.category_id)


class Unit(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    # status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.pk = _next_primary_key(Unit)
        super().save(*args, **kwargs)

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
        if self._state.adding:
            self.pk = _next_primary_key(Product, empty_table_start=1001)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def safe_category(self):
        return category_for_fk_id(self.category_id)


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

    @property
    def safe_category(self):
        return category_for_fk_id(self.category_id)

    def save(self, *args, **kwargs):
        # Use category_id + safe lookup so corrupt duplicate Category rows never break save.
        if self.pk:
            previous_supplier = Supplier.objects.filter(pk=self.pk).first()
            previous_category_id = (
                previous_supplier.category_id if previous_supplier else None
            )
        else:
            previous_category_id = None

        cat = category_for_fk_id(self.category_id)
        short = (cat.short_name or "").upper() if cat else "CAT"

        # Generate supplier_id if it's a new record or if the category has changed
        if not self.supplier_id or self.category_id != previous_category_id:
            unique_supplier_id = False
            suffix = 101
            while not unique_supplier_id:
                last_qs = Supplier.objects.filter(
                    category_id=self.category_id
                ).order_by("id")
                if self.pk:
                    last_qs = last_qs.exclude(pk=self.pk)
                last_supplier = last_qs.last()
                if last_supplier:
                    last_id = int(last_supplier.supplier_id.split("-")[1])
                    proposed_supplier_id = f"{short}-{last_id + 1}"
                else:
                    proposed_supplier_id = f"{short}-{suffix}"

                dup_qs = Supplier.objects.filter(supplier_id=proposed_supplier_id)
                if self.pk:
                    dup_qs = dup_qs.exclude(pk=self.pk)
                if not dup_qs.exists():
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

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.pk = _next_primary_key(Brand)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

