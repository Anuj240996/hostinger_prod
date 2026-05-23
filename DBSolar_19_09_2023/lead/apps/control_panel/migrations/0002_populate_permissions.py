from django.db import migrations

def create_permissions(apps, schema_editor):
    Permission = apps.get_model('control_panel', 'Permission')
    permissions = [
        # Lead
        {'codename': 'add_lead', 'name': 'Can add lead', 'app_label': 'leads', 'model': 'lead'},
        {'codename': 'change_lead', 'name': 'Can change lead', 'app_label': 'leads', 'model': 'lead'},
        {'codename': 'view_lead', 'name': 'Can view lead', 'app_label': 'leads', 'model': 'lead'},
        {'codename': 'delete_lead', 'name': 'Can delete lead', 'app_label': 'leads', 'model': 'lead'},
        # Pipeline
        {'codename': 'view_pipelinestage', 'name': 'Can view pipeline stage', 'app_label': 'pipeline', 'model': 'pipelinestage'},
        {'codename': 'change_pipelinestage', 'name': 'Can change pipeline stage', 'app_label': 'pipeline', 'model': 'pipelinestage'},
        # Survey
        {'codename': 'add_survey', 'name': 'Can add survey', 'app_label': 'surveys', 'model': 'survey'},
        {'codename': 'view_survey', 'name': 'Can view survey', 'app_label': 'surveys', 'model': 'survey'},
        {'codename': 'change_survey', 'name': 'Can change survey', 'app_label': 'surveys', 'model': 'survey'},
        {'codename': 'delete_survey', 'name': 'Can delete survey', 'app_label': 'surveys', 'model': 'survey'},
        # Quotation
        {'codename': 'add_quotation', 'name': 'Can add quotation', 'app_label': 'quotations', 'model': 'quotation'},
        {'codename': 'view_quotation', 'name': 'Can view quotation', 'app_label': 'quotations', 'model': 'quotation'},
        {'codename': 'change_quotation', 'name': 'Can change quotation', 'app_label': 'quotations', 'model': 'quotation'},
        {'codename': 'delete_quotation', 'name': 'Can delete quotation', 'app_label': 'quotations', 'model': 'quotation'},
        # Revenue
        {'codename': 'add_revenue', 'name': 'Can add revenue', 'app_label': 'revenue', 'model': 'revenue'},
        {'codename': 'view_revenue', 'name': 'Can view revenue', 'app_label': 'revenue', 'model': 'revenue'},
        {'codename': 'change_revenue', 'name': 'Can change revenue', 'app_label': 'revenue', 'model': 'revenue'},
        {'codename': 'delete_revenue', 'name': 'Can delete revenue', 'app_label': 'revenue', 'model': 'revenue'},
        # Analytics
        {'codename': 'view_analytics', 'name': 'Can view analytics', 'app_label': 'analytics', 'model': 'analytics'},
        # Sales Team
        {'codename': 'add_user', 'name': 'Can add user', 'app_label': 'auth', 'model': 'user'},
        {'codename': 'view_user', 'name': 'Can view user', 'app_label': 'auth', 'model': 'user'},
        {'codename': 'change_user', 'name': 'Can change user', 'app_label': 'auth', 'model': 'user'},
        {'codename': 'delete_user', 'name': 'Can delete user', 'app_label': 'auth', 'model': 'user'},
        # Settings
        {'codename': 'add_systemsetting', 'name': 'Can add system setting', 'app_label': 'settings', 'model': 'systemsetting'},
        {'codename': 'view_systemsetting', 'name': 'Can view system setting', 'app_label': 'settings', 'model': 'systemsetting'},
        {'codename': 'change_systemsetting', 'name': 'Can change system setting', 'app_label': 'settings', 'model': 'systemsetting'},
        {'codename': 'delete_systemsetting', 'name': 'Can delete system setting', 'app_label': 'settings', 'model': 'systemsetting'},
    ]
    for perm_data in permissions:
        Permission.objects.get_or_create(**perm_data)

class Migration(migrations.Migration):
    dependencies = [
        ('control_panel', '0001_initial'),  # replace with your actual last migration
    ]
    operations = [
        migrations.RunPython(create_permissions),
    ]