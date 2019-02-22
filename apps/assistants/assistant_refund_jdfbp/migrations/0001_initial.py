# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-03 07:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RefundResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('service_order_id', models.CharField(max_length=30, verbose_name='服务单号')),
                ('order_id', models.CharField(max_length=30, verbose_name='订单号')),
                ('goods_id', models.CharField(max_length=30, verbose_name='商品编号')),
                ('goods_name', models.CharField(max_length=250, verbose_name='商品名称')),
                ('goods_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='商品金额')),
                ('order_status', models.CharField(max_length=20, verbose_name='服务单状态')),
                ('application_time', models.DateTimeField(blank=True, null=True, verbose_name='售后服务单申请时间')),
                ('bs_initial_time', models.DateTimeField(blank=True, null=True, verbose_name='商家首次审核时间')),
                ('bs_handle_time', models.DateTimeField(verbose_name='商家首次处理时间')),
                ('duration', models.IntegerField(verbose_name='售后处理时长')),
                ('bs_result', models.CharField(blank=True, max_length=20, null=True, verbose_name='审核结果')),
                ('bs_result_desc', models.CharField(blank=True, max_length=20, null=True, verbose_name='处理结果描述')),
                ('buyer_expectation', models.CharField(max_length=20, verbose_name='客户预期处理方式')),
                ('return_model', models.CharField(max_length=20, verbose_name='返回方式')),
                ('buyer_problem_desc', models.CharField(blank=True, max_length=250, null=True, verbose_name='客户问题描述')),
                ('last_handle_time', models.DateTimeField(blank=True, max_length=20, null=True, verbose_name='最新审核时间')),
                ('handle_opinion', models.CharField(blank=True, max_length=250, null=True, verbose_name='审核意见')),
                ('handler_name', models.CharField(max_length=20, verbose_name='审核人姓名')),
                ('take_delivery_time', models.DateTimeField(blank=True, null=True, verbose_name='取件时间')),
                ('take_delivery_status', models.CharField(blank=True, max_length=20, null=True, verbose_name='取件状态')),
                ('delivery_time', models.CharField(blank=True, max_length=20, null=True, verbose_name='发货时间')),
                ('express_id', models.CharField(max_length=30, verbose_name='运单号')),
                ('express_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='运费金额')),
                ('express_company', models.CharField(max_length=20, verbose_name='快递公司')),
                ('receive_time', models.DateTimeField(blank=True, null=True, verbose_name='商家收货时间')),
                ('refund_reason', models.CharField(blank=True, max_length=50, null=True, verbose_name='收货登记原因')),
                ('receiver', models.CharField(blank=True, max_length=20, null=True, verbose_name='收货人')),
                ('completer', models.CharField(blank=True, max_length=20, null=True, verbose_name='处理人')),
                ('refund_amount', models.CharField(blank=True, max_length=20, null=True, verbose_name='退款金额')),
                ('renew_express_id', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, verbose_name='换新订单')),
                ('renew_goods_id', models.CharField(blank=True, max_length=20, null=True, verbose_name='换新商品编号')),
                ('is_quick_refund', models.CharField(blank=True, max_length=10, null=True, verbose_name='是否闪退订单')),
            ],
            options={
                'verbose_name': '京东FBP退库单源数据',
                'verbose_name_plural': '京东FBP退库单源数据',
            },
        ),
    ]
