from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0124_release_agreement_separate_pdfs'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumerreleaseagreement',
            name='release_pdf_data',
            field=models.BinaryField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='consumerreleaseagreement',
            name='agreement_pdf_data',
            field=models.BinaryField(blank=True, editable=False, null=True),
        ),
    ]
