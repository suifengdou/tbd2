# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-06-04 09:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('giftintalk', '0011_auto_20200527_0919'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='giftimportinfo',
            options={'verbose_name': 'ASS-GT-手工ERP导入单据查询', 'verbose_name_plural': 'ASS-GT-手工ERP导入单据查询'},
        ),
        migrations.AlterModelOptions(
            name='giftimportpendding',
            options={'verbose_name': 'ASS-GT-手工ERP导入单据', 'verbose_name_plural': 'ASS-GT-手工ERP导入单据'},
        ),
        migrations.AlterModelOptions(
            name='giftintalkinfo',
            options={'verbose_name': 'ASS-GT-手工订单提取查询', 'verbose_name_plural': 'ASS-GT-手工订单提取查询'},
        ),
        migrations.AlterModelOptions(
            name='giftintalkpendding',
            options={'verbose_name': 'ASS-GT-手工订单提取递交', 'verbose_name_plural': 'ASS-GT-手工订单提取递交'},
        ),
        migrations.AlterModelOptions(
            name='giftintalkrepeat',
            options={'verbose_name': 'ASS-GT-手工订单提取重复订单罗列', 'verbose_name_plural': 'ASS-GT-手工订单提取重复订单罗列'},
        ),
        migrations.AlterModelOptions(
            name='giftorderinfo',
            options={'verbose_name': 'ASS-GT-手工预订单查询', 'verbose_name_plural': 'ASS-GT-手工预订单查询'},
        ),
        migrations.AlterModelOptions(
            name='giftorderpendding',
            options={'verbose_name': 'ASS-GT-手工预订单处理', 'verbose_name_plural': 'ASS-GT-手工预订单处理'},
        ),
    ]