# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-10-24 09:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockin', '0002_auto_20190928_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockininfo',
            name='status',
            field=models.IntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已入库'), (3, '异常')], default=1, verbose_name='状态'),
        ),
    ]
