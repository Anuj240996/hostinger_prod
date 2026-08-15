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
    """Terms shown on the quotation form are pre-checked on new quotations."""
    return [t.id for t in get_active_terms_conditions()]


def get_form_visible_term_ids():
    return [t.id for t in get_active_terms_conditions()]


def get_pdf_selected_terms(quotation=None):
    """PDF extra terms: checked on this quotation, and still active + on-form in master.

    Default-selected only pre-checks the create form. Unchecked terms must not appear.
    """
    allowed_ids = {t.id for t in get_active_terms_conditions()}
    selected = []
    if quotation is not None:
        try:
            selected = list(quotation.terms_conditions.all())
        except Exception:
            selected = []
    return [t for t in selected if t.id in allowed_ids]


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


PDF_TEMPLATE_STANDARD = 'quotation'
PDF_TEMPLATE_INDUSTRIAL = 'industrial'
PDF_TEMPLATE_STANDARD_INDUSTRIAL = 'standard_industrial'

# Flat list kept for validation / redirects.
PDF_TEMPLATE_OPTIONS = [
    {
        'key': PDF_TEMPLATE_STANDARD,
        'label': 'Standard Invoice',
        'sample_label': 'Sample 1',
        'group': 'standard',
        'hint': 'Existing standard quotation PDF',
        'template': 'quotation/quotation_template.html',
        'url_name': 'quotation:quotation_pdf',
        'pdf_path': '/quotation/{pk}/pdf/',
    },
    {
        'key': PDF_TEMPLATE_STANDARD_INDUSTRIAL,
        'label': 'Standard & Industrial Quotation',
        'sample_label': 'Sample 2',
        'group': 'standard',
        'hint': '6-page proposal (cover, about, invoice, terms, testimonials, thank you)',
        'template': 'quotation/standard_industrial_quotation.html',
        'url_name': 'quotation:standard_industrial_quotation_pdf',
        'pdf_path': '/quotation/{pk}/standard_industrial_pdf/',
    },
    {
        'key': PDF_TEMPLATE_INDUSTRIAL,
        'label': 'Industrial Quotation',
        'sample_label': 'Sample 1',
        'group': 'industrial',
        'hint': 'Existing industrial quotation PDF',
        'template': 'quotation/industrial_quotation.html',
        'url_name': 'quotation:industrial_quotation_pdf',
        'pdf_path': '/quotation/{pk}/industrial_pdf/',
    },
]

STANDARD_TEMPLATE_KEYS = {o['key'] for o in PDF_TEMPLATE_OPTIONS if o['group'] == 'standard'}
INDUSTRIAL_TEMPLATE_KEYS = {o['key'] for o in PDF_TEMPLATE_OPTIONS if o['group'] == 'industrial'}

# Two master cards: Standard (with samples) and Industrial (with samples).
PDF_TEMPLATE_GROUPS = [
    {
        'key': 'standard',
        'label': 'Standard Quotation',
        'radio_name': 'default_standard_pdf_template',
        'hint': 'Choose the default sample for the Standard Quotation PDF button.',
        'samples': [o for o in PDF_TEMPLATE_OPTIONS if o['group'] == 'standard'],
    },
    {
        'key': 'industrial',
        'label': 'Industrial Quotation',
        'radio_name': 'default_industrial_pdf_template',
        'hint': 'Choose the default sample for the Industrial Quotation PDF button.',
        'samples': [o for o in PDF_TEMPLATE_OPTIONS if o['group'] == 'industrial'],
    },
]


def get_default_standard_pdf_template():
    try:
        master = get_quotation_master()
        key = getattr(master, 'default_pdf_template', None) or PDF_TEMPLATE_STANDARD
    except Exception:
        return PDF_TEMPLATE_STANDARD
    if key not in STANDARD_TEMPLATE_KEYS:
        return PDF_TEMPLATE_STANDARD
    return key


def get_default_industrial_pdf_template():
    try:
        master = get_quotation_master()
        key = getattr(master, 'default_industrial_pdf_template', None) or PDF_TEMPLATE_INDUSTRIAL
    except Exception:
        return PDF_TEMPLATE_INDUSTRIAL
    if key not in INDUSTRIAL_TEMPLATE_KEYS:
        return PDF_TEMPLATE_INDUSTRIAL
    return key


def get_default_pdf_template():
    """Backward-compatible: returns Standard-card default sample. """
    return get_default_standard_pdf_template()


def get_pdf_template_option(template_key=None):
    key = template_key or get_default_standard_pdf_template()
    for item in PDF_TEMPLATE_OPTIONS:
        if item['key'] == key:
            return item
    return PDF_TEMPLATE_OPTIONS[0]


def pdf_url_name_for_template(template_key=None):
    return get_pdf_template_option(template_key)['url_name']


def pdf_path_for_template(pk, template_key=None):
    option = get_pdf_template_option(template_key)
    return option['pdf_path'].format(pk=pk)


def redirect_quotation_pdf(pk, template_key=None):
    from django.shortcuts import redirect
    return redirect(pdf_url_name_for_template(template_key), pk=pk)


def get_quotation_pdf_context_extras():
    master = get_quotation_master()
    standard_key = get_default_standard_pdf_template()
    try:
        industrial_key = get_default_industrial_pdf_template()
    except Exception:
        industrial_key = PDF_TEMPLATE_INDUSTRIAL
    return {
        'quotation_master': master,
        'bank_detail': get_default_bank_detail(),
        'default_pdf_template': standard_key,
        'default_standard_pdf_template': standard_key,
        'default_industrial_pdf_template': industrial_key,
        'pdf_template_options': PDF_TEMPLATE_OPTIONS,
        'pdf_template_groups': PDF_TEMPLATE_GROUPS,
        'default_pdf_option': get_pdf_template_option(standard_key),
        'default_standard_pdf_option': get_pdf_template_option(standard_key),
        'default_industrial_pdf_option': get_pdf_template_option(industrial_key),
        'standard_pdf_path_tpl': get_pdf_template_option(standard_key)['pdf_path'],
        'industrial_pdf_path_tpl': get_pdf_template_option(industrial_key)['pdf_path'],
    }
