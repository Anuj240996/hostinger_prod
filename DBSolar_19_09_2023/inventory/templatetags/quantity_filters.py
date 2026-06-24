from django import template

from inventory.quantity_utils import format_quantity_display

register = template.Library()


@register.filter(name='format_qty')
def format_qty(value, unit=None):
    return format_quantity_display(value, unit)
