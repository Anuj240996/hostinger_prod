from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0024_alter_quotation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='termsandcondition',
            name='default_selected',
            field=models.BooleanField(
                default=False,
                help_text='When enabled, pre-selected on new quotation forms.',
            ),
        ),
        migrations.AddField(
            model_name='termsandcondition',
            name='show_in_quotation_form',
            field=models.BooleanField(
                default=True,
                help_text='When enabled, this term appears on create/edit quotation forms.',
            ),
        ),
        migrations.CreateModel(
            name='QuotationMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(default='Heramb Industries', max_length=200)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to='quotation/master/')),
                ('address', models.TextField(blank=True, help_text='Company address shown on quotation PDF footer / letterhead.')),
                ('from_address', models.TextField(blank=True, help_text='From-address block on quotation PDF.')),
                ('header_image', models.ImageField(blank=True, null=True, upload_to='quotation/master/')),
                ('footer_image', models.ImageField(blank=True, null=True, upload_to='quotation/master/')),
                ('subsidy_notes', models.TextField(blank=True, help_text='Subsidy note text shown on quotation PDF.')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Quotation Master',
                'verbose_name_plural': 'Quotation Master',
            },
        ),
        migrations.CreateModel(
            name='QuotationBankDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_name', models.CharField(blank=True, max_length=200)),
                ('gst_no', models.CharField(blank=True, max_length=50)),
                ('pan_no', models.CharField(blank=True, max_length=20)),
                ('account_no', models.CharField(blank=True, max_length=50)),
                ('ifsc_code', models.CharField(blank=True, max_length=20)),
                ('bank_name', models.CharField(blank=True, max_length=100)),
                ('branch_name', models.CharField(blank=True, max_length=100)),
                ('show_in_quotation_form', models.BooleanField(default=True, help_text='Show this bank block on quotation PDF when selected as default.')),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['sort_order', 'id'],
            },
        ),
    ]
