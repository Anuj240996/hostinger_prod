"""
Merge duplicate product.Category rows (same normalized name+short_name) and rewire FKs.
Used on add_category view so legacy/duplicate data cannot break ModelChoiceField.get().
"""

from django.db import transaction


def _rewire_category_fks(old_pk: int, new_pk: int) -> None:
    from product.models import SubCategory, Product, Supplier

    SubCategory.objects.filter(category_id=old_pk).update(category_id=new_pk)
    Product.objects.filter(category_id=old_pk).update(category_id=new_pk)
    Supplier.objects.filter(category_id=old_pk).update(category_id=new_pk)

    try:
        from inventory.models import Stock

        Stock.objects.filter(category_id=old_pk).update(category_id=new_pk)
    except Exception:
        pass

    try:
        from django.apps import apps

        for label in ("Supplier", "Vendor"):
            try:
                Model = apps.get_model("transactions", label)
                Model.objects.filter(category_id=old_pk).update(category_id=new_pk)
            except LookupError:
                pass
    except Exception:
        pass


def _norm_pair(cat) -> tuple:
    n = (cat.name or "").strip().lower()
    s = (cat.short_name or "").strip().lower()
    return (n, s)


@transaction.atomic
def merge_duplicate_product_categories() -> int:
    """
    Merge categories that share the same normalized (name, short_name).
    Returns number of duplicate rows removed.
    """
    from product.models import Category

    cats = list(Category.objects.all().order_by("id"))
    if len(cats) < 2:
        return 0

    groups = {}
    for c in cats:
        key = _norm_pair(c)
        groups.setdefault(key, []).append(c)

    removed = 0
    for key, group in groups.items():
        if len(group) < 2:
            continue
        keeper = group[0]
        for dup in group[1:]:
            _rewire_category_fks(dup.pk, keeper.pk)
            dup.delete()
            removed += 1
    return removed
