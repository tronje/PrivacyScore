# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-10 14:39
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_auto_20170509_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scanresult',
            name='result',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
    ]
