from __future__ import annotations

from django.db import migrations


def backfill_pending_status(apps, schema_editor):
    Firereport = apps.get_model("firereport", "Firereport")
    Firereport.objects.filter(Status__isnull=True).update(Status="Pending")
    Firereport.objects.filter(Status="").update(Status="Pending")


class Migration(migrations.Migration):
    dependencies = [
        ("firereport", "0005_alter_firereport_status"),
    ]

    operations = [
        migrations.RunPython(backfill_pending_status, reverse_code=migrations.RunPython.noop),
    ]

