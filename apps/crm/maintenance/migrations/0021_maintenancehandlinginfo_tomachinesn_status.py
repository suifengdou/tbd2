# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-22 10:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0020_auto_20190420_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenancehandlinginfo',
            name='tomachinesn_status',
            field=models.SmallIntegerField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, verbose_name='递交序列号列表状态'),
        ),
    ]
