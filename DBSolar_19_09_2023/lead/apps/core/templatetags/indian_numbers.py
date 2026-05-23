# from django import template
#
# register = template.Library()
#
# @register.filter
# def indian_currency(value):
#     """
#     Convert a number to Indian currency format (lakhs/crores).
#     Example: 2500000 -> ₹25,00,000.00
#     """
#     try:
#         value = float(value)
#         # Format with two decimal places
#         value_str = f"{value:.2f}"
#         parts = value_str.split('.')
#         integer_part = parts[0]
#         decimal_part = parts[1]
#
#         # Reverse the integer part for grouping
#         rev_int = integer_part[::-1]
#         groups = []
#         # First group of 3 digits (for thousands)
#         groups.append(rev_int[:3])
#         # Subsequent groups of 2 digits
#         i = 3
#         while i < len(rev_int):
#             groups.append(rev_int[i:i+2])
#             i += 2
#         # Join reversed groups and reverse back
#         formatted_int = ','.join(groups)[::-1]
#         return f"₹{formatted_int}.{decimal_part}"
#     except (ValueError, TypeError):
#         return "₹0.00"


from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template

register = template.Library()

# Unicode Indian Rupee (U+20B9) — not Font Awesome fa-rupee-sign (renders as "Rs")
INR_SYMBOL = '\u20b9'


def _group_indian_integer_digits(integer_digits):
    """Group integer digits in Indian style (e.g. 315810 -> 3,15,810)."""
    rev_int = integer_digits[::-1]
    groups = [rev_int[:3]]
    i = 3
    while i < len(rev_int):
        groups.append(rev_int[i:i + 2])
        i += 2
    return ','.join(groups)[::-1]


def _is_whole_amount(dec):
    """True when amount has no paise (e.g. 315810, 315810.00, 300000.00)."""
    dec = dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return dec == dec.to_integral_value()


def _format_indian_number(value, include_symbol=True):
    """
    Indian grouping with optional rupee symbol.
    Whole amounts omit decimals (3,15,810); fractional amounts show them (3,15,810.50).
    """
    try:
        dec = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        formatted = '0'
    else:
        sign = '-' if dec < 0 else ''
        dec = abs(dec).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if _is_whole_amount(dec):
            integer_digits = str(dec.to_integral_value())
            formatted = _group_indian_integer_digits(integer_digits)
        else:
            integer_digits = str(int(dec))
            formatted_int = _group_indian_integer_digits(integer_digits)
            frac_str = format(dec, 'f').split('.', 1)[1]
            frac_str = frac_str.rstrip('0') or '0'
            formatted = f"{formatted_int}.{frac_str}"

        if sign:
            formatted = f"{sign}{formatted}"

        # Whole amounts must never show ".00" (e.g. 3,15,810.00 -> 3,15,810)
        if '.' in formatted:
            whole, frac = formatted.rsplit('.', 1)
            if frac == '00' or frac == '0':
                formatted = whole

    if include_symbol:
        return f"{INR_SYMBOL}{formatted}"
    return formatted


def format_indian_amount_display(value):
    """Format amount for UI (Indian grouping, no symbol, no .00 on whole values)."""
    if value is None:
        return None
    return _format_indian_number(value, include_symbol=False)


def format_indian_card_price_display(value):
    """Lead card quotation price, e.g. ₹3,15,810/-"""
    base = format_indian_amount_display(value)
    if base is None:
        return None
    return f"{INR_SYMBOL}{base}/-"


def format_indian_monthly_charge_display(value):
    """Monthly electricity bill on lead cards, e.g. ₹2,500/monthly"""
    base = format_indian_amount_display(value)
    if base is None:
        return None
    return f"{INR_SYMBOL}{base}/monthly"


@register.filter
def indian_currency(value):
    return _format_indian_number(value, include_symbol=True)


@register.filter
def indian_number(value):
    """Indian grouping without the rupee symbol (use with a separate ₹ prefix)."""
    return _format_indian_number(value, include_symbol=False)


@register.filter
def indian_card_price(value):
    """Card/list price with /- suffix, e.g. 20,032/-"""
    result = format_indian_card_price_display(value)
    return result if result is not None else ''


@register.filter
def indian_monthly_charge(value):
    """Monthly bill with ₹ and /monthly suffix, e.g. ₹2,500/monthly"""
    result = format_indian_monthly_charge_display(value)
    return result if result is not None else ''