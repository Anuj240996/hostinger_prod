from django.db import migrations, models


def split_defaults(apps, schema_editor):
    QuotationMaster = apps.get_model('quotation', 'QuotationMaster')
    standard_keys = {'quotation', 'standard_industrial'}
    for row in QuotationMaster.objects.all():
        current = getattr(row, 'default_pdf_template', None) or 'quotation'
        if current == 'industrial':
            row.default_pdf_template = 'quotation'
            row.default_industrial_pdf_template = 'industrial'
        elif current in standard_keys:
            row.default_industrial_pdf_template = 'industrial'
        else:
            row.default_pdf_template = 'quotation'
            row.default_industrial_pdf_template = 'industrial'
        row.save(update_fields=['default_pdf_template', 'default_industrial_pdf_template'])


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0029_quotationmaster_proposal_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotationmaster',
            name='default_industrial_pdf_template',
            field=models.CharField(
                choices=[('industrial', 'Sample 1 — Industrial Quotation')],
                default='industrial',
                help_text='Default sample inside the Industrial Quotation card.',
                max_length=40,
            ),
        ),
        migrations.AlterField(
            model_name='quotationmaster',
            name='default_pdf_template',
            field=models.CharField(
                choices=[
                    ('quotation', 'Sample 1 — Standard Invoice'),
                    ('standard_industrial', 'Sample 2 — Standard & Industrial Quotation'),
                ],
                default='quotation',
                help_text='Default sample inside the Standard Quotation card.',
                max_length=40,
            ),
        ),
        migrations.RunPython(split_defaults, migrations.RunPython.noop),
    ]
