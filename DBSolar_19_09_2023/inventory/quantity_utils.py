"""Quantity rules: decimals allowed only for Kg, Mtr, Lit/Ltr units."""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

DECIMAL_UNITS = frozenset({'kg', 'mtr', 'lit', 'ltr'})


def normalize_unit(unit):
    return (unit or '').strip().lower().replace('.', '')


def allows_decimal_quantity(unit):
    return normalize_unit(unit) in DECIMAL_UNITS


def quantize_quantity(value, unit=None):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal('0')

    if unit and allows_decimal_quantity(unit):
        return amount.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    return amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)


def format_quantity_display(value, unit=None):
    """Format quantity for display; mirrors static/js/stock_quantity_utils.js."""
    qty = quantize_quantity(value, unit)
    if qty == 0:
        return '0'
    if unit and not allows_decimal_quantity(unit):
        return str(int(qty))
    text = format(qty, 'f')
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    return text or '0'


def quantity_to_str(value, unit=None):
    """Plain decimal string for HTML data attributes and hidden inputs."""
    return format(quantize_quantity(value, unit), 'f')


def edit_sale_remaining(warehouse_qty, saved_line_qty, entered_qty, unit=None):
    """Remaining stock after the current line quantity on edit sale."""
    warehouse = quantize_quantity(warehouse_qty, unit)
    saved = quantize_quantity(saved_line_qty, unit)
    entered = quantize_quantity(entered_qty, unit)
    remaining = warehouse + saved - entered
    if remaining < 0:
        remaining = Decimal('0')
    return quantize_quantity(remaining, unit)
