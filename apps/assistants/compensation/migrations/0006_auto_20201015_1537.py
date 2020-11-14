# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-10-15 15:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compensation', '0005_auto_20200924_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchcompensation',
            name='mistake_tag',
            field=models.SmallIntegerField(choices=[(0, '正常'), (1, '无OA单号'), (2, '先设置订单已完成再审核'), (3, '已递交过此OA单号'), (4, '补寄配件记录格式错误'), (5, '补寄原因错误'), (6, '单据创建失败')], default=0, verbose_name='错误列表'),
        ),
        migrations.AlterField(
            model_name='batchinfo',
            name='mistake_tag',
            field=models.SmallIntegerField(choices=[(0, '正常'), (1, '已付金额不是零，不可重置'), (2, '重置保存补偿单出错'), (3, '补运费和已付不相等'), (4, '补寄配件记录格式错误'), (5, '补寄原因错误'), (6, '单据创建失败')], default=0, verbose_name='错误列表'),
        ),
    ]
