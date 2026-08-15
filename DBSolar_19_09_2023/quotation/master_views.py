"""Quotation master settings: company info, bank details, terms & conditions."""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import QuotationBankDetail, QuotationMaster, TermsAndCondition


def _is_control_panel_admin(user):
    return user.is_superuser or user.is_staff


def control_panel_session_required(view_func):
    """Require Control Panel password session (same as other control panel pages)."""
    @wraps(view_func)
    @login_required(login_url='user-login')
    @user_passes_test(_is_control_panel_admin)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get('control_panel_authenticated'):
            messages.warning(request, 'Please login to Control Panel first')
            return redirect(f"{reverse('user:control_panel_login')}?next={reverse('quotation:quotation_master')}")
        return view_func(request, *args, **kwargs)
    return _wrapped


DEFAULT_FROM_ADDRESS = (
    'Bhagya Banglow, Near Sant Eknath Rang Mandir,\n'
    'New Osman Pura, Chh. Sambhajinagar (MH) - 431001'
)

DEFAULT_SUBSIDY_NOTE = (
    'Exact subsidy depends on your electricity load approval. Maximum up to '
    '₹ 78,000 is available. Final eligible subsidy shall be decided by MNRE / '
    'DISCOM after approval.'
)


def _ensure_master_defaults(master):
    changed = False
    if not master.from_address:
        master.from_address = DEFAULT_FROM_ADDRESS
        changed = True
    if not master.subsidy_notes:
        master.subsidy_notes = DEFAULT_SUBSIDY_NOTE
        changed = True
    if not master.gst_no:
        master.gst_no = '123457896541332'
        changed = True
    if not master.pan_no:
        master.pan_no = 'ABC12358G'
        changed = True
    if changed:
        master.save(update_fields=['from_address', 'subsidy_notes', 'gst_no', 'pan_no'])
    if not QuotationBankDetail.objects.exists():
        QuotationBankDetail.objects.create(
            account_name='Heramb Industries',
            account_no='112233665544778',
            ifsc_code='SVSB000123',
            bank_name='SVC CO-OP Bank',
            branch_name='Aurangabad / Chh. SambhajiNagar',
            show_in_quotation_form=True,
            is_default=True,
            is_active=True,
        )


