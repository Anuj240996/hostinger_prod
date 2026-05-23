"""
Merge duplicate product.Category rows (same name) so FK lookups and unique checks work.
Keeps the lowest id per duplicate name; rewires FKs then deletes extras.

Safe on PostgreSQL/MySQL/SQLite (uses ORM only).
"""

from django.db import migrations
from django.db.models import Count


def _rewire_category_fks(apps, old_pk: int, new_pk: int) -> None:
    SubCategory = apps.get_model("product", "SubCategory")
    Product = apps.get_model("product", "Product")
    Supplier = apps.get_model("product", "Supplier")

    SubCategory.objects.filter(category_id=old_pk).update(category_id=new_pk)
    Product.objects.filter(category_id=old_pk).update(category_id=new_pk)
    Supplier.objects.filter(category_id=old_pk).update(category_id=new_pk)

    try:
        Stock = apps.get_model("inventory", "Stock")
        Stock.objects.filter(category_id=old_pk).update(category_id=new_pk)
    except LookupError:
        pass

    for label in ("Supplier", "Vendor"):
        try:
            TxModel = apps.get_model("transactions", label)
            TxModel.objects.filter(category_id=old_pk).update(category_id=new_pk)
        except LookupError:
            pass


def dedupe_categories_by_name(apps, schema_editor):
    Category = apps.get_model("product", "Category")

    dup_names = (
        Category.objects.exclude(name__isnull=True)
        .exclude(name="")
        .values("name")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
    )

    for row in dup_names:
        name = row["name"]
        cats = list(Category.objects.filter(name=name).order_by("id"))
        if len(cats) < 2:
            continue
        keeper = cats[0]
        for dup in cats[1:]:
            _rewire_category_fks(apps, dup.pk, keeper.pk)
            dup.delete()

    # Same short_name (can happen if name differed but short_name collided)
    dup_short = (
        Category.objects.exclude(short_name__isnull=True)
        .exclude(short_name="")
        .values("short_name")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
    )

    for row in dup_short:
        sn = row["short_name"]
        cats = list(Category.objects.filter(short_name=sn).order_by("id"))
        if len(cats) < 2:
            continue
        keeper = cats[0]
        for dup in cats[1:]:
            if dup.pk == keeper.pk:
                continue
            _rewire_category_fks(apps, dup.pk, keeper.pk)
            dup.delete()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0004_fix_product_id_sequences_postgresql"),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(dedupe_categories_by_name, noop_reverse),
    ]
