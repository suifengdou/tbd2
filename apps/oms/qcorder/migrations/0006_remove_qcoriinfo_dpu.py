# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-26 13:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qcorder', '0005_qcoriinfo_qc_order_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='qcoriinfo',
            name='dpu',
        ),
    ]
