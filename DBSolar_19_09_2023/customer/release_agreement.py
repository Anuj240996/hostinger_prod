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


def get_or_create_doc_row(customer, user=None, result=None):
    from .models import ConsumerReleaseAgreement, Result

    if result is None:
        result = Result.objects.filter(consumer_id=customer).order_by('-id').first()

    doc = (
        ConsumerReleaseAgreement.objects.filter(customer=customer)
        .order_by('-created_at')
        .first()
    )
    if doc:
        return doc

    return ConsumerReleaseAgreement.objects.create(
        customer=customer,
        result=result,
        created_by=user if getattr(user, 'is_authenticated', False) else None,
    )


def _build_release_pdf_bytes(customer, result):
    html = render_to_string(
        'customer/release_agreement_pdf.html',
        {
            'customer': customer,
            'result': result,
            'generated_at': timezone.now(),
            'flags': {field: bool(getattr(result, field, False)) for field in RELEASE_READY_FIELDS},
            'doc_kind': 'Release',
        },
    )
    result_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=result_buffer, encoding='utf-8')
    if pisa_status.err:
        raise RuntimeError(f'Release PDF failed with {pisa_status.err} errors')
    return result_buffer.getvalue()


def ensure_release_agreement_for_customer(customer, user=None, force=False):
    """
    If customer_result flags are all True, ensure a Release PDF exists
    (Agreement remains manual upload unless already present).
    """
    from .models import Result

    if not customer:
        return None

    result = Result.objects.filter(consumer_id=customer).order_by('-id').first()
    if not result_is_release_ready(result):
        return get_or_create_doc_row(customer, user=user, result=result)

    doc = get_or_create_doc_row(customer, user=user, result=result)
    if doc.has_release_pdf and not force:
        return doc

    pdf_bytes = _build_release_pdf_bytes(customer, result)
    filename = f'release_{customer.Cust_id}.pdf'
    doc.result = result
    if user and getattr(user, 'is_authenticated', False):
        doc.created_by = user
    doc.release_pdf.save(filename, ContentFile(pdf_bytes), save=False)
    # Keep legacy field in sync for older download URLs
    doc.pdf.save(filename, ContentFile(pdf_bytes), save=False)
    doc.release_pdf_data = bytes(pdf_bytes)
    doc.save()
    return doc


def save_uploaded_doc(customer, doc_type, uploaded_file, user=None):
    """Save a manually uploaded release or agreement PDF."""
    doc_type = (doc_type or '').strip().lower()
    if doc_type not in ('release', 'agreement'):
        raise ValueError('doc_type must be release or agreement')
    if not uploaded_file:
        raise ValueError('No file uploaded')

    name = (getattr(uploaded_file, 'name', '') or '').lower()
    content_type = (getattr(uploaded_file, 'content_type', '') or '').lower()
    if not (name.endswith('.pdf') or 'pdf' in content_type):
        raise ValueError('Only PDF files are allowed')

    data = uploaded_file.read()
    if not data:
        raise ValueError('Uploaded file is empty')
    data = bytes(data)

    doc = get_or_create_doc_row(customer, user=user)
    safe_name = f'{doc_type}_{customer.Cust_id}.pdf'
    if doc_type == 'release':
        doc.release_pdf.save(safe_name, ContentFile(data, name=safe_name), save=False)
        doc.pdf.save(safe_name, ContentFile(data, name=safe_name), save=False)
        doc.release_pdf_data = data
    else:
        doc.agreement_pdf.save(safe_name, ContentFile(data, name=safe_name), save=False)
        doc.agreement_pdf_data = data
    if user and getattr(user, 'is_authenticated', False):
        doc.created_by = user
    doc.save()
    return doc


def delete_uploaded_doc(customer, doc_type):
    """Remove Release or Agreement PDF (disk + binary) for a consumer."""
    from .models import ConsumerReleaseAgreement

    doc_type = (doc_type or '').strip().lower()
    if doc_type not in ('release', 'agreement'):
        raise ValueError('doc_type must be release or agreement')

    doc = (
        ConsumerReleaseAgreement.objects.filter(customer=customer)
        .order_by('-created_at')
        .first()
    )
    if not doc:
        raise ValueError('No Release & Agreement record found for this consumer.')

    def _clear_file(field):
        if not field:
            return
        try:
            if field.name:
                field.delete(save=False)
        except Exception:
            pass
        try:
            field.name = ''
        except Exception:
            pass

    if doc_type == 'release':
        _clear_file(doc.release_pdf)
        _clear_file(doc.pdf)
        doc.release_pdf = None
        doc.pdf = None
        doc.release_pdf_data = None
    else:
        _clear_file(doc.agreement_pdf)
        doc.agreement_pdf = None
        doc.agreement_pdf_data = None

    doc.save()
    return doc


def backfill_release_agreements(limit=None, user=None):
    """Create missing Release PDFs for every Result row that is release-ready."""
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
