# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-12 17:41
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0006_auto_20170712_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='REGON',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('regon', models.CharField(db_index=True, max_length=20, null=True, verbose_name='REGON  number')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(help_text='Data for database search results REGON BIP1', verbose_name='Response data')),
                ('institution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='regon_data', to='institutions.Institution', verbose_name='Institution')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
