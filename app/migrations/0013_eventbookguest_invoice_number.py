# Generated by Django 4.1.3 on 2024-06-21 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_invoice_cash_amount_invoice_online_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventbookguest',
            name='invoice_number',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
