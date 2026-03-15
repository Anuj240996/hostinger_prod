# Generated migration to convert date fields to DateTimeField

from django.db import migrations, models, connection
from django.utils import timezone
from datetime import datetime
import re


def check_column_exists(table_name, column_name):
    """Check if a column exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name=%s AND column_name=%s
        """, [table_name, column_name])
        return cursor.fetchone() is not None


def add_fields_if_not_exists(apps, schema_editor):
    """Add date fields only if they don't already exist"""
    db_table = 'firereport_firereport'
    
    if not check_column_exists(db_table, 'progress_date'):
        with connection.cursor() as cursor:
            cursor.execute(f'ALTER TABLE {db_table} ADD COLUMN progress_date TIMESTAMP NULL')
    
    if not check_column_exists(db_table, 'working_date'):
        with connection.cursor() as cursor:
            cursor.execute(f'ALTER TABLE {db_table} ADD COLUMN working_date TIMESTAMP NULL')
    
    if not check_column_exists(db_table, 'complete_date'):
        with connection.cursor() as cursor:
            cursor.execute(f'ALTER TABLE {db_table} ADD COLUMN complete_date TIMESTAMP NULL')


def noop_reverse(apps, schema_editor):
    """No-op reverse function"""
    pass


def convert_assignedtime_to_datetime(apps, schema_editor):
    """Convert AssignedTime from CharField to DateTimeField"""
    Firereport = apps.get_model("firereport", "Firereport")
    
    def _to_datetime(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value if timezone.is_aware(value) else timezone.make_aware(value)
        if isinstance(value, str):
            txt = value.strip()
            if not txt:
                return None
            # Normalize timezone offsets
            if re.search(r"[+-]\d{2}$", txt):
                txt = txt + ":00"
            elif re.search(r"[+-]\d{4}$", txt):
                txt = txt[:-2] + ":" + txt[-2:]
            # Handle ISO 8601 strings
            try:
                iso_txt = txt.replace("Z", "+00:00")
                parsed = datetime.fromisoformat(iso_txt)
                return timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed
            except Exception:
                pass
            # Try common formats
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(txt, fmt)
                    return timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed
                except Exception:
                    continue
        return None
    
    # Convert existing CharField values to DateTimeField
    for fr in Firereport.objects.all():
        if fr.AssignedTime:
            dt = _to_datetime(fr.AssignedTime)
            if dt:
                Firereport.objects.filter(id=fr.id).update(AssignedTime=dt)


def reverse_convert_assignedtime(apps, schema_editor):
    """Reverse: Convert DateTimeField back to CharField (for rollback)"""
    Firereport = apps.get_model("firereport", "Firereport")
    for fr in Firereport.objects.all():
        if fr.AssignedTime:
            dt_str = fr.AssignedTime.strftime("%d/%m/%Y %H:%M:%S")
            Firereport.objects.filter(id=fr.id).update(AssignedTime=dt_str)


class Migration(migrations.Migration):

    dependencies = [
        ('firereport', '0011_alter_firetequesthistory_postingdate'),
    ]

    operations = [
        # Step 1: Add new DateTimeField columns (nullable)
        # Use SeparateDatabaseAndState to handle existing columns in DB
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # Only add columns if they don't exist
                migrations.RunPython(add_fields_if_not_exists, noop_reverse),
            ],
            state_operations=[
                # Update Django's migration state
                migrations.AddField(
                    model_name='firereport',
                    name='progress_date',
                    field=models.DateTimeField(null=True, db_column='progress_date'),
                ),
                migrations.AddField(
                    model_name='firereport',
                    name='working_date',
                    field=models.DateTimeField(null=True, db_column='working_date'),
                ),
                migrations.AddField(
                    model_name='firereport',
                    name='complete_date',
                    field=models.DateTimeField(null=True, db_column='complete_date'),
                ),
            ],
        ),
        # Step 2: Convert AssignedTime from CharField to DateTimeField
        migrations.AlterField(
            model_name='firereport',
            name='AssignedTime',
            field=models.DateTimeField(null=True, db_column='assignedtime'),
        ),
        # Step 3: Convert existing data
        migrations.RunPython(convert_assignedtime_to_datetime, reverse_convert_assignedtime),
        # Note: Text fields (postingdate_text, assignedtime_text, etc.) are not removed here
        # because they don't exist in the model definition. If they exist in the database,
        # they can be removed manually via SQL or a separate migration after checking the database schema.
    ]
