from django.db import migrations, models


_RENAME_SERIAL_COLUMN_TO_CAMELCASE = """
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'transactions_purchaseserial'
      AND column_name = 'serialno'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'transactions_purchaseserial'
      AND column_name = 'serialNo'
  ) THEN
    ALTER TABLE transactions_purchaseserial RENAME COLUMN serialno TO "serialNo";
  END IF;
END $$;
"""


_RENAME_SERIAL_COLUMN_TO_LOWERCASE = """
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'transactions_purchaseserial'
      AND column_name = 'serialNo'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'transactions_purchaseserial'
      AND column_name = 'serialno'
  ) THEN
    ALTER TABLE transactions_purchaseserial RENAME COLUMN "serialNo" TO serialno;
  END IF;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0017_fix_salebill_fk_column_case_postgresql"),
    ]

    operations = [
        migrations.RunSQL(
            sql=_RENAME_SERIAL_COLUMN_TO_CAMELCASE,
            reverse_sql=_RENAME_SERIAL_COLUMN_TO_LOWERCASE,
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="purchaseserial",
                    name="serialNo",
                    field=models.CharField(
                        blank=True,
                        db_column="serialNo",
                        max_length=50,
                        null=True,
                    ),
                ),
            ],
        ),
    ]
