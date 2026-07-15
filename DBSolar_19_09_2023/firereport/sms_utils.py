"""Service Report OTP delivery: WhatsApp + Email (not SMS)."""
from __future__ import annotations

import logging
import re
from typing import Optional, Tuple
from urllib.parse import quote_plus

import requests
from django.conf import settings
from django.core.mail import send_mail

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


def mask_email(email: str) -> str:
    email = (email or "").strip()
    if "@" not in email:
        return email or "****"
    name, domain = email.split("@", 1)
    if len(name) <= 2:
        masked = name[0] + "*" if name else "*"
    else:
        masked = name[0] + ("*" * min(6, len(name) - 2)) + name[-1]
    return f"{masked}@{domain}"


def build_service_report_otp_message(*, name: str, service_id: int, otp: str) -> str:
    consumer = (name or "Customer").strip() or "Customer"
    return (
        f"Dear {consumer}, DB Solar Service Report OTP for SRV/{service_id} is {otp}. "
        f"Share this OTP with the DB Solar engineer only after you are satisfied with the service work. "
        f"Valid for 10 minutes. - DB Solar"
    )


def build_service_report_otp_email_subject(*, service_id: int) -> str:
    return f"DB Solar Service Report OTP - SRV/{service_id}"


def send_whatsapp(phone: str, message: str) -> Tuple[bool, str]:
    """Auto-send WhatsApp message to consumer mobile number."""
    mobile = normalize_indian_mobile(phone)
    if not mobile:
        return False, "Invalid consumer mobile number for WhatsApp"

    provider = (getattr(settings, "WHATSAPP_PROVIDER", None) or "console").strip().lower()
    country = str(getattr(settings, "SMS_COUNTRY_CODE", "91") or "91").strip()
    full_mobile = f"{country}{mobile}"
    # Ultramsg/Meta often want +91...
    e164 = f"+{full_mobile}"

    if provider == "console":
        logger.warning("WHATSAPP_PROVIDER=console phone=%s msg=%s", mask_mobile(mobile), message)
        return True, (
            "OTP generated (WhatsApp console mode — set WHATSAPP API keys in EasyPanel to send real WhatsApp)"
        )

    if provider == "ultramsg":
        instance = (getattr(settings, "ULTRAMSG_INSTANCE_ID", None) or "").strip()
        token = (getattr(settings, "ULTRAMSG_TOKEN", None) or "").strip()
        if not instance or not token:
            return False, "ULTRAMSG_INSTANCE_ID / ULTRAMSG_TOKEN not configured"
        url = f"https://api.ultramsg.com/{instance}/messages/chat"
        try:
            resp = requests.post(
                url,
                data={"token": token, "to": e164, "body": message, "priority": "10"},
                timeout=25,
            )
            body = (resp.text or "").strip()
            if resp.status_code >= 400:
                return False, f"UltraMsg error: {body[:200]}"
            # UltraMsg returns JSON with "sent":"true" on success
            low = body.lower()
            if '"error"' in low and '"sent":"true"' not in low and '"sent": true' not in low:
                return False, f"UltraMsg rejected: {body[:200]}"
            return True, "OTP WhatsApp sent"
        except Exception as exc:
            logger.exception("UltraMsg WhatsApp send failed")
            return False, f"WhatsApp send failed: {exc}"

    if provider in ("meta", "whatsapp_cloud", "cloud"):
        token = (getattr(settings, "WHATSAPP_META_TOKEN", None) or "").strip()
        phone_id = (getattr(settings, "WHATSAPP_META_PHONE_NUMBER_ID", None) or "").strip()
        api_version = (getattr(settings, "WHATSAPP_META_API_VERSION", None) or "v19.0").strip()
        if not token or not phone_id:
            return False, "WHATSAPP_META_TOKEN / WHATSAPP_META_PHONE_NUMBER_ID not configured"
        url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"
        # Prefer simple text for setup; Meta OTP templates can be configured later via WHATSAPP_META_TEMPLATE
        template = (getattr(settings, "WHATSAPP_META_TEMPLATE", None) or "").strip()
        try:
            if template:
                lang = (getattr(settings, "WHATSAPP_META_TEMPLATE_LANG", None) or "en").strip()
                # Extract 6-digit OTP from message for template body param
                m = re.search(r"\b(\d{6})\b", message or "")
                otp_code = m.group(1) if m else message
                payload = {
                    "messaging_product": "whatsapp",
                    "to": full_mobile,
                    "type": "template",
                    "template": {
                        "name": template,
                        "language": {"code": lang},
                        "components": [
                            {
                                "type": "body",
                                "parameters": [{"type": "text", "text": str(otp_code)}],
                            }
                        ],
                    },
                }
            else:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": full_mobile,
                    "type": "text",
                    "text": {"preview_url": False, "body": message},
                }
            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=25,
            )
            body = (resp.text or "").strip()
            if resp.status_code >= 400:
                return False, f"Meta WhatsApp error: {body[:200]}"
            return True, "OTP WhatsApp sent"
        except Exception as exc:
            logger.exception("Meta WhatsApp send failed")
            return False, f"WhatsApp send failed: {exc}"

    if provider == "http":
        url_tmpl = (getattr(settings, "WHATSAPP_HTTP_URL", None) or "").strip()
        if not url_tmpl:
            return False, "WHATSAPP_HTTP_URL is not configured"
        url = (
            url_tmpl
            .replace("{phone}", quote_plus(full_mobile))
            .replace("{e164}", quote_plus(e164))
            .replace("{mobile}", quote_plus(mobile))
            .replace("{message}", quote_plus(message))
        )
        try:
            method = (getattr(settings, "WHATSAPP_HTTP_METHOD", "GET") or "GET").upper()
            if method == "POST":
                resp = requests.post(
                    url,
                    data={"phone": full_mobile, "to": e164, "message": message},
                    timeout=25,
                )
            else:
                resp = requests.get(url, timeout=25)
            if resp.status_code >= 400:
                return False, f"WhatsApp gateway HTTP {resp.status_code}: {(resp.text or '')[:200]}"
            return True, "OTP WhatsApp sent"
        except Exception as exc:
            logger.exception("HTTP WhatsApp send failed")
            return False, f"WhatsApp send failed: {exc}"

    return False, f"Unknown WHATSAPP_PROVIDER={provider}"


