# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-12 12:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistant_refund_jdfbp', '0010_auto_20181212_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refundresource',
            name='handlingstatus',
            field=models.CharField(choices=[(0, '未审核'), (1, '已处理'), (2, '已完结')], default=0, max_length=30, verbose_name='最终录入状态'),
        ),
    ]
