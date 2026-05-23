from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("firereport", "0017_fix_firetequesthistory_postingdate_datetime"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("FullName", models.CharField(db_column="fullname", max_length=250, null=True)),
                ("MobileNumber", models.CharField(db_column="mobilenumber", max_length=12, null=True)),
                ("Location", models.CharField(db_column="Location", max_length=200, null=True)),
                ("Message", models.TextField(db_column="message", null=True)),
                ("Status", models.CharField(blank=True, db_column="status", default="In Process", max_length=150, null=True)),
                ("Postingdate", models.DateTimeField(auto_now_add=True, db_column="postingdate")),
                ("AssignedTime", models.DateTimeField(db_column="assignedtime", null=True)),
                ("UpdationDate", models.DateTimeField(db_column="updationdate", null=True)),
                ("complete_date", models.DateTimeField(db_column="complete_date", null=True)),
                ("Account_id", models.IntegerField(db_column="account_id", default=0)),
                ("AssignBy", models.IntegerField(db_column="assignby", default=0)),
                ("AssignTo", models.ForeignKey(db_column="assignto_id", null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="ServiceRequestHistory",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("status", models.CharField(max_length=200, null=True)),
                ("remark", models.CharField(max_length=250, null=True)),
                ("postingDate", models.DateTimeField(auto_now_add=True)),
                ("AssignBy", models.IntegerField(db_column="assignby", default=0)),
                ("AssignTo", models.ForeignKey(db_column="assignto_id", null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ("service_request", models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="firereport.servicerequest")),
            ],
        ),
    ]
