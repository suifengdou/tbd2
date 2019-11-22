# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-11-19 17:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockOutInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('stockout_id', models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='出库单号')),
                ('source_order_id', models.CharField(max_length=30, verbose_name='关联单号')),
                ('order_status', models.IntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], default=1, verbose_name='状态')),
                ('category', models.IntegerField(choices=[(0, '常规出库'), (1, '客供出库'), (2, '配件出库')], default=0, verbose_name='出库类型')),
                ('goods_name', models.CharField(max_length=60, verbose_name='货品名称')),
                ('goods_id', models.CharField(max_length=30, verbose_name='货品编码')),
                ('quantity', models.IntegerField(verbose_name='发货数量')),
                ('nickname', models.CharField(blank=True, max_length=60, null=True, verbose_name='昵称')),
                ('receiver', models.CharField(blank=True, max_length=60, null=True, verbose_name='收货人')),
                ('province', models.CharField(blank=True, max_length=30, null=True, verbose_name='省份')),
                ('city', models.CharField(blank=True, max_length=30, null=True, verbose_name='城市')),
                ('district', models.CharField(blank=True, max_length=60, null=True, verbose_name='区县')),
                ('mobile', models.CharField(blank=True, max_length=30, null=True, verbose_name='收货人手机')),
                ('memorandum', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('address', models.CharField(blank=True, max_length=160, null=True, verbose_name='地址')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.WarehouseInfo', verbose_name='仓库名称')),
            ],
            options={
                'verbose_name': 'WMS-O-出库单',
                'verbose_name_plural': 'WMS-O-出库单',
                'db_table': 'wms_stk_stockout',
            },
        ),
        migrations.CreateModel(
            name='StockOutPenddingInfo',
            fields=[
            ],
            options={
                'verbose_name': 'WMS-O-未审核出库单',
                'verbose_name_plural': 'WMS-O-未审核出库单',
                'proxy': True,
                'indexes': [],
            },
            bases=('stockout.stockoutinfo',),
        ),
    ]
