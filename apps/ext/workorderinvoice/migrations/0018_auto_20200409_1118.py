# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-04-09 11:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorderinvoice', '0017_auto_20200407_1657'),
    ]

    operations = [
        migrations.CreateModel(
            name='WOApply',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-发票工单-待申请',
                'verbose_name_plural': 'EXT-发票工单-待申请',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderinvoice.workorder',),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='process_tag',
            field=models.SmallIntegerField(choices=[(0, '未处理'), (1, '开票中'), (2, '已开票'), (3, '待买票'), (4, '信息错'), (5, '被驳回'), (6, '已处理'), (7, '未申请')], default=0, verbose_name='处理标签'),
        ),
    ]