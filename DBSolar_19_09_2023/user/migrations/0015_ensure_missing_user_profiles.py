from django.db import migrations


def ensure_user_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('user', 'Profile')

    for user in User.objects.all().iterator():
        if Profile.objects.filter(customer_id=user.id).exists():
            continue
        Profile.objects.create(
            customer_id=user.id,
            department='Administration',
            designation='Staff',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_alter_profile_department_alter_profile_designation'),
    ]

    operations = [
        migrations.RunPython(ensure_user_profiles, migrations.RunPython.noop),
    ]
