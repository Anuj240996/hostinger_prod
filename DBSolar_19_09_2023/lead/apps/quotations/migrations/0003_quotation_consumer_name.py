from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotations', '0002_add_quote_number_sequence'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotation',
            name='consumer_name',
            field=models.CharField(
                blank=True,
                help_text="Optional display name on the PDF; if empty, the selected lead's name is used.",
                max_length=200,
            ),
        ),
    ]
