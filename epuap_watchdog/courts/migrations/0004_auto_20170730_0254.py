# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-30 02:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0017_auto_20170730_0250'),
        ('courts', '0003_regonguest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='regonguest',
            name='institution',
        ),
        migrations.AddField(
            model_name='regonguest',
            name='regon',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='institutions.REGON'),
            preserve_default=False,
        ),
    ]
