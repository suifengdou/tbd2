# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-04-23 10:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorderinvoice', '0027_auto_20200420_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceorder',
            name='order_status',
            field=models.SmallIntegerField(choices=[(0, '已被取消'), (1, '开票处理'), (2, '终审复核'), (3, '工单完结')], default=1, verbose_name='订单状态'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='mistake_tag',
            field=models.SmallIntegerField(choices=[(0, '正常'), (1, '没开票公司'), (2, '货品错误'), (3, '专票信息缺'), (4, '收件手机错'), (5, '超限额发票'), (6, '递交发票订单出错'), (7, '生成发票货品出错'), (8, '单货品超限额非法'), (9, '发票订单生成重复'), (10, '生成发票订单出错'), (11, '生成发票订单货品出错'), (12, '单据被驳回'), (13, '税号错误'), (14, '源单号格式错误'), (15, '导入货品错误')], default=0, verbose_name='错误原因'),
        ),
    ]