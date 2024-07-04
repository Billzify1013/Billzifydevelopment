# Generated by Django 4.1.3 on 2024-07-04 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_alter_dailymanagement_check_in_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketIteams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=300)),
                ('price', models.IntegerField(default=0)),
                ('ratings', models.CharField(max_length=40)),
            ],
        ),
    ]
