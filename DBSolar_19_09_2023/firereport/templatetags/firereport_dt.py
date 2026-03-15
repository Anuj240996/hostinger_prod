from __future__ import annotations

from datetime import datetime
import re

from django import template
from django.utils import timezone

register = template.Library()
_MSG_RE = re.compile(
    r"^\[Category:\s*(?P<cat>.*?)\]\s*\[Title:\s*(?P<title>.*?)\]\s*(?:\r?\n)?(?P<body>[\s\S]*)$"
)


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        txt = value.strip()
        # Normalize to an ISO-like format with 6-digit microseconds and tz.
        m = re.match(
            r"^(?P<dt>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})(?P<frac>\.\d+)?(?P<tz>Z|[+-]\d{2}(:?\d{2})?)?$",
            txt,
        )
        if m:
            base = m.group("dt")
            frac = m.group("frac") or ""
            tz = m.group("tz") or ""
            if frac:
                frac_digits = frac[1:]
                if len(frac_digits) < 6:
                    frac_digits = frac_digits.ljust(6, "0")
                elif len(frac_digits) > 6:
                    frac_digits = frac_digits[:6]
                frac = "." + frac_digits
            if tz in ("Z", "z"):
                tz = "+00:00"
            if tz and re.match(r"[+-]\d{2}$", tz):
                tz = tz + ":00"
            elif tz and re.match(r"[+-]\d{4}$", tz):
                tz = tz[:-2] + ":" + tz[-2:]
            txt = f"{base}{frac}{tz}"

        try:
            parsed = datetime.fromisoformat(txt)
            if timezone.is_naive(parsed):
                return timezone.make_aware(parsed, timezone.get_default_timezone())
            return parsed
        except Exception:
            pass

        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(txt, fmt)
                return timezone.make_aware(parsed, timezone.get_default_timezone())
            except Exception:
                continue
    return None


@register.filter(name="indian_dt")
def indian_dt(value):
    dt = _parse_dt(value)
    if not dt:
        return "-"
    try:
        dt = timezone.localtime(dt)
    except Exception:
        pass
    return dt.strftime("%d-%m-%Y %H:%M")


@register.filter(name="complaint_category")
def complaint_category(message):
    if not message:
        return "-"
    m = _MSG_RE.match(str(message).strip())
    if not m:
        return "-"
    return (m.group("cat") or "").strip() or "-"


@register.filter(name="complaint_title")
def complaint_title(message):
    if not message:
        return "-"
    m = _MSG_RE.match(str(message).strip())
    if not m:
        return "-"
    return (m.group("title") or "").strip() or "-"


@register.filter(name="complaint_body")
def complaint_body(message):
    if not message:
        return "-"
    m = _MSG_RE.match(str(message).strip())
    if not m:
        return str(message)
    body = (m.group("body") or "").strip()
    return body or "-"
