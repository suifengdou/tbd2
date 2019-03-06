# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-03-05 14:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenancehandlinginfo',
            name='handling_status',
            field=models.CharField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, max_length=30, verbose_name='操作状态'),
        ),
        migrations.AlterField(
            model_name='maintenancehandlinginfo',
            name='is_guarantee',
            field=models.CharField(max_length=50, verbose_name='是否在保'),
        ),
        migrations.AlterField(
            model_name='maintenancehandlinginfo',
            name='repeat_tag',
            field=models.CharField(choices=[(0, '正常'), (1, '未处理'), (2, '产品'), (3, '维修'), (4, '客服')], default=0, max_length=30, verbose_name='重复维修标记'),
        ),
    ]
