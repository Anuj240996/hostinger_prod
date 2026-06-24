from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0117_customer_mobile_app_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='mobile_app_linked_at',
            field=models.DateTimeField(blank=True, db_column='mobile_app_linked_at', null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='mobile_app_linked_username',
            field=models.CharField(blank=True, db_column='mobile_app_linked_username', max_length=150, null=True),
        ),
    ]
