# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-12 13:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0002_auto_20170712_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='epuap_id',
            field=models.CharField(db_index=True, help_text='Basic Institution ID in ePUAP', max_length=100, unique=True, verbose_name='ePUAP ID'),
        ),
    ]
