from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0028_quotationmaster_default_pdf_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotationmaster',
            name='proposal_cover_image',
            field=models.ImageField(
                blank=True,
                help_text='Left-column cover photo for Standard & Industrial quotation.',
                null=True,
                upload_to='quotation/master/',
            ),
        ),
    ]