@control_panel_session_required
def quotation_master(request):
    try:
        master = QuotationMaster.get_solo()
    except (ProgrammingError, OperationalError):
        try:
            connection.rollback()
        except Exception:
            pass
        master = QuotationMaster.objects.defer(
            'default_pdf_template', 'default_industrial_pdf_template', 'proposal_cover_image'
        ).filter(pk=1).first()
        if master is None:
            master = QuotationMaster(pk=1, company_name='Heramb Industries')
        messages.warning(
            request,
            'Run database migrate for quotation so Standard & Industrial can be saved as the default template.',
        )
    _ensure_master_defaults(master)

    if request.method == 'POST':
        action = request.POST.get('action', 'save_company')

        if action == 'save_company':
            master.company_name = request.POST.get('company_name', master.company_name)
            master.gst_no = request.POST.get('gst_no', '')
            master.pan_no = request.POST.get('pan_no', '')
            master.address = request.POST.get('address', '')
            master.from_address = request.POST.get('from_address', '')
            master.subsidy_notes = request.POST.get('subsidy_notes', '')
            if request.FILES.get('company_logo'):
                master.company_logo = request.FILES['company_logo']
            if request.FILES.get('header_image'):
                master.header_image = request.FILES['header_image']
            if request.FILES.get('footer_image'):
                master.footer_image = request.FILES['footer_image']
            master.save()
            messages.success(request, 'Company details saved.')

        elif action == 'save_pdf_template':
            from .master_helpers import (
                INDUSTRIAL_TEMPLATE_KEYS,
                STANDARD_TEMPLATE_KEYS,
                get_pdf_template_option,
            )
            standard_selected = request.POST.get('default_standard_pdf_template', '')
            industrial_selected = request.POST.get('default_industrial_pdf_template', '')
            if standard_selected not in STANDARD_TEMPLATE_KEYS:
                messages.error(request, 'Please select a valid Standard Quotation sample.')
            elif industrial_selected not in INDUSTRIAL_TEMPLATE_KEYS:
                messages.error(request, 'Please select a valid Industrial Quotation sample.')
            else:
                try:
                    update_fields = ['default_pdf_template']
                    master.default_pdf_template = standard_selected
                    if hasattr(master, 'default_industrial_pdf_template'):
                        master.default_industrial_pdf_template = industrial_selected
                        update_fields.append('default_industrial_pdf_template')
                    master.save(update_fields=update_fields)
                    std = get_pdf_template_option(standard_selected)
                    ind = get_pdf_template_option(industrial_selected)
                    messages.success(
                        request,
                        'Defaults saved — Standard: {} — {}; Industrial: {} — {}.'.format(
                            std.get('sample_label', ''),
                            std.get('label', standard_selected),
                            ind.get('sample_label', ''),
                            ind.get('label', industrial_selected),
                        ),
                    )
                except (ProgrammingError, OperationalError):
                    try:
                        connection.rollback()
                    except Exception:
                        pass
                    messages.error(
                        request,
                        'Could not save the template. Run: python manage.py migrate quotation',
                    )

        elif action == 'save_term':
            term_id = request.POST.get('term_id')
            content = request.POST.get('content', '').strip()
            if not content:
                messages.error(request, 'Terms content is required.')
            else:
                if term_id:
                    term = get_object_or_404(TermsAndCondition, pk=term_id)
                else:
                    term = TermsAndCondition()
                term.content = content
                term.has_yellow_background = request.POST.get('has_yellow_background') == 'on'
                term.is_active = request.POST.get('is_active') == 'on'
                term.show_in_quotation_form = request.POST.get('show_in_quotation_form') == 'on'
                term.default_selected = request.POST.get('default_selected') == 'on'
                term.save()
                messages.success(request, 'Terms & condition saved.')

        elif action == 'delete_term':
            term_id = request.POST.get('term_id')
            if term_id:
                TermsAndCondition.objects.filter(pk=term_id).delete()
                messages.success(request, 'Terms & condition deleted.')

        elif action == 'save_bank':
            bank_id = request.POST.get('bank_id')
            if bank_id:
                bank = get_object_or_404(QuotationBankDetail, pk=bank_id)
            else:
                bank = QuotationBankDetail()
            bank.account_name = request.POST.get('account_name', '')
            bank.account_no = request.POST.get('account_no', '')
            bank.ifsc_code = request.POST.get('ifsc_code', '')
            bank.bank_name = request.POST.get('bank_name', '')
            bank.branch_name = request.POST.get('branch_name', '')
            # Single "Use on quotation PDF" checkbox controls show + default + active
            use_on_pdf = request.POST.get('use_on_pdf') == 'on'
            bank.show_in_quotation_form = use_on_pdf
            bank.is_default = use_on_pdf
            bank.is_active = use_on_pdf
            try:
                bank.sort_order = int(request.POST.get('sort_order') or 0)
            except ValueError:
                bank.sort_order = 0
            bank.save()
            if use_on_pdf:
                QuotationBankDetail.objects.exclude(pk=bank.pk).update(
                    is_default=False,
                    show_in_quotation_form=False,
                    is_active=False,
                )
            messages.success(request, 'Bank details saved.')

        elif action == 'delete_bank':
            bank_id = request.POST.get('bank_id')
            if bank_id:
                QuotationBankDetail.objects.filter(pk=bank_id).delete()
                messages.success(request, 'Bank record deleted.')
                # If only one bank remains, make it the PDF bank by default
                remaining = QuotationBankDetail.objects.all()
                if remaining.count() == 1:
                    only = remaining.first()
                    only.show_in_quotation_form = True
                    only.is_default = True
                    only.is_active = True
                    only.save(update_fields=['show_in_quotation_form', 'is_default', 'is_active'])

        return redirect('quotation:quotation_master')

    terms = TermsAndCondition.objects.all().order_by('id')
    banks = QuotationBankDetail.objects.filter(is_active=True).order_by('sort_order', 'id')
    all_banks = QuotationBankDetail.objects.all().order_by('sort_order', 'id')

    # Single bank card → always selected for PDF
    if all_banks.count() == 1:
        only = all_banks.first()
        if not (only.show_in_quotation_form and only.is_default and only.is_active):
            only.show_in_quotation_form = True
            only.is_default = True
            only.is_active = True
            only.save(update_fields=['show_in_quotation_form', 'is_default', 'is_active'])

    from .master_helpers import get_quotation_pdf_context_extras

    context = {
        'master': master,
        'terms': terms,
        'banks': banks,
        'all_banks': all_banks,
        'bank_count': all_banks.count(),
    }
    context.update(get_quotation_pdf_context_extras())
    return render(request, 'quotation/quotation_master.html', context)


