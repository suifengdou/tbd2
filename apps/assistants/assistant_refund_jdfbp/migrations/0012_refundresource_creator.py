# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-17 09:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistant_refund_jdfbp', '0011_auto_20181212_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='refundresource',
            name='creator',
            field=models.CharField(default='system', max_length=30, verbose_name='创建者'),
        ),
    ]
