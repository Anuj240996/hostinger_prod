# Generated manually for assigned_associate on Quotation

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("quotation", "0014_quotation_convert_consumer"),
    ]

    operations = [
        migrations.AddField(
            model_name="quotation",
            name="assigned_associate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_quotations",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Assign Associate",
            ),
        ),
    ]
