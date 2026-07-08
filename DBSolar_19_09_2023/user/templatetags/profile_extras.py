from django import template
from django.conf import settings

from user.templatetags.custom_filters import _media_profile_image_url

register = template.Library()


@register.filter
def profile_image_url(profile):
    """Avatar URL from media/profile_pics, with default fallback."""
    media_url = settings.MEDIA_URL if settings.MEDIA_URL.endswith('/') else f'{settings.MEDIA_URL}/'
    default_url = f'{media_url}profile_pics/default.png'
    if profile is None:
        return default_url
    try:
        return _media_profile_image_url(getattr(profile, 'image', None))
    except Exception:
        return default_url
