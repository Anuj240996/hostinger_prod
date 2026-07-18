import io
import os
from decimal import Decimal, InvalidOperation
from html import escape

from django.contrib.staticfiles import finders

DEFAULT_COMPANY_NAME = 'HERAMB INDUSTRIES'
DEFAULT_COMPANY_ADDRESS = (
    'Sales - On-Grid / Off-Grid Solar, REGD ADDRESS : Bhagya Bangla,\n'
    'Block No. 2,Opp - Sant Eknamth Mandir,New Osmanpura,\n'
    'Chh.Sambhaji Nagar. Maharashtra, 431001,\n'
    'EMAIL : herambasd1@gmail.com , GSTIN/UIN : 27AIPPD9639R1Z6'

    
    )
DEFAULT_LOGO_STATIC = 'images/db_logo_200.png'


def format_organization_address(org):
    if not org:
        return ''
    city_line = ', '.join(p for p in (org.city, org.state, org.postal_code) if p)
    parts = [org.address_line1, org.address_line2, city_line, org.country]
    return ', '.join(str(p).strip() for p in parts if p and str(p).strip())


def format_lead_address(lead):
    parts = [lead.address, lead.city, lead.state, lead.pincode]
    return ', '.join(str(p).strip() for p in parts if p and str(p).strip())


def get_survey_report_branding(request):
    org = getattr(request, 'organization', None)
    # Force requested branding for survey report output.
    name = DEFAULT_COMPANY_NAME
    address = DEFAULT_COMPANY_ADDRESS
    logo_path = None
    logo_url = None

    if org and org.logo:
            try:
                logo_path = org.logo.path
                logo_url = request.build_absolute_uri(org.logo.url)
            except (ValueError, OSError):
                logo_url = request.build_absolute_uri(org.logo.url)

    if not logo_path or not os.path.isfile(logo_path):
        found = finders.find(DEFAULT_LOGO_STATIC)
        if found and os.path.isfile(found):
            logo_path = found

    if not logo_url:
        from django.templatetags.static import static

        logo_url = request.build_absolute_uri(static(DEFAULT_LOGO_STATIC))

    return {
        'company_name': name,
        'company_address': address,
        'logo_path': logo_path if logo_path and os.path.isfile(logo_path) else None,
        'logo_url': logo_url,
        'organization': org,
    }


def _display(value, suffix='', default='—'):
    if value is None or value == '':
        return default
    return f'{_format_number(value)}{suffix}'


def _format_number(value):
    """Show integers without .00; keep decimals when present."""
    if value is None or value == '':
        return ''
    try:
        dec_value = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return str(value)
    text = format(dec_value, 'f')
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    return text


def _clean_pdf_text(value):
    """Normalize common mojibake sequences before rendering PDF text."""
    text = str(value or '—')
    if 'â‚¹' in text:
        text = text.replace('â‚¹', '₹')
    if 'â€”' in text:
        text = text.replace('â€”', '—')
    # Defensive decode path for UTF-8 text misread as latin-1/cp1252.
    try:
        if any(ch in text for ch in ('â', 'Ã', 'â‚')):
            fixed = text.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')
            if fixed:
                text = fixed
    except Exception:
        pass
    return text


def _format_inr(value):
    """Format number with Indian rupee symbol for PDF output."""
    if value is None or value == '':
        return '—'
    try:
        amount = float(value)
        return f'₹{amount:,.2f}'
    except (TypeError, ValueError):
        return f'₹{value}'


