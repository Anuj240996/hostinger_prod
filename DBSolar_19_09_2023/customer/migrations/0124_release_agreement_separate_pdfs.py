from django.db import migrations, models


def copy_legacy_pdf_to_release(apps, schema_editor):
    Doc = apps.get_model('customer', 'ConsumerReleaseAgreement')
    for row in Doc.objects.all():
        if row.pdf and not row.release_pdf:
            row.release_pdf = row.pdf
            row.save(update_fields=['release_pdf'])


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0123_consumerreleaseagreement'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumerreleaseagreement',
            name='release_pdf',
            field=models.FileField(blank=True, upload_to='release_agreements/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='consumerreleaseagreement',
            name='agreement_pdf',
            field=models.FileField(blank=True, upload_to='release_agreements/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='consumerreleaseagreement',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.RunPython(copy_legacy_pdf_to_release, migrations.RunPython.noop),
    ]
