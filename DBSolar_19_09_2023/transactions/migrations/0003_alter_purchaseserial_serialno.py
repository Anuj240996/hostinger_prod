# Generated migration to fix case-sensitivity issue for serialNo field
# PostgreSQL automatically lowercases column names, so we need to map to the existing lowercase column
# Since the database already has the correct column name, we only update Django's model state

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_alter_salebill_cust_id_alter_salebill_vend_id'),
    ]

    operations = [
        # Use SeparateDatabaseAndState to update only the model state without altering the database
        # The database already has the correct column name (serialno)
        migrations.SeparateDatabaseAndState(
            # Database operations: do nothing since column already exists correctly
            database_operations=[],
            # State operations: update the model to reflect the db_column mapping
            state_operations=[
                migrations.AlterField(
                    model_name='purchaseserial',
                    name='serialNo',
                    field=models.CharField(blank=True, db_column='serialno', max_length=50, null=True),
                ),
            ],
        ),
    ]

