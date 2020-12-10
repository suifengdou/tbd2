# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-27 10:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountIdList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('ori_order_trade_no', models.CharField(db_index=True, max_length=120, unique=True, verbose_name='计数单号列表')),
            ],
            options={
                'verbose_name': 'CRM-C-计数单号列表',
                'verbose_name_plural': 'CRM-C-计数单号列表',
                'db_table': 'crm_c_order_countlist',
            },
        ),
        migrations.CreateModel(
            name='CustomerInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('mobile', models.CharField(db_index=True, max_length=30, unique=True, verbose_name='手机')),
                ('e_mail', models.EmailField(blank=True, max_length=254, null=True, verbose_name='电子邮件')),
                ('qq', models.CharField(blank=True, max_length=30, null=True, verbose_name='QQ')),
                ('wangwang', models.CharField(blank=True, max_length=60, null=True, verbose_name='旺旺')),
                ('jdfbp_id', models.CharField(blank=True, max_length=60, null=True, verbose_name='京东FBP账号')),
                ('jdzy_id', models.CharField(blank=True, max_length=60, null=True, verbose_name='京东自营账号')),
                ('gfsc_id', models.CharField(blank=True, max_length=60, null=True, verbose_name='官方商城账号')),
                ('alipay_id', models.CharField(blank=True, max_length=60, null=True, verbose_name='支付宝账号')),
                ('pdd_id', models.CharField(blank=True, max_length=60, null=True, verbose_name='拼多多账号')),
                ('wechat', models.CharField(blank=True, max_length=60, null=True, verbose_name='微信号')),
                ('others_id', models.CharField(blank=True, max_length=60, null=True, verbose_name='其他平台')),
                ('birthday', models.DateTimeField(blank=True, null=True, verbose_name='生日')),
                ('total_amount', models.FloatField(default=0, verbose_name='购买总金额')),
                ('total_times', models.IntegerField(default=0, verbose_name='购买总次数')),
                ('last_time', models.DateTimeField(blank=True, null=True, verbose_name='最近购买时间')),
                ('return_time', models.DateTimeField(blank=True, null=True, verbose_name='最后一次回访时间')),
                ('contact_times', models.IntegerField(blank=True, default=0, null=True, verbose_name='回访关怀次数')),
                ('free_service_times', models.IntegerField(default=0, verbose_name='无金额发货次数')),
                ('maintenance_times', models.IntegerField(default=0, verbose_name='中央维修次数')),
                ('memorandum', models.CharField(blank=True, max_length=30, null=True, verbose_name='备注')),
                ('order_failure_times', models.IntegerField(default=0, verbose_name='退款次数')),
            ],
            options={
                'verbose_name': 'CRM-C-客户信息',
                'verbose_name_plural': 'CRM-C-客户信息',
                'db_table': 'crm_c_customerinfo',
            },
        ),
        migrations.CreateModel(
            name='OrderList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='orders.OrderInfo', verbose_name='订单')),
            ],
            options={
                'verbose_name': 'CRM-C-订单列表',
                'verbose_name_plural': 'CRM-C-订单列表',
                'db_table': 'crm_c_order_list',
            },
        ),
    ]
