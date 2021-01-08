# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-01-01 14:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorderdp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workorderdealerpart',
            name='broken_part',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='故障部位'),
        ),
        migrations.AddField(
            model_name='workorderdealerpart',
            name='description',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='故障描述'),
        ),
        migrations.AddField(
            model_name='workorderdealerpart',
            name='m_sn',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='机器序列号'),
        ),
        migrations.AlterField(
            model_name='workorderdealerpart',
            name='mistake_tag',
            field=models.SmallIntegerField(choices=[(0, '正常'), (1, '一个订单不可重复递交'), (2, '同一收件人有多个订单'), (3, '货品名称包含整机不是配件'), (4, '货品名称错误，或者货品格式错误'), (5, '店铺错误'), (6, '手机号错误'), (7, '地址是集运仓'), (8, '收货人信息不全'), (9, '14天内重复递交过订单'), (10, '14天外重复递交过订单'), (11, '创建配件发货单错误'), (12, '无三级区县'), (13, '售后配件需要补全sn、部件和描述')], default=0, verbose_name='错误原因'),
        ),
    ]
