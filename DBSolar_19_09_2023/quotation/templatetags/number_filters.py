from django import template
import re

register = template.Library()
#
# @register.filter
# def clean_decimal(value):
#     """
#     Show integer without decimals.
#     Show decimal only when needed.
#     """
#     try:
#         value = float(value)
#     except:
#         return value
#
#     if value.is_integer():
#         return str(int(value))  # remove .0
#     return str(value)          # keep decimal


#
# @register.filter
# def clean_decimal(value):
#     """
#     Clean decimal from string like '3.30 KW' -> '3.3 KW'
#     """
#     if not value:
#         return value
#
#     value_str = str(value).strip().upper()
#
#     # Remove unit if present
#     if value_str.endswith("KW"):
#         number_part = value_str[:-2].strip()   # Removes KW
#         unit = " KW"
#     else:
#         number_part = value_str
#         unit = ""
#
#     # Remove trailing zeros
#     if "." in number_part:
#         number_part = number_part.rstrip("0").rstrip(".")
#
#     return number_part + unit

@register.filter
def clean_decimal(value):
    """
    Cleans decimal from strings like '3.30 KW' and returns only number:
    '3.30 KW' -> '3.3'
    '3.00'     -> '3'
    """
    if not value:
        return value

    value_str = str(value).strip().upper()

    # Remove 'KW' if present
    if value_str.endswith("KW"):
        number_part = value_str[:-2].strip()
    else:
        number_part = value_str

    # Remove trailing zeros
    if "." in number_part:
        number_part = number_part.rstrip("0").rstrip(".")

    return number_part


@register.filter
def indian_format_no_decimals(value):
    """
    Format number in Indian grouping and remove decimals.
    Examples:
      121100.00 -> 1,21,100
      12345678  -> 1,23,45,678
    """
    try:
        number = float(value)
    except (ValueError, TypeError):
        return value

    sign = "-" if number < 0 else ""
    integer_part = str(int(abs(number)))

    if len(integer_part) <= 3:
        return sign + integer_part

    last_three = integer_part[-3:]
    rest = integer_part[:-3]
    rest = re.sub(r"(\d)(?=(\d{2})+(?!\d))", r"\1,", rest)
    return sign + rest + "," + last_three
