"""Shared helpers for quotation master settings."""

from django.db import connection

from .models import QuotationBankDetail, QuotationMaster, TermsAndCondition

_TRUTHY = ('1', 't', 'true', 'y', 'yes', 'on')


def _is_truthy(value):
    if value is None:
        return False
    return str(value).lower() in _TRUTHY


def _term_from_row(row):
    """Build TermsAndCondition instance from raw SQL row."""
    term = TermsAndCondition()
    term.id = row[0]
    term.content = row[1] if row[1] else ''
    term.has_yellow_background = _is_truthy(row[2])
    term.is_active = _is_truthy(row[3])
    term.show_in_quotation_form = _is_truthy(row[4]) if len(row) > 4 else True
    term.default_selected = _is_truthy(row[5]) if len(row) > 5 else False
    term.created_at = row[6] if len(row) > 6 else None
    from django.db.models.base import ModelState
    term._state = ModelState()
    term._state.adding = False
    term._state.db = 'default'
    return term


def get_active_terms_conditions():
    """Active terms marked to show on quotation create/edit forms."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    content,
                    CAST(has_yellow_background AS TEXT),
                    CAST(is_active AS TEXT),
                    CAST(show_in_quotation_form AS TEXT),
                    CAST(default_selected AS TEXT),
                    created_at
                FROM quotation_termsandcondition
            """)
            rows = cursor.fetchall()
        terms_list = []
        for row in rows:
            if _is_truthy(row[3]) and _is_truthy(row[4]):
                terms_list.append(_term_from_row(row))
        return terms_list
    except Exception:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error("Error fetching quotation form terms: %s", traceback.format_exc())
        try:
            return list(
                TermsAndCondition.objects.filter(is_active=True, show_in_quotation_form=True)
            )
        except Exception:
            return []


def get_default_selected_term_ids():
    """IDs of terms pre-selected on new quotation forms."""
    return [t.id for t in get_active_terms_conditions() if t.default_selected]


def get_form_visible_term_ids():
    return [t.id for t in get_active_terms_conditions()]


def get_quotation_master():
    return QuotationMaster.get_solo()


def get_default_bank_detail():
    bank = (
        QuotationBankDetail.objects.filter(is_active=True, is_default=True, show_in_quotation_form=True)
        .order_by('sort_order', 'id')
        .first()
    )
    if bank:
        return bank
    return (
        QuotationBankDetail.objects.filter(is_active=True, show_in_quotation_form=True)
        .order_by('sort_order', 'id')
        .first()
    )


def get_quotation_pdf_context_extras():
    master = get_quotation_master()
    return {
        'quotation_master': master,
        'bank_detail': get_default_bank_detail(),
    }
