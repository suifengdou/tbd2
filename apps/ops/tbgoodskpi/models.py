# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone
import pandas as pd

from db.base_model import BaseModel
from apps.base.shop.models import ShopInfo


class OriTMGoodsKPI(BaseModel):
    TEMPLATE_DIC = {
        "统计日期": "statistical_time",
        "商品ID": "goods_id",
        "商品名称": "goods_name",
        "PC端曝光量": "pc_exposure",
        "访客数": "unique_visitor",
        "无线端访客数": "mobile_unique_visitor",
        "PC端点击次数": "pc_click_number",
        "详情页跳出率": "detail_page_bounce_rate",
        "PC端详情页跳出率": "pc_detail_page_bounce_rate",
        "无线端详情页跳出率": "mobile_detail_page_bounce_rate",
        "平均停留时长": "avg_stay_time",
        "无线端平均停留时长": "mobile_avg_stay_time",
        "PC端平均停留时长": "pc_avg_stay_time",
        "支付金额": "payment_amount",
        "PC端访客数": "pc_unique_visitor",
        "加购件数": "shopping_goods",
        "PC端加购件数": "pc_shopping_goods",
        "无线端加购件数": "mobile_shopping_goods",
        "商品收藏买家数": "product_favorite_buyers",
        "PC端商品收藏买家数": "pc_product_favorite_buyers",
        "无线端商品收藏买家数": "mobile_product_favorite_buyers",
        "PC端支付金额": "pc_payment_amount",
        "无线端支付金额": "mobile_payment_amount",
        "支付件数": "payment_quantity",
        "PC端支付件数": "pc_payment_quantity",
        "无线端支付件数": "mobile_payment_quantity",
        "支付买家数": "payment_buyers",
        "PC端支付买家数": "pc_payment_buyers",
        "无线端支付买家数": "mobile_payment_buyers",
        "客单价": "per_customer_transaction",
        "PC端客单价": "pc_per_customer_transaction",
        "无线端客单价": "mobile_per_customer_transaction",
        "支付转化率": "payment_conversion_rate",
        "PC端支付转化率": "pc_payment_conversion_rate",
        "无线端支付转化率": "mobile_payment_conversion_rate",
        "商品浏览量": "goods_views",
        "无线端商品浏览量": "mobile_goods_views",
        "PC端商品浏览量": "pc_goods_views",
        "成功退款退货金额": "refund_amount",
        "下单买家数": "order_buyers",
        "下单件数": "order_quantity",
        "下单金额": "order_amount",
        "店铺": "shopping_goods",
        "单据状态": "status"
    }
    VERIFY_FIELD = ['statistical_time', 'goods_id', 'goods_name', 'pc_exposure', 'unique_visitor',
                    'mobile_unique_visitor', 'pc_click_number', 'detail_page_bounce_rate', 'pc_detail_page_bounce_rate',
                    'mobile_detail_page_bounce_rate', 'avg_stay_time', 'mobile_avg_stay_time', 'pc_avg_stay_time',
                    'payment_amount', 'pc_unique_visitor', 'shopping_goods', 'pc_shopping_goods',
                    'mobile_shopping_goods', 'product_favorite_buyers', 'pc_product_favorite_buyers',
                    'mobile_product_favorite_buyers', 'pc_payment_amount', 'mobile_payment_amount', 'payment_quantity',
                    'pc_payment_quantity', 'mobile_payment_quantity', 'payment_buyers', 'pc_payment_buyers',
                    'mobile_payment_buyers', 'per_customer_transaction', 'pc_per_customer_transaction',
                    'mobile_per_customer_transaction', 'payment_conversion_rate', 'pc_payment_conversion_rate',
                    'mobile_payment_conversion_rate', 'goods_views', 'mobile_goods_views', 'pc_goods_views',
                    'refund_amount', 'order_buyers', 'order_quantity', 'order_amount']

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    statistical_time = models.DateTimeField(verbose_name='统计日期')
    goods_id = models.CharField(max_length=30, verbose_name='商品ID')
    goods_name = models.CharField(max_length=200, verbose_name='商品名称')
    pc_exposure = models.IntegerField(verbose_name='PC端曝光量')
    unique_visitor = models.IntegerField(verbose_name='访客数')
    mobile_unique_visitor = models.IntegerField(verbose_name='无线端访客数')
    pc_click_number = models.IntegerField(verbose_name='PC端点击次数')
    detail_page_bounce_rate = models.FloatField(verbose_name='详情页跳出率')
    pc_detail_page_bounce_rate = models.FloatField(verbose_name='PC端详情页跳出率')
    mobile_detail_page_bounce_rate = models.FloatField(verbose_name='无线端详情页跳出率')
    avg_stay_time = models.FloatField(verbose_name='平均停留时长')
    mobile_avg_stay_time = models.FloatField(verbose_name='无线端平均停留时长')
    pc_avg_stay_time = models.FloatField(verbose_name='PC端平均停留时长')
    payment_amount = models.FloatField(verbose_name='支付金额')
    pc_unique_visitor = models.IntegerField(verbose_name='PC端访客数')
    shopping_goods = models.IntegerField(verbose_name='加购件数')
    pc_shopping_goods = models.IntegerField(verbose_name='PC端加购件数')
    mobile_shopping_goods = models.IntegerField(verbose_name='无线端加购件数')
    product_favorite_buyers = models.IntegerField(verbose_name='商品收藏买家数')
    pc_product_favorite_buyers = models.IntegerField(verbose_name='PC端商品收藏买家数')
    mobile_product_favorite_buyers = models.IntegerField(verbose_name='无线端商品收藏买家数')
    pc_payment_amount = models.FloatField(verbose_name='PC端支付金额')
    mobile_payment_amount = models.FloatField(verbose_name='无线端支付金额')
    payment_quantity = models.IntegerField(verbose_name='支付件数')
    pc_payment_quantity = models.IntegerField(verbose_name='PC端支付件数')
    mobile_payment_quantity = models.IntegerField(verbose_name='无线端支付件数')
    payment_buyers = models.IntegerField(verbose_name='支付买家数')
    pc_payment_buyers = models.IntegerField(verbose_name='PC端支付买家数')
    mobile_payment_buyers = models.IntegerField(verbose_name='无线端支付买家数')
    per_customer_transaction = models.FloatField(verbose_name='客单价')
    pc_per_customer_transaction = models.FloatField(verbose_name='PC端客单价')
    mobile_per_customer_transaction = models.FloatField(verbose_name='无线端客单价')
    payment_conversion_rate = models.FloatField(verbose_name='支付转化率')
    pc_payment_conversion_rate = models.FloatField(verbose_name='PC端支付转化率')
    mobile_payment_conversion_rate = models.FloatField(verbose_name='无线端支付转化率')
    goods_views = models.IntegerField(verbose_name='商品浏览量')
    mobile_goods_views = models.IntegerField(verbose_name='无线端商品浏览量')
    pc_goods_views = models.IntegerField(verbose_name='PC端商品浏览量')
    refund_amount = models.FloatField(verbose_name='成功退款退货金额')
    order_buyers = models.IntegerField(verbose_name='下单买家数')
    order_quantity = models.IntegerField(verbose_name='下单件数')
    order_amount = models.FloatField(verbose_name='下单金额')
    shop = models.ForeignKey(ShopInfo, on_delete=models.SET_NULL, verbose_name='店铺', null=True, blank=True)
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')

    class Meta:
        verbose_name = '天猫货品维度原始运营指标表'
        verbose_name_plural = verbose_name
        db_table = 'ops_tbgoodsorikip'

    def __str__(self):
        return self.statistical_time

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None





