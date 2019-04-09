# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-08 21:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_auto_20190110_1253'),
    ]

    operations = [
        migrations.CreateModel(
            name='OriOrderInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('erp_order_id', models.CharField(blank=True, max_length=30, null=True, verbose_name='订单编号')),
                ('shop', models.CharField(max_length=30, verbose_name='店铺')),
                ('order_source', models.CharField(blank=True, max_length=30, null=True, verbose_name='订单来源')),
                ('warehouse', models.CharField(blank=True, max_length=30, null=True, verbose_name='仓库')),
                ('sub_original_order_id', models.CharField(blank=True, db_index=True, max_length=30, null=True, verbose_name='子单原始单号')),
                ('status', models.CharField(blank=True, max_length=30, null=True, verbose_name='订单状态')),
                ('order_type', models.CharField(blank=True, max_length=30, null=True, verbose_name='订单类型')),
                ('cash_on_delivery', models.CharField(blank=True, max_length=30, null=True, verbose_name='货到付款')),
                ('refund_status', models.CharField(blank=True, max_length=30, null=True, verbose_name='订单退款状态')),
                ('order_time', models.DateTimeField(verbose_name='交易时间')),
                ('pay_time', models.DateTimeField(blank=True, null=True, verbose_name='付款时间')),
                ('buyer_nick', models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='客户网名')),
                ('receiver_name', models.CharField(max_length=100, verbose_name='收件人')),
                ('receiver_area', models.CharField(blank=True, max_length=30, null=True, verbose_name='收货地区')),
                ('receiver_address', models.CharField(max_length=200, verbose_name='收货地址')),
                ('receiver_mobile', models.CharField(blank=True, db_index=True, max_length=30, null=True, verbose_name='收件人手机')),
                ('distributor', models.CharField(blank=True, max_length=30, null=True, verbose_name='分销商')),
                ('discreteness_source_id', models.CharField(blank=True, max_length=30, null=True, verbose_name='来源组合装编号')),
                ('receiver_telephone', models.CharField(blank=True, max_length=30, null=True, verbose_name='收件人电话')),
                ('zip_code', models.CharField(blank=True, max_length=30, null=True, verbose_name='邮编')),
                ('order_area', models.CharField(blank=True, max_length=30, null=True, verbose_name='区域')),
                ('logistics_company', models.CharField(blank=True, max_length=30, null=True, verbose_name='物流公司')),
                ('logistics_no', models.CharField(blank=True, max_length=30, null=True, verbose_name='物流单号')),
                ('buyer_message', models.CharField(blank=True, max_length=800, null=True, verbose_name='买家留言')),
                ('seller_remark', models.CharField(blank=True, max_length=800, null=True, verbose_name='客服备注')),
                ('print_remark', models.CharField(blank=True, max_length=500, null=True, verbose_name='打印备注')),
                ('payment', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='订单支付金额')),
                ('post_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='邮费')),
                ('discount_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='订单总优惠')),
                ('total_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='应收金额')),
                ('payment_and_delivery_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='款到发货金额')),
                ('cod_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='货到付款金额')),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='预估重量')),
                ('has_invoice', models.CharField(blank=True, max_length=30, null=True, verbose_name='需要发票')),
                ('invoice_rise', models.CharField(blank=True, max_length=100, null=True, verbose_name='发票抬头')),
                ('invoice_content', models.CharField(blank=True, max_length=100, null=True, verbose_name='发票内容')),
                ('salesman', models.CharField(blank=True, max_length=30, null=True, verbose_name='业务员')),
                ('auditor', models.CharField(blank=True, max_length=30, null=True, verbose_name='审核人')),
                ('goods_id', models.CharField(max_length=30, verbose_name='商家编码')),
                ('goods_code', models.CharField(blank=True, max_length=30, null=True, verbose_name='货品编号')),
                ('goods_name', models.CharField(max_length=150, verbose_name='货品名称')),
                ('goods_specification', models.CharField(blank=True, max_length=30, null=True, verbose_name='规格名称')),
                ('platform_goods_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='平台货品名称')),
                ('platform_goods_specification', models.CharField(blank=True, max_length=150, null=True, verbose_name='平台规格名称')),
                ('quantity', models.IntegerField(blank=True, null=True, verbose_name='下单数量')),
                ('fixed', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='标价')),
                ('goods_discount_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='货品总优惠')),
                ('goods_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='成交价')),
                ('allocated_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='分摊后价格')),
                ('discount_ratio', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='打折比')),
                ('real_quantity', models.IntegerField(verbose_name='实发数量')),
                ('allocated_total_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='分摊后总价')),
                ('before_refund_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='退款前支付金额')),
                ('allocated_post_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='分摊邮费')),
                ('goods_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='单品支付金额')),
                ('discreteness_id', models.CharField(blank=True, max_length=30, null=True, verbose_name='拆自组合装')),
                ('gift_type', models.CharField(blank=True, max_length=30, null=True, verbose_name='赠品方式')),
                ('tocustomer_status', models.CharField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, max_length=30, verbose_name='生成客户信息状态')),
                ('totendency_ht_status', models.CharField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, max_length=30, verbose_name='生成习惯时间状态')),
                ('totendency_ha_status', models.CharField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, max_length=30, verbose_name='生成习惯区域状态')),
                ('totendency_ac_status', models.CharField(choices=[(0, '未审核'), (1, '已处理'), (2, '无效'), (3, '异常')], default=0, max_length=30, verbose_name='生成消费能力状态')),
                ('platform', models.CharField(default='其他', max_length=30, verbose_name='平台')),
                ('exception_tag', models.BooleanField(default=0, verbose_name='手机异常标记')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
                'db_table': 'oriorderinfo',
            },
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='allocated_post_fee',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='auditor',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='before_refund_payment',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='discount_fee',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='discount_ratio',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='fixed',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='goods_code',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='goods_discount_fee',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='goods_specification',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='platform_goods_name',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='platform_goods_specification',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='refund_status',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='salesman',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='total_fee',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='totendency_ac_status',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='totendency_ha_status',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='totendency_ht_status',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='weight',
        ),
        migrations.RemoveField(
            model_name='orderinfo',
            name='zip_code',
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='receiver_mobile',
            field=models.CharField(blank=True, db_index=True, max_length=30, null=True, verbose_name='收件人手机'),
        ),
        migrations.AlterModelTable(
            name='orderinfo',
            table='orderinfo',
        ),
    ]