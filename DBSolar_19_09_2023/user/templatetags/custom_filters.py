from django import template
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key, '')


def _profile_for_user_or_profile(profile_or_user):
    if profile_or_user is None:
        return None

    User = get_user_model()
    if isinstance(profile_or_user, User):
        try:
            return profile_or_user.profile
        except ObjectDoesNotExist:
            return None
    return profile_or_user


@register.filter(name='user_profile')
def user_profile(user):
    """Return Profile for a User, or None when missing."""
    return _profile_for_user_or_profile(user)


@register.filter(name='user_profile_label')
def user_profile_label(user):
    profile = _profile_for_user_or_profile(user)
    if not profile:
        return 'Consumer'
    designation = (getattr(profile, 'designation', None) or '').strip()
    department = (getattr(profile, 'department', None) or '').strip()
    if designation and department:
        return f'{designation}-{department}'
    return designation or department or 'Staff'


@register.filter(name='profile_image_url')
def profile_image_url(profile_or_user):
    """Avatar URL for a User or Profile, with static fallback."""
    profile = _profile_for_user_or_profile(profile_or_user)
    if profile is None:
        return static('images/dblogosmall.png')
    try:
        image = profile.image
        if image and image.name:
            storage = image.storage
            if storage.exists(image.name):
                return image.url
    except Exception:
        pass
    return static('images/dblogosmall.png')
