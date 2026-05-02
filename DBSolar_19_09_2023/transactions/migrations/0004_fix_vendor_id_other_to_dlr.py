from django.db import migrations


def fix_vendor_id_other_to_dlr(apps, schema_editor):
    Vendor = apps.get_model("transactions", "Vendor")
    qs_other = Vendor.objects.filter(vendor_id__startswith="OTHER-")
    qs_others = Vendor.objects.filter(vendor_id__startswith="OTHERS-")

    # Combine without duplicate processing
    other_ids = {v.pk for v in qs_other}
    candidates = list(qs_other) + [v for v in qs_others if v.pk not in other_ids]

    updated = 0
    skipped = 0

    def to_dlr(old_val: str):
        if not old_val:
            return None
        up = old_val.upper()
        if up.startswith("DLR-"):
            return old_val
        if up.startswith("OTHER-"):
            return "DLR-" + old_val.split("-", 1)[1]
        if up.startswith("OTHERS-"):
            return "DLR-" + old_val.split("-", 1)[1]
        return None

    for v in candidates:
        new_id = to_dlr(v.vendor_id)
        if not new_id or new_id == v.vendor_id:
            continue

        # Avoid unique constraint collisions
        if Vendor.objects.filter(vendor_id=new_id).exclude(pk=v.pk).exists():
            skipped += 1
            continue

        v.vendor_id = new_id
        v.save(update_fields=["vendor_id"])
        updated += 1

    print(f"[vendor_id_fix] updated={updated}, skipped_due_to_collision={skipped}")


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0003_alter_purchaseserial_serialno"),
    ]

    operations = [
        migrations.RunPython(fix_vendor_id_other_to_dlr, migrations.RunPython.noop),
    ]

