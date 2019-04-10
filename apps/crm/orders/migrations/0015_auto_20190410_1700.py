# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-10 17:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_auto_20190410_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oriorderinfo',
            name='tocustomer_status',
            field=models.SmallIntegerField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, verbose_name='生成客户信息状态'),
        ),
        migrations.AlterField(
            model_name='oriorderinfo',
            name='totendency_ac_status',
            field=models.SmallIntegerField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, verbose_name='生成消费能力状态'),
        ),
        migrations.AlterField(
            model_name='oriorderinfo',
            name='totendency_ha_status',
            field=models.SmallIntegerField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, verbose_name='生成习惯区域状态'),
        ),
        migrations.AlterField(
            model_name='oriorderinfo',
            name='totendency_ht_status',
            field=models.SmallIntegerField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, verbose_name='生成习惯时间状态'),
        ),
    ]
