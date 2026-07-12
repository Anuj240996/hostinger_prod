from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("customer", "0122_resync_customer_result_id_sequence"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConsumerReleaseAgreement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pdf", models.FileField(blank=True, upload_to="release_agreements/%Y/%m/")),
                ("title", models.CharField(default="Release & Agreement", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_release_agreements",
                        to="auth.user",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        db_column="consumer_id_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="release_agreements",
                        to="customer.customer",
                    ),
                ),
                (
                    "result",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="release_agreements",
                        to="customer.result",
                    ),
                ),
            ],
            options={
                "verbose_name": "Consumer Release Agreement",
                "verbose_name_plural": "Consumer Release Agreements",
                "db_table": "customer_release_agreement",
                "ordering": ["-created_at"],
            },
        ),
    ]
