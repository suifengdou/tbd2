# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-19 18:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20181219_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='auditor',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='审核人'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='buyer_message',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='买家留言'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='buyer_nick',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='客户网名'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='cash_on_delivery',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='货到付款'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='discreteness_id',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='拆自组合装'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='discreteness_source_id',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='来源组合装编号'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='distributor',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='分销商'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='erp_order_id',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='订单编号'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='gift_type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='赠品方式'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='goods_code',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='货品编号'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='goods_specification',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='规格名称'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='has_invoice',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='需要发票'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='invoice_content',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='发票内容'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='invoice_no',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='物流单号'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='invoice_rise',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='发票抬头'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='logistics_company',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='物流公司'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='order_area',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='区域'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='order_source',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='订单来源'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='order_time',
            field=models.DateTimeField(verbose_name='交易时间'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='order_type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='订单类型'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='payment',
            field=models.DecimalField(decimal_places=2, default=3, max_digits=10, verbose_name='订单支付金额'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='platform_goods_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='平台货品名称'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='platform_goods_specification',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='平台规格名称'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='print_remark',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='打印备注'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='quantity',
            field=models.IntegerField(blank=True, null=True, verbose_name='下单数量'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='receiver_area',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='收货地区'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='receiver_telephone',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='收件人电话'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='refund_status',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='订单退款状态'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='salesman',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='业务员'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='seller_remark',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='客服备注'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='status',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='订单状态'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='sub_original_order_id',
            field=models.CharField(blank=True, db_index=True, max_length=30, null=True, verbose_name='子单原始单号'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='warehouse',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='仓库'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='zip_code',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='邮编'),
        ),
    ]
