from django.db import migrations, models
from django.utils import timezone

def populate_sequence(apps, schema_editor):
    QuoteNumberSequence = apps.get_model('quotations', 'QuoteNumberSequence')
    Quotation = apps.get_model('quotations', 'Quotation')
    # Group existing quotes by year
    quotes = Quotation.objects.all()
    year_dict = {}
    for q in quotes:
        # Extract year from quote_number if possible, else use created date
        if q.quote_number and q.quote_number.startswith('Q-'):
            try:
                parts = q.quote_number.split('-')
                if len(parts) >= 2:
                    year = int(parts[1])
                else:
                    year = q.created.year
            except:
                year = q.created.year
        else:
            year = q.created.year
        year_dict[year] = year_dict.get(year, 0) + 1

    for year, count in year_dict.items():
        # The last number should be at least count
        QuoteNumberSequence.objects.create(year=year, last_number=count)

    # Also ensure current year exists even if no quotes
    current_year = timezone.now().year
    if current_year not in year_dict:
        QuoteNumberSequence.objects.create(year=current_year, last_number=0)

class Migration(migrations.Migration):
    dependencies = [
        # ('quotations', 'XXXX_previous_migration'),  # replace with actual last migration
        ('quotations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuoteNumberSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(unique=True)),
                ('last_number', models.IntegerField(default=0)),
            ],
        ),
        migrations.RunPython(populate_sequence),
    ]