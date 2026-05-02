# import re
# from django import template
#
# register = template.Library()
#
# @register.filter
# def indian_format(value):
#     """
#     Formats a number into the Indian numbering format.
#     Example:
#         1000     -> 1,000
#         20000    -> 20,000
#         210222   -> 2,10,222
#     """
#     try:
#         value = float(value)
#     except (ValueError, TypeError):
#         return value
#
#     # Split into integer and fractional parts.
#     integer_part = int(value)
#     fraction = round(value - integer_part, 2)
#     s = str(integer_part)
#
#     # For numbers larger than 3 digits, format the left part in pairs.
#     if len(s) > 3:
#         last_three = s[-3:]
#         rest = s[:-3]
#         # Insert commas every 2 digits in the 'rest'
#         rest = re.sub(r'(\d)(?=(\d{2})+(?!\d))', r'\1,', rest)
#         formatted = rest + ',' + last_three
#     else:
#         formatted = s
#
#     # Append fractional part if it exists and is non-zero.
#     if abs(fraction) >= 0.01:
#         # This will always produce two decimals, e.g. .50 or .75
#         frac_str = f"{fraction:.2f}"[1:]  # [1:] removes the leading 0
#         formatted += frac_str
#
#     return formatted


import re
from django import template

register = template.Library()


# @register.filter
# def indian_format(value):
#     """
#     Formats a number into the Indian numbering system with comma separation
#     and without any decimal part.
#
#     Examples:
#         21123    -> "21,123"
#         121100   -> "1,21,100"
#     """
#     try:
#         value = float(value)
#     except (ValueError, TypeError):
#         return value
#
#     # Handle negative numbers.
#     sign = '-' if value < 0 else ''
#     value = abs(value)
#
#     # Get the integer part.
#     integer_part = int(value)
#     s = str(integer_part)
#
#     if len(s) > 3:
#         last_three = s[-3:]
#         rest = s[:-3]
#         # Insert commas every two digits in the 'rest' portion.
#         rest = re.sub(r'(\d)(?=(\d{2})+(?!\d))', r'\1,', rest)
#         formatted = rest + ',' + last_three
#     else:
#         formatted = s
#
#     return sign + formatted

import re
from django import template

register = template.Library()

@register.filter
def indian_format(value):
    """
    Formats a number into the Indian numbering system with comma separation.
    Shows decimal part only if it is non-zero, otherwise hides decimal part.

    Examples:
        21123      -> "21,123"
        121100     -> "1,21,100"
        121100.00  -> "1,21,100"
        21123.45   -> "21,123.45"
        -1234567.89 -> "-12,34,567.89"
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value

    # Handle negative numbers.
    sign = '-' if value < 0 else ''
    value = abs(value)

    # Get integer and fractional parts.
    integer_part = int(value)
    fraction = value - integer_part

    s = str(integer_part)

    if len(s) > 3:
        last_three = s[-3:]
        rest = s[:-3]
        # Insert commas every two digits in the 'rest' portion.
        rest = re.sub(r'(\d)(?=(\d{2})+(?!\d))', r'\1,', rest)
        formatted_int = rest + ',' + last_three
    else:
        formatted_int = s

    # Only add decimal part if fraction is non-zero (with a small epsilon tolerance).
    if abs(fraction) > 0.0001:
        # Format fractional part with 2 decimal places, strip leading zero.
        formatted_frac = f"{fraction:.2f}"[1:]  # e.g., ".45"
    else:
        formatted_frac = ''

    return sign + formatted_int + formatted_frac


@register.filter
def indian_format_with_decimals(value):
    """
    Formats a number into the Indian numbering system with comma separation
    and always displays exactly two decimal places.

    Examples:
        121100     -> "1,21,100.00"
        21123.45   -> "21,123.45"
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value

    # Handle negative numbers.
    sign = '-' if value < 0 else ''
    value = abs(value)

    # Get the integer part and the fractional part.
    integer_part = int(value)
    fraction = value - integer_part
    s = str(integer_part)

    if len(s) > 3:
        last_three = s[-3:]
        rest = s[:-3]
        # Insert commas every two digits in the 'rest' portion.
        rest = re.sub(r'(\d)(?=(\d{2})+(?!\d))', r'\1,', rest)
        formatted_int = rest + ',' + last_three
    else:
        formatted_int = s

    # Always include two decimal places.
    # f"{fraction:.2f}" yields a string like "0.00" or "0.45".
    # [1:] removes the leading zero, resulting in ".00" or ".45".
    formatted_frac = f"{fraction:.2f}"[1:]

    return sign + formatted_int + formatted_frac


def _parse_bill_time(value):
    """Return datetime or date or None from DB-backed bill time (datetime, date, str)."""
    from datetime import date, datetime

    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        from django.utils.dateparse import parse_date, parse_datetime

        dt = parse_datetime(s.replace("Z", "+00:00") if "Z" in s else s)
        if dt is not None:
            return dt
        if len(s) >= 10:
            d = parse_date(s[:10])
            if d is not None:
                return d
        return None
    if hasattr(value, "strftime"):
        try:
            return value
        except Exception:
            return None
    return None


@register.filter
def as_bill_date(value):
    """
    Format bill time for DC/PDF (dd/mm/yyyy). Handles datetime, date, ISO strings, None.
    Replaces broken {{ bill.time.date|date:'d/m/Y' }} when time is a string from PostgreSQL.
    """
    from django.utils import dateformat

    parsed = _parse_bill_time(value)
    if parsed is None:
        return ""
    return dateformat.format(parsed, "d/m/Y")


@register.filter
def as_bill_date_iso(value):
    """HTML date input value (yyyy-mm-dd). Same inputs as as_bill_date."""
    from django.utils import dateformat

    parsed = _parse_bill_time(value)
    if parsed is None:
        return ""
    return dateformat.format(parsed, "Y-m-d")
