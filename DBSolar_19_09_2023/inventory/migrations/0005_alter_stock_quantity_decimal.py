from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_fix_favoritelist_through_id_sequences'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=10),
        ),
    ]
