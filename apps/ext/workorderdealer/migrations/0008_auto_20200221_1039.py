# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-02-21 10:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorderdealer', '0007_auto_20200221_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='mistake_tag',
            field=models.SmallIntegerField(choices=[(0, '正常'), (1, '返回单号为空'), (2, '处理意见为空'), (3, '经销商反馈为空'), (4, '先标记为已处理才能审核'), (5, '先标记为已对账才能审核'), (6, '正常'), (7, '正常'), (8, '正常')], default=0, verbose_name='错误原因'),
        ),
    ]