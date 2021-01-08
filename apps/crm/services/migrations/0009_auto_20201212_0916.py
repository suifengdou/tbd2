# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-12 09:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_auto_20201210_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicesinfo',
            name='order_type',
            field=models.SmallIntegerField(choices=[(1, '电话'), (2, '短信'), (3, '旺旺留言')], default=1, verbose_name='任务类型'),
        ),
        migrations.AlterField(
            model_name='servicesdetail',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='目标是否达成'),
        ),
        migrations.AlterField(
            model_name='servicesdetail',
            name='outcome',
            field=models.SmallIntegerField(blank=True, choices=[(1, '电话连通'), (2, '电话未通'), (3, '短信已发'), (4, '旺旺已留言'), (5, '旺旺留言失败')], null=True, verbose_name='结果'),
        ),
        migrations.AlterField(
            model_name='servicesinfo',
            name='order_category',
            field=models.SmallIntegerField(choices=[(1, '电话'), (2, '短信'), (3, '旺旺留言')], db_index=True, default=1, verbose_name='任务执行类型'),
        ),
    ]