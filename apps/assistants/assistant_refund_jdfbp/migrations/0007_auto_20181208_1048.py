# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-08 10:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistant_refund_jdfbp', '0006_auto_20181208_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refundresource',
            name='receive_time',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='商家收货时间'),
        ),
    ]
