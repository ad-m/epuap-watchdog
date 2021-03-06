# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-15 17:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

def delete_all(apps, schema_editor):
    CityHall = apps.get_model('cityhalls', 'cityhall')
    CityHall.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('cityhalls', '0006_auto_20170815_1709'),
    ]

    operations = [
        migrations.RunPython(delete_all),
        migrations.AlterField(
            model_name='cityhall',
            name='detected_regon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='institutions.REGON'),
        ),
    ]
