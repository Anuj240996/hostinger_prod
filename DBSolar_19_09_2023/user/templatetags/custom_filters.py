from django import template
from django.templatetags.static import static

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key, '')


@register.filter(name='profile_image_url')
def profile_image_url(profile):
    """Avatar URL with static fallback when media file is missing."""
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
