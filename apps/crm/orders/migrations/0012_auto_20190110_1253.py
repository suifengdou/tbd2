# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-10 12:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_auto_20190109_1256'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderinfo',
            old_name='invoice_no',
            new_name='logistics_no',
        ),
    ]