@control_panel_session_required
def edit_quotation_template(request, template_key):
    """Edit a quotation PDF template. Standard & Industrial shows the 6-page cover layout."""
    from .master_helpers import PDF_TEMPLATE_OPTIONS, get_default_pdf_template

    valid = {item['key'] for item in PDF_TEMPLATE_OPTIONS}
    if template_key not in valid:
        messages.error(request, 'Unknown quotation template.')
        return redirect('quotation:quotation_master')

    try:
        master = QuotationMaster.get_solo()
    except (ProgrammingError, OperationalError):
        try:
            connection.rollback()
        except Exception:
            pass
        master = QuotationMaster.objects.defer(
            'default_pdf_template', 'default_industrial_pdf_template', 'proposal_cover_image'
        ).filter(pk=1).first()
        if master is None:
            master = QuotationMaster(pk=1, company_name='Heramb Industries')

    if request.method == 'POST' and template_key == 'standard_industrial':
        action = (request.POST.get('action') or '').strip()
        try:
            if action == 'about' or request.FILES.get('proposal_about_image'):
                from django.core.files.storage import default_storage
                from .cover_render import PROPOSAL_ABOUT_MEDIA
                upload = request.FILES.get('proposal_about_image')
                if not upload:
                    messages.error(request, 'Please choose an About page image.')
                else:
                    if default_storage.exists(PROPOSAL_ABOUT_MEDIA):
                        default_storage.delete(PROPOSAL_ABOUT_MEDIA)
                    default_storage.save(PROPOSAL_ABOUT_MEDIA, upload)
                    messages.success(request, 'About page image saved.')
            elif request.FILES.get('proposal_cover_image'):
                master.proposal_cover_image = request.FILES['proposal_cover_image']
                master.save(update_fields=['proposal_cover_image'])
                messages.success(request, 'Cover page image saved.')
            else:
                messages.error(request, 'Please choose an image file to upload.')
        except (ProgrammingError, OperationalError):
            try:
                connection.rollback()
            except Exception:
                pass
            messages.error(request, 'Could not save image.')
        except Exception as exc:
            messages.error(request, 'Could not save image: %s' % exc)
        return redirect('quotation:edit_quotation_template', template_key=template_key)

    about_image_url = ''
    try:
        from .cover_render import about_image_public_url
        about_image_url = about_image_public_url()
    except Exception:
        about_image_url = ''

    label = next(item['label'] for item in PDF_TEMPLATE_OPTIONS if item['key'] == template_key)
    return render(request, 'quotation/edit_quotation_template.html', {
        'master': master,
        'template_key': template_key,
        'template_label': label,
        'default_pdf_template': get_default_pdf_template(),
        'about_image_url': about_image_url,
    })
