# Fixed for fresh PostgreSQL DBs: skip integer -> uuid (cannot cast).
# Match models.Customer.Cust_id (BigAutoField).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0106_alter_customer_cust_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='Cust_id',
            field=models.BigAutoField(
                db_column='cust_id',
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
