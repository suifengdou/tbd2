# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-09-28 15:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OriTMGoodsKPI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('statistical_time', models.DateTimeField(verbose_name='统计日期')),
                ('goods_id', models.CharField(max_length=30, verbose_name='商品ID')),
                ('goods_name', models.CharField(max_length=200, verbose_name='商品名称')),
                ('pc_exposure', models.IntegerField(verbose_name='PC端曝光量')),
                ('unique_visitor', models.IntegerField(verbose_name='访客数')),
                ('mobile_unique_visitor', models.IntegerField(verbose_name='无线端访客数')),
                ('pc_click_number', models.IntegerField(verbose_name='PC端点击次数')),
                ('detail_page_bounce_rate', models.FloatField(verbose_name='详情页跳出率')),
                ('pc_detail_page_bounce_rate', models.FloatField(verbose_name='PC端详情页跳出率')),
                ('mobile_detail_page_bounce_rate', models.FloatField(verbose_name='无线端详情页跳出率')),
                ('avg_stay_time', models.FloatField(verbose_name='平均停留时长')),
                ('mobile_avg_stay_time', models.FloatField(verbose_name='无线端平均停留时长')),
                ('pc_avg_stay_time', models.FloatField(verbose_name='PC端平均停留时长')),
                ('payment_amount', models.FloatField(verbose_name='支付金额')),
                ('pc_unique_visitor', models.IntegerField(verbose_name='PC端访客数')),
                ('shopping_goods', models.IntegerField(verbose_name='加购件数')),
                ('pc_shopping_goods', models.IntegerField(verbose_name='PC端加购件数')),
                ('mobile_shopping_goods', models.IntegerField(verbose_name='无线端加购件数')),
                ('product_favorite_buyers', models.IntegerField(verbose_name='商品收藏买家数')),
                ('pc_product_favorite_buyers', models.IntegerField(verbose_name='PC端商品收藏买家数')),
                ('mobile_product_favorite_buyers', models.IntegerField(verbose_name='无线端商品收藏买家数')),
                ('pc_payment_amount', models.FloatField(verbose_name='PC端支付金额')),
                ('mobile_payment_amount', models.FloatField(verbose_name='无线端支付金额')),
                ('payment_quantity', models.IntegerField(verbose_name='支付件数')),
                ('pc_payment_quantity', models.IntegerField(verbose_name='PC端支付件数')),
                ('mobile_payment_quantity', models.IntegerField(verbose_name='无线端支付件数')),
                ('payment_buyers', models.IntegerField(verbose_name='支付买家数')),
                ('pc_payment_buyers', models.IntegerField(verbose_name='PC端支付买家数')),
                ('mobile_payment_buyers', models.IntegerField(verbose_name='无线端支付买家数')),
                ('per_customer_transaction', models.FloatField(verbose_name='客单价')),
                ('pc_per_customer_transaction', models.FloatField(verbose_name='PC端客单价')),
                ('mobile_per_customer_transaction', models.FloatField(verbose_name='无线端客单价')),
                ('payment_conversion_rate', models.FloatField(verbose_name='支付转化率')),
                ('pc_payment_conversion_rate', models.FloatField(verbose_name='PC端支付转化率')),
                ('mobile_payment_conversion_rate', models.FloatField(verbose_name='无线端支付转化率')),
                ('goods_views', models.IntegerField(verbose_name='商品浏览量')),
                ('mobile_goods_views', models.IntegerField(verbose_name='无线端商品浏览量')),
                ('pc_goods_views', models.IntegerField(verbose_name='PC端商品浏览量')),
                ('refund_amount', models.FloatField(verbose_name='成功退款退货金额')),
                ('order_buyers', models.IntegerField(verbose_name='下单买家数')),
                ('order_quantity', models.IntegerField(verbose_name='下单件数')),
                ('order_amount', models.FloatField(verbose_name='下单金额')),
                ('status', models.IntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], default=1, verbose_name='单据状态')),
                ('shop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.ShopInfo', verbose_name='店铺')),
            ],
            options={
                'verbose_name': '天猫货品维度原始运营指标表',
                'verbose_name_plural': '天猫货品维度原始运营指标表',
                'db_table': 'ops_tbgoodsorikip',
            },
        ),
    ]
