# Columns added at runtime by db_solar_app Node backend for mobile complaints/services
from django.db import migrations


FIREREPORT_MOBILE_COLUMNS_SQL = r"""
ALTER TABLE firereport_firereport ADD COLUMN IF NOT EXISTS category VARCHAR(255);
ALTER TABLE firereport_firereport ADD COLUMN IF NOT EXISTS title VARCHAR(255);
ALTER TABLE firereport_firereport ADD COLUMN IF NOT EXISTS warranty_type TEXT;
ALTER TABLE firereport_firereport ADD COLUMN IF NOT EXISTS app_user_id INTEGER;
ALTER TABLE firereport_firereport ADD COLUMN IF NOT EXISTS progress_date TIMESTAMP;
ALTER TABLE firereport_firereport ADD COLUMN IF NOT EXISTS working_date TIMESTAMP;
ALTER TABLE firereport_firereport ADD COLUMN IF NOT EXISTS complete_date TIMESTAMP;

ALTER TABLE firereport_servicerequest ADD COLUMN IF NOT EXISTS app_user_id INTEGER;
ALTER TABLE firereport_servicerequest ADD COLUMN IF NOT EXISTS service_type TEXT;
ALTER TABLE firereport_servicerequest ADD COLUMN IF NOT EXISTS additional_notes TEXT;
ALTER TABLE firereport_servicerequest ADD COLUMN IF NOT EXISTS warranty_type TEXT;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('firereport', '0019_service_report_models'),
    ]

    operations = [
        migrations.RunSQL(
            sql=FIREREPORT_MOBILE_COLUMNS_SQL,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
