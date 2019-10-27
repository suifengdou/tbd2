# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-10-18 11:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planorder', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='planorderinfo',
            name='status',
        ),
        migrations.AddField(
            model_name='planorderinfo',
            name='order_status',
            field=models.IntegerField(choices=[(0, '取消'), (1, '未处理'), (2, '待确认'), (3, '已递交'), (4, '异常')], default=1, verbose_name='计划采购单状态'),
        ),
    ]