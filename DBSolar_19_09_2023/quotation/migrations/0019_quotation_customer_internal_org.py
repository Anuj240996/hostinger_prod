import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quotation", "0018_quotation_discount_percentage"),
        ("core", "0002_add_default_data_to_existing_orgs"),
    ]

    operations = [
        migrations.AddField(
            model_name="quotation",
            name="customer_approval",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="quotation",
            name="internal_approval",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="quotation",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="erp_quotations",
                to="core.organization",
            ),
        ),
    ]
