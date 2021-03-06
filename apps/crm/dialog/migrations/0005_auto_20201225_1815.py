# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-25 18:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialog', '0004_auto_20201225_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oridetailtb',
            name='mistake_tag',
            field=models.SmallIntegerField(choices=[(0, '正常'), (1, '对话格式错误'), (2, '重复导入'), (3, '差价货品名称错误'), (4, '差价金额填写错误'), (5, '差价收款人姓名错误'), (6, '差价支付宝名称错误'), (7, '差价订单号错误'), (8, '差价核算公式格式错误'), (9, '差价核算公式计算错误'), (10, '差价核算结果与上报差价不等'), (11, '差价类型只能是1或者3')], default=0, verbose_name='错误列表'),
        ),
    ]
