import json
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog
from apps.core.models import Organization
from .models import Role, Feature, SubscriptionPlan, OrganizationSubscription, OrganizationFeature
from .middleware import get_current_user

# Helper to store the old instance before save (for change tracking)
def store_pre_save_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._pre_save_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass

def get_changed_fields(instance):
    """Returns a dict of changed fields for an instance that has a _pre_save_instance attribute."""
    if not hasattr(instance, '_pre_save_instance'):
        return None
    old = instance._pre_save_instance
    new = instance
    changes = {}
    for field in instance._meta.fields:
        if field.name in ['id', 'created_at', 'updated_at']:
            continue
        old_val = getattr(old, field.name)
        new_val = getattr(new, field.name)
        if old_val != new_val:
            # Convert to serializable types
            if hasattr(old_val, 'isoformat'):
                old_val = old_val.isoformat()
                new_val = new_val.isoformat()
            changes[field.name] = {'old': str(old_val), 'new': str(new_val)}
    return changes if changes else None

def log_action(sender, instance, created=False, **kwargs):
    user = get_current_user()
    action = 'CREATE' if created else 'UPDATE'
    changes = None if created else get_changed_fields(instance)
    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance),
        changes=changes,
    )

def log_delete(sender, instance, **kwargs):
    user = get_current_user()
    AuditLog.objects.create(
        user=user,
        action='DELETE',
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance),
        changes=None,
    )

def connect_signals():
    models_to_audit = [
        Organization,
        User,
        Role,
        Feature,
        SubscriptionPlan,
        OrganizationSubscription,
        OrganizationFeature,
    ]
    for model in models_to_audit:
        pre_save.connect(store_pre_save_state, sender=model, weak=False)
        post_save.connect(log_action, sender=model, weak=False)
        pre_delete.connect(log_delete, sender=model, weak=False)