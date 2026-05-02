# Generated migration to fix case-sensitivity issues for Cust_id and Vend_id fields
# PostgreSQL automatically lowercases column names, so we need to map to the existing lowercase columns
# Since the database already has the correct column names, we only update Django's model state

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
        ('customer', '0001_initial'),
    ]

    operations = [
        # Use SeparateDatabaseAndState to update only the model state without altering the database
        # The database already has the correct column names (cust_id_id, vend_id_id)
        migrations.SeparateDatabaseAndState(
            # Database operations: do nothing since columns already exist correctly
            database_operations=[],
            # State operations: update the model to reflect the db_column mapping
            state_operations=[
                migrations.AlterField(
                    model_name='salebill',
                    name='Cust_id',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='cust_id_id',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='salescustomer',
                        to='customer.customer'
                    ),
                ),
                migrations.AlterField(
                    model_name='salebill',
                    name='Vend_id',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='vend_id_id',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='salesvendor',
                        to='transactions.vendor'
                    ),
                ),
            ],
        ),
    ]

