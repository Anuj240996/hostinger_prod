from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('firereport', '0022_resync_firetequesthistory_id_sequence'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceReportOtp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20)),
                ('otp_code', models.CharField(max_length=6)),
                ('message_text', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('sent_ok', models.BooleanField(default=False)),
                ('send_detail', models.CharField(blank=True, max_length=250, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_report_otps', to='auth.user')),
                ('service_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_otps', to='firereport.servicerequest')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
