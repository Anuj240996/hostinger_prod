import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("user", "0016_resync_auth_user_and_profile_sequences"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="customer",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="image",
            field=models.ImageField(
                blank=True,
                default="profile_pics/default.png",
                null=True,
                upload_to="profile_pics",
            ),
        ),
    ]
