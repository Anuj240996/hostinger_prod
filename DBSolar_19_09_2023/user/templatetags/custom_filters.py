from django import template
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

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
            # OneToOne is on Profile.customer; reverse related name is profile
            try:
                from user.models import Profile
                return Profile.objects.filter(customer=profile_or_user).first()
            except Exception:
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


def _normalize_profile_pics_path(image_name):
    """Force relative storage path into media/profile_pics/..."""
    if not image_name:
        return 'profile_pics/default.png'
    name = str(image_name).replace('\\', '/').lstrip('/')
    if name.startswith('media/'):
        name = name[len('media/'):]
    if name.startswith('profile_pics/'):
        return name
    if name.startswith('profile_images/'):
        return 'profile_pics/' + name.split('/', 1)[1]
    # bare filename stored in DB
    return f'profile_pics/{name}'


def _media_profile_image_url(image):
    """Build /media/profile_pics/... URL (files live under MEDIA_ROOT/profile_pics)."""
    media_url = settings.MEDIA_URL if settings.MEDIA_URL.endswith('/') else f'{settings.MEDIA_URL}/'
    if not image or not getattr(image, 'name', None):
        return f'{media_url}profile_pics/default.png'
    return f'{media_url}{_normalize_profile_pics_path(image.name)}'


@register.filter(name='profile_image_url')
def profile_image_url(profile_or_user):
    """Avatar URL for a User or Profile from media/profile_pics."""
    media_url = settings.MEDIA_URL if settings.MEDIA_URL.endswith('/') else f'{settings.MEDIA_URL}/'
    default_url = f'{media_url}profile_pics/default.png'
    profile = _profile_for_user_or_profile(profile_or_user)
    if profile is None:
        return default_url
    try:
        return _media_profile_image_url(getattr(profile, 'image', None))
    except Exception:
        return default_url