def send_otp_email(email: str, *, subject: str, message: str) -> Tuple[bool, str]:
    """Send OTP email to consumer."""
    to_email = (email or "").strip()
    if not to_email or "@" not in to_email:
        return False, "Consumer email is missing or invalid"

    from_email = (
        getattr(settings, "DEFAULT_FROM_EMAIL", None)
        or getattr(settings, "EMAIL_HOST_USER", None)
        or "noreply@db-solar.co.in"
    )
    try:
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        if not sent:
            return False, "Email gateway returned 0 (not sent)"
        return True, f"OTP email sent to {mask_email(to_email)}"
    except Exception as exc:
        logger.exception("OTP email send failed")
        return False, f"Email send failed: {exc}"


def deliver_service_report_otp(
    *,
    phone: str,
    email: Optional[str],
    name: str,
    service_id: int,
    otp: str,
) -> dict:
    """
    Auto-send OTP on WhatsApp number + email.
    Returns channel results; overall ok if WhatsApp OR email succeeds
    (WhatsApp required when phone exists; email is best-effort add-on if address present).
    """
    message = build_service_report_otp_message(name=name, service_id=service_id, otp=otp)
    subject = build_service_report_otp_email_subject(service_id=service_id)

    wa_ok, wa_detail = send_whatsapp(phone, message)
    email_ok, email_detail = (False, "No consumer email")
    if email:
        email_ok, email_detail = send_otp_email(email, subject=subject, message=message)

    # Prefer WhatsApp success; email alone is also acceptable if WA fails but mail works.
    overall_ok = bool(wa_ok or email_ok)
    parts = []
    parts.append(f"WhatsApp: {wa_detail}")
    parts.append(f"Email: {email_detail}")
    detail = " | ".join(parts)

    return {
        "ok": overall_ok,
        "detail": detail,
        "message_text": message,
        "whatsapp_ok": wa_ok,
        "whatsapp_detail": wa_detail,
        "email_ok": email_ok,
        "email_detail": email_detail,
        "masked_phone": mask_mobile(phone),
        "masked_email": mask_email(email) if email else "",
    }


# Keep old name as unused alias for any leftover imports (no SMS path for this feature).
def send_sms(phone: str, message: str) -> Tuple[bool, str]:
    return send_whatsapp(phone, message)
