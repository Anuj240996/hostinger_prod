from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0027_quotationmaster_gst_pan'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotationmaster',
            name='default_pdf_template',
            field=models.CharField(
                choices=[
                    ('quotation', 'Standard Quotation'),
                    ('industrial', 'Industrial Quotation'),
                    ('standard_industrial', 'Standard & Industrial Quotation'),
                ],
                default='quotation',
                help_text='Default quotation PDF template used in the software.',
                max_length=40,
            ),
        ),
    ]
