# Generated by Django 2.0.9 on 2019-01-08 11:36

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0050_zaak_hoofdzaak'),
    ]

    operations = [
        migrations.AddField(
            model_name='zaak',
            name='relevante_andere_zaken',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.URLField(max_length=255, verbose_name='URL naar andere zaak'), blank=True, default=list, size=None),
        ),
    ]
