from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0116_customer_assoc_assign'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='mobile_app_password',
            field=models.CharField(blank=True, db_column='mobile_app_password', max_length=128, null=True),
        ),
    ]
