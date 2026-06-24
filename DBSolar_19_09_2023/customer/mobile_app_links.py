import logging
from collections import defaultdict
from types import SimpleNamespace

from django.db import connection
from django.db.utils import DatabaseError
from django.utils import timezone

logger = logging.getLogger(__name__)

_LINK_FIELD_SEP = '|||'


def attach_mobile_app_links(customers):
    """Attach app_auth_links + user_app names to each customer (by new_customer_id)."""
    customers = list(customers)
    auth_user_ids = sorted({c.new_customer_id for c in customers if c.new_customer_id})
    try:
        links_by_auth_user = _fetch_links_from_db(auth_user_ids)
    except DatabaseError as exc:
        logger.warning("Mobile app link tables unavailable; skipping link lookup: %s", exc)
        links_by_auth_user = {}

    for customer in customers:
        lookup_id = int(customer.new_customer_id) if customer.new_customer_id is not None else None
        link_rows = links_by_auth_user.get(lookup_id, []) if lookup_id is not None else []
        _set_customer_mobile_link_fields(customer, link_rows)

    return customers


def _set_customer_mobile_link_fields(customer, link_rows):
    customer.mobile_app_links = link_rows

    names = [row.app_name for row in link_rows]
    emails = [row.app_email for row in link_rows]
    dates = [_format_link_datetime(row.created_at) for row in link_rows]
    link_ids = [str(row.id) for row in link_rows]

    customer.mobile_app_link_primary_name = names[0] if names else ''
    customer.mobile_app_link_names = _LINK_FIELD_SEP.join(names)
    customer.mobile_app_link_emails = _LINK_FIELD_SEP.join(emails)
    customer.mobile_app_link_dates = _LINK_FIELD_SEP.join(dates)
    customer.mobile_app_link_ids = _LINK_FIELD_SEP.join(link_ids)


def _fetch_links_from_db(auth_user_ids):
    if not auth_user_ids:
        return {}

    placeholders = ','.join(['%s'] * len(auth_user_ids))
    sql = f"""
        SELECT
            l.auth_user_id,
            l.id,
            l.app_user_id,
            COALESCE(NULLIF(TRIM(ua.name), ''), '') AS app_name,
            COALESCE(ua.email, '') AS app_email,
            l.created_at
        FROM app_auth_links l
        LEFT JOIN user_app ua ON ua.id = l.app_user_id
        WHERE l.auth_user_id IN ({placeholders})
        ORDER BY l.created_at DESC
    """

    links_by_auth_user = defaultdict(list)
    with connection.cursor() as cursor:
        cursor.execute(sql, auth_user_ids)
        for auth_user_id, link_id, app_user_id, app_name, app_email, created_at in cursor.fetchall():
            display_name = app_name.strip() if app_name else f'App user #{app_user_id}'
            links_by_auth_user[int(auth_user_id)].append(
                SimpleNamespace(
                    id=link_id,
                    app_user_id=app_user_id,
                    app_name=display_name,
                    app_email=app_email or '',
                    created_at=created_at,
                )
            )
    return links_by_auth_user


def delete_app_auth_link(link_id, auth_user_id):
    """Delete one mobile app link if it belongs to the given consumer auth_user."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM app_auth_links WHERE id = %s AND auth_user_id = %s',
                [int(link_id), int(auth_user_id)],
            )
            return cursor.rowcount > 0
    except DatabaseError as exc:
        logger.warning("Could not delete mobile app link: %s", exc)
        return False


def mobile_app_link_payload(customer):
    """Serialize link fields for JSON responses and table button updates."""
    return {
        'mobile_app_link_primary_name': getattr(customer, 'mobile_app_link_primary_name', ''),
        'mobile_app_link_names': getattr(customer, 'mobile_app_link_names', ''),
        'mobile_app_link_emails': getattr(customer, 'mobile_app_link_emails', ''),
        'mobile_app_link_dates': getattr(customer, 'mobile_app_link_dates', ''),
        'mobile_app_link_ids': getattr(customer, 'mobile_app_link_ids', ''),
        'remaining_count': len(getattr(customer, 'mobile_app_links', []) or []),
    }


def _format_link_datetime(value):
    if not value:
        return ''
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return timezone.localtime(value).strftime('%d %b %Y, %H:%M')
