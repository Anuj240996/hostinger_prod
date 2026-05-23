from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quotation", "0017_quotation_replace_crm_merge_with_slim_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="quotation",
            name="discount_percentage",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=5,
                null=True,
                verbose_name="Discount (%)",
            ),
        ),
    ]
