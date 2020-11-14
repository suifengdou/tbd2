# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-11-12 17:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20201103_1730'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('buyer_nick', models.CharField(db_index=True, max_length=150, verbose_name='客户网名')),
                ('trade_no', models.CharField(db_index=True, max_length=60, verbose_name='订单编号')),
                ('receiver_name', models.CharField(max_length=150, verbose_name='收件人')),
                ('receiver_address', models.CharField(max_length=256, verbose_name='收货地址')),
                ('receiver_mobile', models.CharField(db_index=True, max_length=40, verbose_name='收件人手机')),
                ('pay_time', models.DateTimeField(verbose_name='付款时间')),
                ('receiver_area', models.CharField(max_length=150, verbose_name='收货地区')),
                ('logistics_no', models.CharField(blank=True, max_length=150, null=True, verbose_name='物流单号')),
                ('buyer_message', models.TextField(blank=True, null=True, verbose_name='买家留言')),
                ('cs_remark', models.TextField(blank=True, max_length=800, null=True, verbose_name='客服备注')),
                ('src_tids', models.TextField(blank=True, null=True, verbose_name='原始子订单号')),
                ('num', models.IntegerField(verbose_name='实发数量')),
                ('price', models.FloatField(verbose_name='成交价')),
                ('share_amount', models.FloatField(verbose_name='货品成交总价')),
                ('goods_name', models.CharField(max_length=255, verbose_name='货品名称')),
                ('spec_code', models.CharField(db_index=True, max_length=150, verbose_name='商家编码')),
                ('shop_name', models.CharField(max_length=128, verbose_name='店铺')),
                ('logistics_name', models.CharField(blank=True, max_length=60, null=True, verbose_name='物流公司')),
                ('warehouse_name', models.CharField(max_length=100, verbose_name='仓库')),
                ('order_category', models.CharField(db_index=True, max_length=40, verbose_name='订单类型')),
                ('deliver_time', models.DateTimeField(db_index=True, verbose_name='发货时间')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], db_index=True, default=1, verbose_name='单据状态')),
                ('process_tag', models.SmallIntegerField(choices=[(0, '未处理'), (1, '待核实'), (2, '已确认'), (3, '待清账'), (4, '已处理'), (5, '特殊订单')], default=0, verbose_name='处理标签')),
                ('mistake_tag', models.SmallIntegerField(choices=[(0, '正常'), (1, '14天内重复订单')], default=0, verbose_name='错误列表')),
            ],
            options={
                'verbose_name': 'CRM-UT订单-查询',
                'verbose_name_plural': 'CRM-UT订单-查询',
                'db_table': 'crm_o_orderinfo',
            },
        ),
        migrations.DeleteModel(
            name='CheckOriOrder',
        ),
        migrations.AlterField(
            model_name='oriorderinfo',
            name='mistake_tag',
            field=models.SmallIntegerField(choices=[(0, '正常'), (1, '待确认重复订单')], default=0, verbose_name='错误列表'),
        ),
        migrations.AlterField(
            model_name='oriorderinfo',
            name='num',
            field=models.IntegerField(verbose_name='货品数量'),
        ),
        migrations.CreateModel(
            name='CheckOrder',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-UT订单-未过滤',
                'verbose_name_plural': 'CRM-UT订单-未过滤',
                'proxy': True,
                'indexes': [],
            },
            bases=('orders.orderinfo',),
        ),
        migrations.CreateModel(
            name='SubmitOrder',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-UT订单-未提交',
                'verbose_name_plural': 'CRM-UT订单-未提交',
                'proxy': True,
                'indexes': [],
            },
            bases=('orders.orderinfo',),
        ),
    ]