def build_survey_report_pdf(survey, branding, structure_3d_png=None):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    pdf_font_name = 'Helvetica'
    try:
        font_candidates = [
            r'C:\Windows\Fonts\arial.ttf',
            r'C:\Windows\Fonts\calibri.ttf',
            r'C:\Windows\Fonts\segoeui.ttf',
        ]
        for font_path in font_candidates:
            if os.path.isfile(font_path):
                pdfmetrics.registerFont(TTFont('SurveyUnicode', font_path))
                pdf_font_name = 'SurveyUnicode'
                break
    except Exception:
        pdf_font_name = 'Helvetica'

    normal = styles['Normal']
    normal.fontSize = 9
    normal.fontName = pdf_font_name
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName=pdf_font_name,
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontName=pdf_font_name,
        fontSize=11,
        textColor=colors.HexColor('#1f4e79'),
        spaceBefore=6,
        spaceAfter=6,
    )
    elements = []

    logo_cell = ''
    logo_path = branding.get('logo_path')
    if logo_path:
        try:
            logo_cell = Image(logo_path, width=48, height=48)
        except Exception:
            logo_cell = ''

    header_right = (
        f"<b>Survey #{survey.pk}</b><br/>"
        f"Completed: {survey.completed_date.strftime('%d %b %Y') if survey.completed_date else '—'}"
    )
    company_address_pdf = '<br/>'.join(
        escape(line.strip()) for line in str(branding['company_address']).splitlines() if line.strip()
    )

    header_data = [[
        logo_cell,
        Paragraph(
            f"<b>{escape(branding['company_name'])}</b><br/>{company_address_pdf}",
            normal,
        ),
        Paragraph(header_right, normal),
    ]]
    header_table = Table(header_data, colWidths=[56, 330, 110])
    header_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph('SITE SURVEY REPORT', title_style))
    elements.append(Spacer(1, 8))

    lead = survey.lead

    def section_table(title, rows):
        elements.append(Paragraph(title, section_style))
        data = []
        for label, value in rows:
            data.append([
                Paragraph(f'<b>{label}</b>', normal),
                Paragraph(_clean_pdf_text(value), normal),
            ])
        table = Table(data, colWidths=[160, 336])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.6, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 8))

    section_table('Client / Lead Details', [
        ('Name', lead.name),
        ('Phone', lead.phone),
        ('Email', lead.email or '—'),
        ('Address', format_lead_address(lead)),
        ('Latitude', str(lead.latitude) if lead.latitude is not None else '—'),
        ('Longitude', str(lead.longitude) if lead.longitude is not None else '—'),
        ('Property Type', lead.get_property_type_display()),
        ('Roof Type', lead.get_roof_type_display()),
        ('Monthly Electricity Bill', _format_inr(lead.electricity_bill)),
    ])

    engineer_name = survey.engineer.get_full_name() if survey.engineer else '—'
    if survey.engineer and not engineer_name.strip():
        engineer_name = survey.engineer.username

    section_table('Survey Information', [
        ('Status', survey.get_status_display()),
        ('Scheduled', survey.scheduled_date.strftime('%d %b %Y, %I:%M %p')),
        ('Completed', survey.completed_date.strftime('%d %b %Y, %I:%M %p') if survey.completed_date else '—'),
        ('Site Engineer', engineer_name),
        ('Feasibility', survey.get_feasibility_display() if survey.feasibility else '—'),
    ])

    section_table('Technical Details', [
        ('Recommended Size', _display(survey.recommended_size, ' kW')),
        ('Panel Capacity', _display(survey.panel_count, ' W')),
        ('Inverter Capacity', _display(survey.inverter_capacity, ' kW')),
        ('Est. Yearly Generation', _display(survey.estimated_generation, ' Units/year')),
        ('Building Height', _display(survey.building_height, ' Mtr')),
        ('Structure Type', survey.get_structure_type_display() if survey.structure_type else '—'),
    ])

    if survey.structure_type and survey.structure_type != 'tin_shade':
        section_table('Solar Structure', [
            ('Front Height', _display(survey.structure_front_height_ft, ' ft')),
            ('Back Height', _display(survey.structure_back_height_ft, ' ft')),
            ('Legs', _display(survey.structure_leg_count, ' Nos.')),
            ('Rafters', _display(survey.structure_rafter_count, ' Nos.')),
            ('Purlins', _display(survey.structure_purlin_count, ' Nos.')),
            ('Solar Panels on Structure', _display(survey.structure_solar_panel_count, ' Nos.')),
        ])

    from .structure_diagram_svg import (
        structure_diagram_reportlab_image,
        structure_front3d_reportlab_image,
        structure_diagram_summary_text,
        survey_has_structure_layout,
    )

    if structure_3d_png:
        try:
            from reportlab.lib.utils import ImageReader

            img_buf = io.BytesIO(structure_3d_png)
            img_buf.seek(0)
            reader = ImageReader(img_buf)
            iw, ih = reader.getSize()
            img_w = 420
            img_h = img_w * (ih / iw) if iw else 260
            img_buf.seek(0)
            elements.append(Paragraph('3D Structure (Front View)', section_style))
            elements.append(Paragraph(
                'Front-view snapshot from the survey page 3D structure viewer.',
                normal,
            ))
            elements.append(Spacer(1, 4))
            elements.append(Image(img_buf, width=img_w, height=min(img_h, 360)))
            elements.append(Spacer(1, 8))
        except Exception:
            pass

    if survey_has_structure_layout(survey) and not structure_3d_png:
        # Prefer static 3D SVG (includes optional walkway/ladder) over 2D plan+side.
        front3d_img = None
        diagram_img = None
        try:
            front3d_img = structure_front3d_reportlab_image(survey, width=420, height=320)
        except Exception:
            front3d_img = None
        if front3d_img:
            elements.append(Paragraph('3D Structure (Front View)', section_style))
            elements.append(Spacer(1, 4))
            elements.append(front3d_img)
            elements.append(Spacer(1, 8))
        else:
            try:
                diagram_img = structure_diagram_reportlab_image(survey)
            except Exception:
                diagram_img = None
            if diagram_img:
                summary = structure_diagram_summary_text(survey)
                elements.append(Paragraph('Solar Structure Layout', section_style))
                if summary:
                    elements.append(Paragraph(summary, normal))
                    elements.append(Spacer(1, 4))
                elements.append(diagram_img)
                elements.append(Spacer(1, 8))

    def wall_label(direction, length, used):
        used_txt = ' (Used)' if used else ''
        return f'{_display(length, " ft")}{used_txt}'

    section_table('Roof Area & Wall Lengths', [
        ('North', wall_label('N', survey.length_north_ft, survey.area_use_north)),
        ('South', wall_label('S', survey.length_south_ft, survey.area_use_south)),
        ('East', wall_label('E', survey.length_east_ft, survey.area_use_east)),
        ('West', wall_label('W', survey.length_west_ft, survey.area_use_west)),
        ('Total Roof Area', _display(survey.roof_area_required, ' sq.ft')),
    ])

    shadow = 'Shadow issues detected' if survey.has_shadow_issues else 'No shadow issues'
    structural = 'Feasible' if survey.structural_feasible else 'Not feasible'
    section_table('Feasibility Analysis', [
        ('Shadow Analysis', shadow),
        ('Structural Feasibility', structural),
    ])

    notes = (survey.technical_notes or '').strip() or 'No technical notes.'
    elements.append(Paragraph('Technical Notes', section_style))
    elements.append(Paragraph(notes.replace('\n', '<br/>'), normal))
    elements.append(Spacer(1, 8))

    images = list(survey.roof_images.all())
    if images:
        elements.append(Paragraph('Survey Photos', section_style))
        for idx, img in enumerate(images[:3]):
            try:
                path = img.image.path
                if os.path.isfile(path):
                    elements.append(Image(path, width=160, height=120))
                    if idx < len(images[:3]) - 1:
                        elements.append(Spacer(1, 6))
            except (ValueError, OSError):
                continue

    signature_data = [
        [
            Paragraph('<b>Checked / Assigned Engg</b>', normal),
            Paragraph(_clean_pdf_text(engineer_name), normal),
            Paragraph('<b>Date</b>', normal),
            Paragraph(
                survey.completed_date.strftime('%d %b %Y') if survey.completed_date else '—',
                normal
            ),
        ],
        [
            Paragraph('<b>Location</b>', normal),
            Paragraph(_clean_pdf_text(format_lead_address(lead) or '—'), normal),
            Paragraph('<b>Signature</b>', normal),
            Paragraph(' ', normal),
        ],
    ]
    elements.append(Spacer(1, 8))
    elements.append(Paragraph('Signature Details', section_style))
    signature_table = Table(signature_data, colWidths=[120, 180, 70, 126], rowHeights=[22, 30])
    signature_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.6, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f1f5f9')),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(signature_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
