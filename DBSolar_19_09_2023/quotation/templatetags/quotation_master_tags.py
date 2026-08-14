from django import template

register = template.Library()


@register.simple_tag
def default_pdf_template():
    from quotation.master_helpers import get_default_pdf_template
    try:
        return get_default_pdf_template()
    except Exception:
        return 'quotation'


@register.simple_tag
def default_quotation_pdf_url(pk):
    from django.urls import reverse
    from quotation.master_helpers import pdf_url_name_for_template
    try:
        return reverse(pdf_url_name_for_template(), kwargs={'pk': pk})
    except Exception:
        return reverse('quotation:quotation_pdf', kwargs={'pk': pk})
