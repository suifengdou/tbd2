# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-26 10:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20201212_0916'),
    ]

    operations = [
        migrations.CreateModel(
            name='OriBMSOrderInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('buyer_nick', models.CharField(db_index=True, max_length=150, verbose_name='买家昵称')),
                ('trade_no', models.CharField(db_index=True, max_length=60, verbose_name='订单编号')),
                ('receiver_name', models.CharField(max_length=150, verbose_name='收货人姓名')),
                ('receiver_address', models.CharField(max_length=256, verbose_name='收货人地址')),
                ('province', models.CharField(max_length=40, verbose_name='省')),
                ('city', models.CharField(max_length=40, verbose_name='市')),
                ('district', models.CharField(max_length=40, verbose_name='区')),
                ('street', models.CharField(max_length=40, verbose_name='街道')),
                ('receiver_mobile', models.CharField(db_index=True, max_length=40, verbose_name='手机')),
                ('pay_time', models.DateTimeField(verbose_name='支付时间')),
                ('logistics_no', models.CharField(blank=True, max_length=150, null=True, verbose_name='运单号')),
                ('cs_remark', models.TextField(blank=True, max_length=800, null=True, verbose_name='卖家备注')),
                ('src_tids', models.CharField(db_index=True, max_length=120, verbose_name='交易订单号')),
                ('num', models.IntegerField(verbose_name='订货数量')),
                ('price', models.FloatField(verbose_name='订单金额')),
                ('share_amount', models.FloatField(verbose_name='商品小计')),
                ('goods_name', models.CharField(max_length=255, verbose_name='商品名称')),
                ('spec_code', models.CharField(db_index=True, max_length=150, verbose_name='商品编码')),
                ('shop_name', models.CharField(max_length=128, verbose_name='店铺名称')),
                ('logistics_name', models.CharField(blank=True, max_length=60, null=True, verbose_name='快递公司')),
                ('warehouse_name', models.CharField(max_length=100, verbose_name='仓库名称')),
                ('order_category', models.CharField(db_index=True, max_length=40, verbose_name='订单类型')),
                ('deliver_time', models.DateTimeField(db_index=True, verbose_name='发货时间')),
                ('ori_order_status', models.CharField(max_length=40, verbose_name='状态')),
                ('goods_weight', models.CharField(max_length=40, verbose_name='商品重量(克)')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], db_index=True, default=1, verbose_name='单据状态')),
                ('process_tag', models.SmallIntegerField(choices=[(0, '未处理'), (1, '待核实'), (2, '已确认'), (3, '待清理'), (4, '已处理'), (5, '驳回'), (6, '特殊订单')], default=0, verbose_name='处理标签')),
                ('mistake_tag', models.SmallIntegerField(choices=[(0, '正常'), (1, '已导入过的订单'), (2, '待确认重复订单')], default=0, verbose_name='错误列表')),
            ],
            options={
                'verbose_name': 'CRM-原始BMS订单-查询',
                'verbose_name_plural': 'CRM-原始BMS订单-查询',
                'db_table': 'crm_o_bms_oriorderinfo',
            },
        ),
        migrations.CreateModel(
            name='SubmitOBMSOrder',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-原始BMS订单-未提交',
                'verbose_name_plural': 'CRM-原始BMS订单-未提交',
                'proxy': True,
                'indexes': [],
            },
            bases=('orders.oribmsorderinfo',),
        ),
    ]
