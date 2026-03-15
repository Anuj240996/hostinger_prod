import re


def parse_number(data):
    if data is not None:
        data = str(data)
        regex = r"\d+"
        match_list = re.findall(regex, data)
        if match_list:
            return ''.join(match_list)
    return ''


def remove_trailing_zero_from_float(num):
    if num % 1 == 0:
        return int(num)
    else:
        return num


def parse_phone_number(number):
    digits = parse_number(number)
    if not digits:
        return ""
    if len(digits) > 10:
        digits = digits[-10:]

    return digits


def clean_string(data):
    if not isinstance(data, str):
        data = str(data)
    if not data:
        return ""
    else:
        return data.strip()


def remove_spaces_and_special_chars(word, chars_to_ignore=None):
    if not chars_to_ignore:
        chars_to_ignore = []
    if word:
        regex_pattern_special_chars = "[^A-Za-z0-9\\s{}]".format("".join(chars_to_ignore))
        regex_pattern_spaces = "\\s+"
        new_word = re.sub(regex_pattern_special_chars, "", word)
        new_word = re.sub(regex_pattern_spaces, " ", new_word)
        return new_word.strip() if new_word else ""
    else:
        return ""


def get_clean_pincode(pincode_str):
    return parse_number(pincode_str)


def parse_indian_state(state_str, identifier=None):
    from core.models import StateChoices
    from sentry_sdk import capture_message

    state_str = remove_spaces_and_special_chars(state_str)
    state_str = state_str.replace("&", "and")
    state_str = "_".join(state_str.upper().strip().split(" "))

    if not state_str:
        return StateChoices.NULL

    if state_str in ["ANDAMAN_AND_NICOBAR_ISLANDS", str(StateChoices.AN)] or "ANDAMAN" in state_str or "NICOBAR" in state_str:
        return StateChoices.AN

    elif state_str in ["ANDHRA_PRADESH", str(StateChoices.AP)] or "ANDHRA" in state_str or "ANDRA" in state_str:
        return StateChoices.AP

    elif state_str in ["ARUNACHAL_PRADESH", str(StateChoices.AR)]:
        return StateChoices.AR

    elif state_str in ["ASSAM", str(StateChoices.AS)]:
        return StateChoices.AS

    elif state_str in ["BIHAR", str(StateChoices.BR)]:
        return StateChoices.BR

    elif state_str in ["CHANDIGARH", str(StateChoices.CG)]:
        return StateChoices.CG

    elif state_str in ["CHHATTISGARH", "CHATTISGARH", "CHHATISGARH",str(StateChoices.CH)]:
        return StateChoices.CH

    elif "HAVELI" in state_str or "DADRA" in state_str or state_str in [str(StateChoices.DN)]:
        return StateChoices.DN

    elif state_str in ["DAMAN_AND_DIU", "DAMAN_DIU", str(StateChoices.DD)]:
        return StateChoices.DD

    elif "DELHI" in state_str or state_str in [str(StateChoices.DL)]:
        return StateChoices.DL

    elif "GOA" in state_str or state_str in [str(StateChoices.GA)]:
        return StateChoices.GA

    elif state_str in ["GUJARAT", str(StateChoices.GJ)]:
        return StateChoices.GJ

    elif state_str in ["HARYANA", str(StateChoices.HR)]:
        return StateChoices.HR

    elif state_str in ["HIMACHAL_PRADESH", str(StateChoices.HP)]:
        return StateChoices.HP

    elif "JAMMU" in state_str or "KASHMIR" in state_str or state_str in [str(StateChoices.JK)]:
        return StateChoices.JK

    elif state_str in ["JHARKHAND", str(StateChoices.JH)]:
        return StateChoices.JH

    elif state_str in ["KARNATAKA", "KARANATAKA", str(StateChoices.KA)]:
        return StateChoices.KA

    elif state_str in ["KERALA", str(StateChoices.KL)]:
        return StateChoices.KL

    elif state_str in ["LADAKH", str(StateChoices.LA)]:
        return StateChoices.LA

    elif state_str in ["LAKSHADWEEP", str(StateChoices.LD)]:
        return StateChoices.LD

    elif state_str in ["MADHYA_PRADESH", str(StateChoices.MP)] or ("MADHYA" in state_str and "PRADESH" in state_str):
        return StateChoices.MP

    elif state_str in ["MAHARASHTRA", "MAHARASTRA", str(StateChoices.MH)]:
        return StateChoices.MH

    elif state_str in ["MANIPUR", str(StateChoices.MN)]:
        return StateChoices.MN

    elif state_str in ["MEGHALAYA", str(StateChoices.ML)]:
        return StateChoices.ML

    elif state_str in ["MIZORAM", str(StateChoices.MZ)]:
        return StateChoices.MZ

    elif state_str in ["NAGALAND", str(StateChoices.NL)]:
        return StateChoices.NL

    elif state_str in ["ODISHA", "ORISSA", str(StateChoices.OR)]:
        return StateChoices.OR

    elif state_str in ["PUDUCHERRY", "PONDICHERRY", str(StateChoices.PY)]:
        return StateChoices.PY

    elif state_str in ["PUNJAB", str(StateChoices.PB)]:
        return StateChoices.PB

    elif state_str in ["RAJASTHAN", str(StateChoices.RJ)]:
        return StateChoices.RJ

    elif state_str in ["SIKKIM", str(StateChoices.SK)]:
        return StateChoices.SK

    elif state_str in ["TAMIL_NADU", "TAMILNADU", str(StateChoices.TN)]:
        return StateChoices.TN

    elif state_str in ["TELANGANA", "TELENGANA", str(StateChoices.TS)]:
        return StateChoices.TS

    elif state_str in ["TRIPURA", str(StateChoices.TR)]:
        return StateChoices.TR

    elif state_str in ["UTTAR_PRADESH", str(StateChoices.UP)] or ("UTTAR" in state_str and "PRADESH" in state_str):
        return StateChoices.UP

    elif state_str in ["UTTARAKHAND", str(StateChoices.UK), "UT"]:
        return StateChoices.UK

    elif state_str in ["WEST_BENGAL", str(StateChoices.WB)]:
        return StateChoices.WB

    else:
        capture_message("Unable to parse:{} as state. Identifier: {}".format(state_str, identifier))
        return ""


def parse_number_to_ordinal(number):
    '''
    Taken From: https://stackoverflow.com/a/50992575
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    n = int(number)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix