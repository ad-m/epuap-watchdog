# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-18 02:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0012_auto_20170718_0235'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='esp',
            unique_together=set([('institution', 'name')]),
        ),
    ]
