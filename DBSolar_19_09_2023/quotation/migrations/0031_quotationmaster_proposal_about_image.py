from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0030_quotationmaster_default_industrial_pdf_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotationmaster',
            name='proposal_about_image',
            field=models.ImageField(
                blank=True,
                help_text='About-page photo for Sample 2 (Standard & Industrial) quotation.',
                null=True,
                upload_to='quotation/master/',
            ),
        ),
    ]
