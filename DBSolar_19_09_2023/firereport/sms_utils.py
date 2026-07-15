"""SMS helpers for Service Report OTP."""
from __future__ import annotations

import logging
import re
from typing import Optional, Tuple
from urllib.parse import quote_plus

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_indian_mobile(raw) -> Optional[str]:
    if raw is None:
        return None
    digits = re.sub(r"\D+", "", str(raw))
    if digits.startswith("91") and len(digits) >= 12:
        digits = digits[-10:]
    if len(digits) == 10 and digits[0] in "6789":
        return digits
    return None


def mask_mobile(phone: str) -> str:
    phone = normalize_indian_mobile(phone) or str(phone or "")
    if len(phone) < 4:
        return "****"
    return f"{phone[:2]}XXXXXX{phone[-2:]}"


def build_service_report_otp_message(*, name: str, service_id: int, otp: str) -> str:
    consumer = (name or "Customer").strip() or "Customer"
    return (
        f"Dear {consumer}, DB Solar Service Report OTP for SRV/{service_id} is {otp}. "
        f"Share this OTP with the DB Solar engineer only after you are satisfied with the service work. "
        f"Valid for 10 minutes. - DB Solar"
    )


def send_sms(phone: str, message: str) -> Tuple[bool, str]:
    mobile = normalize_indian_mobile(phone)
    if not mobile:
        return False, "Invalid consumer mobile number"

    provider = (getattr(settings, "SMS_PROVIDER", None) or "console").strip().lower()
    country = str(getattr(settings, "SMS_COUNTRY_CODE", "91") or "91").strip()
    full_mobile = f"{country}{mobile}"

    if provider == "console":
        logger.warning("SMS_PROVIDER=console phone=%s msg=%s", mask_mobile(mobile), message)
        return True, (
            "OTP generated (SMS console mode — configure MSG91_AUTH_KEY to send real SMS)"
        )

    if provider == "msg91":
        auth_key = (getattr(settings, "MSG91_AUTH_KEY", None) or "").strip()
        sender = (getattr(settings, "MSG91_SENDER", None) or "DBSOLR").strip()
        route = str(getattr(settings, "MSG91_ROUTE", "4") or "4").strip()
        if not auth_key:
            return False, "MSG91_AUTH_KEY is not configured on the server"
        try:
            resp = requests.get(
                "https://api.msg91.com/api/sendhttp.php",
                params={
                    "authkey": auth_key,
                    "mobiles": full_mobile,
                    "message": message,
                    "sender": sender,
                    "route": route,
                    "country": country,
                },
                timeout=20,
            )
            body = (resp.text or "").strip()
            if resp.status_code >= 400:
                return False, f"MSG91 error: {body[:200]}"
            if body.lower().startswith("error") or '"type":"error"' in body.lower():
                return False, f"MSG91 rejected SMS: {body[:200]}"
            return True, "OTP SMS sent"
        except Exception as exc:
            logger.exception("MSG91 send failed")
            return False, f"SMS send failed: {exc}"

    if provider == "http":
        url_tmpl = (getattr(settings, "SMS_HTTP_URL", None) or "").strip()
        if not url_tmpl:
            return False, "SMS_HTTP_URL is not configured"
        url = (
            url_tmpl
            .replace("{phone}", quote_plus(full_mobile))
            .replace("{mobile}", quote_plus(mobile))
            .replace("{message}", quote_plus(message))
        )
        try:
            method = (getattr(settings, "SMS_HTTP_METHOD", "GET") or "GET").upper()
            resp = requests.post(url, timeout=20) if method == "POST" else requests.get(url, timeout=20)
            if resp.status_code >= 400:
                return False, f"SMS gateway HTTP {resp.status_code}: {(resp.text or '')[:200]}"
            return True, "OTP SMS sent"
        except Exception as exc:
            logger.exception("HTTP SMS send failed")
            return False, f"SMS send failed: {exc}"

    return False, f"Unknown SMS_PROVIDER={provider}"
