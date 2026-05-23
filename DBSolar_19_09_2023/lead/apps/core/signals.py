from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models import Organization
from .utils import add_default_data_for_organization
#
# # In apps/core/views.py, inside OrganizationWizard.done, after org.save()
# from .utils import add_default_data_for_organization
#
#
# @receiver(post_save, sender=Organization)
# def add_defaults_to_new_org(sender, instance, created, **kwargs):
#     if created:
#         add_default_data_for_organization(instance)
#
#
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Organization
from .utils import add_default_data_for_organization

@receiver(post_save, sender=Organization)
def add_defaults_to_new_org(sender, instance, created, **kwargs):
    if created:
        add_default_data_for_organization(instance)


@receiver(post_migrate)
def ensure_defaults_for_existing_orgs(sender, **kwargs):
    """
    Keep default CRM master data available after installation/migration.
    This is idempotent because add_default_data_for_organization uses get_or_create.
    """
    # Avoid running during non-core app migration signal emissions.
    if getattr(sender, "label", None) != "core":
        return

    for org in Organization.objects.all():
        add_default_data_for_organization(org)