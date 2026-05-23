# Generated manually: allow optional short_name / blank name at model level

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0005_deduplicate_product_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(
                blank=True, max_length=100, null=True, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="short_name",
            field=models.CharField(
                blank=True, max_length=100, null=True, unique=True
            ),
        ),
    ]
