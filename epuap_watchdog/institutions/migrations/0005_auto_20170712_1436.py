# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-12 14:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0004_auto_20170712_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='esp',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
    ]