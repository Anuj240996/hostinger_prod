from django.db import migrations, models


def copy_gst_pan_from_bank(apps, schema_editor):
    QuotationMaster = apps.get_model('quotation', 'QuotationMaster')
    QuotationBankDetail = apps.get_model('quotation', 'QuotationBankDetail')
    master, _ = QuotationMaster.objects.get_or_create(pk=1)
    if master.gst_no and master.pan_no:
        return
    bank = (
        QuotationBankDetail.objects.filter(is_default=True).order_by('id').first()
        or QuotationBankDetail.objects.order_by('id').first()
    )
    if not bank:
        return
    changed = False
    if not master.gst_no and bank.gst_no:
        master.gst_no = bank.gst_no
        changed = True
    if not master.pan_no and bank.pan_no:
        master.pan_no = bank.pan_no
        changed = True
    if changed:
        master.save(update_fields=['gst_no', 'pan_no'])


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0026_alter_quotationbankdetail_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotationmaster',
            name='gst_no',
            field=models.CharField(blank=True, help_text='Company GST number on quotation PDF.', max_length=50),
        ),
        migrations.AddField(
            model_name='quotationmaster',
            name='pan_no',
            field=models.CharField(blank=True, help_text='Company PAN number on quotation PDF.', max_length=20),
        ),
        migrations.RunPython(copy_gst_pan_from_bank, migrations.RunPython.noop),
    ]
