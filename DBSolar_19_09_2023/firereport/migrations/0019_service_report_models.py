from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('firereport', '0018_servicerequest_and_history'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceRemarkMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remark', models.CharField(max_length=250, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['remark'],
            },
        ),
        migrations.CreateModel(
            name='ServiceReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_date', models.DateField(blank=True, null=True)),
                ('report_time', models.TimeField(blank=True, null=True)),
                ('consumer_name', models.CharField(blank=True, max_length=250, null=True)),
                ('consumer_address', models.CharField(blank=True, max_length=300, null=True)),
                ('consumer_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('plant_capacity', models.CharField(blank=True, max_length=100, null=True)),
                ('load_sanction', models.CharField(blank=True, max_length=100, null=True)),
                ('phase_type', models.CharField(blank=True, default='single', max_length=20, null=True)),
                ('solar_module_make', models.CharField(blank=True, max_length=150, null=True)),
                ('solar_module_quantity', models.CharField(blank=True, max_length=50, null=True)),
                ('solar_module_capacity', models.CharField(blank=True, max_length=100, null=True)),
                ('inverter_make', models.CharField(blank=True, max_length=150, null=True)),
                ('inverter_quantity', models.CharField(blank=True, max_length=50, null=True)),
                ('inverter_capacity', models.CharField(blank=True, max_length=100, null=True)),
                ('ac_voltage_rn', models.CharField(blank=True, max_length=50, null=True)),
                ('ac_voltage_yn', models.CharField(blank=True, max_length=50, null=True)),
                ('ac_voltage_bn', models.CharField(blank=True, max_length=50, null=True)),
                ('ac_current_r', models.CharField(blank=True, max_length=50, null=True)),
                ('ac_current_y', models.CharField(blank=True, max_length=50, null=True)),
                ('ac_current_b', models.CharField(blank=True, max_length=50, null=True)),
                ('dc_rows_json', models.TextField(blank=True, null=True)),
                ('acdb_pn', models.CharField(blank=True, max_length=50, null=True)),
                ('acdb_ne', models.CharField(blank=True, max_length=50, null=True)),
                ('acdb_pn2', models.CharField(blank=True, max_length=50, null=True)),
                ('generation_today', models.CharField(blank=True, max_length=100, null=True)),
                ('generation_yesterday', models.CharField(blank=True, max_length=100, null=True)),
                ('generation_monthly', models.CharField(blank=True, max_length=100, null=True)),
                ('generation_yearly', models.CharField(blank=True, max_length=100, null=True)),
                ('remarks_text', models.TextField(blank=True, null=True)),
                ('import_units', models.CharField(blank=True, max_length=100, null=True)),
                ('export_units', models.CharField(blank=True, max_length=100, null=True)),
                ('meter_generation_units', models.CharField(blank=True, max_length=100, null=True)),
                ('consumer_sign_name', models.CharField(blank=True, max_length=200, null=True)),
                ('engg_sign_name', models.CharField(blank=True, max_length=200, null=True)),
                ('engg_id', models.CharField(blank=True, max_length=100, null=True)),
                ('engg_sign_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('service_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='service_report', to='firereport.servicerequest')),
            ],
        ),
    ]
