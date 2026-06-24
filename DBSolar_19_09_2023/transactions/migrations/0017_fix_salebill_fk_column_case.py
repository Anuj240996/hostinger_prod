# Production PostgreSQL uses mixed-case Cust_id_id / Vend_id_id (from legacy schema).
# Migration 0002 incorrectly mapped to lowercase; align Django state with the live DB.

from django.db import migrations, models
import django.db.models.deletion


_RENAME_LOWERCASE_FK_COLUMNS = """
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'transactions_salebill'
      AND column_name = 'cust_id_id'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'transactions_salebill'
      AND column_name = 'Cust_id_id'
  ) THEN
    ALTER TABLE transactions_salebill RENAME COLUMN cust_id_id TO "Cust_id_id";
  END IF;

  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'transactions_salebill'
      AND column_name = 'vend_id_id'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'transactions_salebill'
      AND column_name = 'Vend_id_id'
  ) THEN
    ALTER TABLE transactions_salebill RENAME COLUMN vend_id_id TO "Vend_id_id";
  END IF;
END $$;
"""

_RENAME_MIXEDCASE_FK_COLUMNS_BACK = """
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'transactions_salebill'
      AND column_name = 'Cust_id_id'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'transactions_salebill'
      AND column_name = 'cust_id_id'
  ) THEN
    ALTER TABLE transactions_salebill RENAME COLUMN "Cust_id_id" TO cust_id_id;
  END IF;

  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'transactions_salebill'
      AND column_name = 'Vend_id_id'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'transactions_salebill'
      AND column_name = 'vend_id_id'
  ) THEN
    ALTER TABLE transactions_salebill RENAME COLUMN "Vend_id_id" TO vend_id_id;
  END IF;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0016_fix_purchase_details_and_item_id_sequences'),
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=_RENAME_LOWERCASE_FK_COLUMNS,
            reverse_sql=_RENAME_MIXEDCASE_FK_COLUMNS_BACK,
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='salebill',
                    name='Cust_id',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='Cust_id_id',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='salescustomer',
                        to='customer.customer',
                    ),
                ),
                migrations.AlterField(
                    model_name='salebill',
                    name='Vend_id',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='Vend_id_id',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='salesvendor',
                        to='transactions.vendor',
                    ),
                ),
            ],
        ),
    ]
