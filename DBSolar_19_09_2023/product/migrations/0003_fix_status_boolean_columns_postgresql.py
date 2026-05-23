"""
PostgreSQL: product_* ``status`` columns may be bit varying while Django sends boolean.
Same pattern as customer.0111 / customer.0113.

Safe to re-run: only alters columns that are still udt_name = 'varbit'.
"""

from django.db import migrations


# Django default table names for product app models with BooleanField ``status``
PRODUCT_STATUS_TABLES = (
    "product_category",
    "product_subcategory",
    "product_product",
    "product_brand",
    "product_supplier",
)


def _is_varbit_column(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(
        """
        SELECT c.udt_name
        FROM information_schema.columns c
        WHERE c.table_schema = current_schema()
          AND c.table_name = %s
          AND c.column_name = %s
        """,
        [table_name, column_name],
    )
    row = cursor.fetchone()
    return bool(row and row[0] == "varbit")


def alter_product_status_varbit_to_boolean(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != "postgresql":
        return

    with connection.cursor() as cursor:
        for table in PRODUCT_STATUS_TABLES:
            if not _is_varbit_column(cursor, table, "status"):
                continue
            cursor.execute(
                f"""
                ALTER TABLE "{table}"
                ALTER COLUMN "status" TYPE boolean USING (
                    CASE
                        WHEN "status" IS NULL OR bit_length("status") = 0 THEN true
                        ELSE get_bit("status", 0) = 1
                    END
                );
                """
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0002_alter_brand_id_alter_category_id_alter_product_id_and_more"),
    ]

    operations = [
        migrations.RunPython(alter_product_status_varbit_to_boolean, noop_reverse),
    ]
