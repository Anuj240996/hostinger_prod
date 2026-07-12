"""Release & Agreement PDF helpers driven by customer_result milestone flags."""
from io import BytesIO

from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa


RELEASE_READY_FIELDS = (
    'solar_panel',
    'inverter',
    'net_meter',
    'mseb',
    'inspection_report',
)


def result_is_release_ready(result):
    if not result:
        return False
    return all(bool(getattr(result, field, False)) for field in RELEASE_READY_FIELDS)


def _build_release_pdf_bytes(customer, result):
    html = render_to_string(
        'customer/release_agreement_pdf.html',
        {
            'customer': customer,
            'result': result,
            'generated_at': timezone.now(),
            'flags': {field: bool(getattr(result, field, False)) for field in RELEASE_READY_FIELDS},
        },
    )
    result_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=result_buffer, encoding='utf-8')
    if pisa_status.err:
        raise RuntimeError(f'Release agreement PDF failed with {pisa_status.err} errors')
    return result_buffer.getvalue()


def ensure_release_agreement_for_customer(customer, user=None, force=False):
    """
    If customer_result flags are all True for this consumer_id, create/store
    Release & Agreement PDF (once unless force=True).
    """
    from .models import ConsumerReleaseAgreement, Result

    if not customer:
        return None

    result = Result.objects.filter(consumer_id=customer).order_by('-id').first()
    if not result_is_release_ready(result):
        return None

    existing = (
        ConsumerReleaseAgreement.objects.filter(customer=customer)
        .exclude(pdf='')
        .exclude(pdf__isnull=True)
        .order_by('-created_at')
        .first()
    )
    if existing and not force:
        return existing

    pdf_bytes = _build_release_pdf_bytes(customer, result)
    filename = f'release_agreement_{customer.Cust_id}.pdf'

    if existing and force:
        doc = existing
    else:
        doc = ConsumerReleaseAgreement(
            customer=customer,
            result=result,
            created_by=user if getattr(user, 'is_authenticated', False) else None,
        )

    doc.result = result
    if user and getattr(user, 'is_authenticated', False):
        doc.created_by = user
    doc.pdf.save(filename, ContentFile(pdf_bytes), save=False)
    doc.save()
    return doc


def backfill_release_agreements(limit=None, user=None):
    """Create missing PDFs for every Result row that is release-ready."""
    from .models import Result

    qs = Result.objects.filter(
        solar_panel=True,
        inverter=True,
        net_meter=True,
        mseb=True,
        inspection_report=True,
        consumer_id__isnull=False,
    ).select_related('consumer_id')
    if limit:
        qs = qs[:limit]

    created = []
    for result in qs:
        doc = ensure_release_agreement_for_customer(result.consumer_id, user=user)
        if doc:
            created.append(doc)
    return created
