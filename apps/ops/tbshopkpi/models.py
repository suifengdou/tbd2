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


class OriTMShopKPI(BaseModel):
    TEMPLATE_DIC = {
        "统计日期": "statistical_time",
        "PC端访客数": "pc_unique_visitor",
        "PC端浏览量": "pc_page_views",
        "访客数": "unique_visitor",
        "无线端访客数": "mobile_unique_visitor",
        "浏览量": "page_views",
        "无线端浏览量": "mobile_page_views",
        "商品访客数": "product_unique_visitor",
        "无线端商品访客数": "mobile_product_unique_visitor",
        "PC端商品访客数": "pc_product_unique_visitor",
        "商品浏览量": "product_page_views",
        "无线端商品浏览量": "mobile_product_page_views",
        "PC端商品浏览量": "pc_product_page_views",
        "平均停留时长": "avg_stay_time",
        "无线端平均停留时长": "mobile_avg_stay_time",
        "PC端平均停留时长": "pc_avg_stay_time",
        "跳失率": "bounce_rate",
        "无线端跳失率": "mobile_bounce_rate",
        "PC端跳失率": "pc_bounce_rate",
        "商品收藏买家数": "product_favorite_buyers",
        "无线端商品收藏买家数": "mobile_product_favorite_buyers",
        "PC端商品收藏买家数": "pc_product_favorite_buyers",
        "商品收藏次数": "favorite_number",
        "无线端商品收藏次数": "mobile_favorite_number",
        "PC端商品收藏次数": "pc_favorite_number",
        "加购人数": "shopping_buyers",
        "无线端加购人数": "mobile_shopping_buyers",
        "PC端加购人数": "pc_shopping_buyers",
        "支付金额": "payment_amount",
        "PC端支付金额": "pc_payment_amount",
        "无线端支付金额": "mobile_payment_amount",
        "支付买家数": "payment_buyers",
        "PC端支付买家数": "pc_payment_buyers",
        "无线端支付买家数": "mobile_payment_buyers",
        "支付子订单数": "payment_suborder",
        "PC端支付子订单数": "pc_payment_suborder",
        "无线端支付子订单数": "mobile_payment_suborder",
        "支付件数": "payment_quantity",
        "PC端支付件数": "pc_payment_quantity",
        "无线端支付件数": "mobile_payment_quantity",
        "下单金额": "order_amount",
        "PC端下单金额": "pc_order_amount",
        "无线端下单金额": "mobile_order_amount",
        "下单买家数": "order_buyers",
        "PC端下单买家数": "pc_order_buyers",
        "无线端下单买家数": "mobile_order_buyers",
        "下单件数": "order_quantity",
        "PC端下单件数": "pc_order_quantity",
        "无线端下单件数": "mobile_order_quantity",
        "人均浏览量": "avg_page_views",
        "PC端人均浏览量": "pc_avg_page_views",
        "无线端人均浏览量": "mobile_avg_page_views",
        "下单转化率": "order_conversion_rate",
        "PC端下单转化率": "pc_order_conversion_rate",
        "无线端下单转化率": "mobile_order_conversion_rate",
        "支付转化率": "payment_conversion_rate",
        "PC端支付转化率": "pc_payment_conversion_rate",
        "无线端支付转化率": "mobile_payment_conversion_rate",
        "客单价": "per_customer_transaction",
        "PC端客单价": "pc_per_customer_transaction",
        "无线端客单价": "mobile_per_customer_transaction",
        "UV价值": "uv_value",
        "PC端UV价值": "pc_uv_value",
        "无线端UV价值": "mobile_uv_value",
        "老访客数": "repeat_visitor",
        "新访客数": "new_visitor",
        "无线端老访客数": "mobile_repeat_visitor",
        "无线端新访客数": "mobile_new_visitor",
        "PC端老访客数": "pc_repeat_visitor",
        "PC端新访客数": "pc_new_visitor",
        "加购件数": "shopping_goods",
        "PC端加购件数": "pc_shopping_goods",
        "无线端加购件数": "mobile_shopping_goods",
        "支付老买家数": "payment_repeat_visitor",
        "PC端支付老买家数": "pc_payment_repeat_visitor",
        "无线端支付老买家数": "mobile_payment_repeat_visitor",
        "老买家支付金额": "amount_repeat_visitor",
        "直通车消耗": "fee_through_train",
        "钻石展位消耗": "cost_per_mille",
        "淘宝客佣金": "commission_promoter",
        "成功退款金额": "refund_amount",
        "评价数": "comment",
        "有图评价数": "has_photograph_comment",
        "正面评价数": "positive_comment",
        "负面评价数": "negative_comment",
        "老买家正面评价数": "repeat_visitor_positive_comment",
        "老买家负面评价数": "repeat_visitor_negative_comment",
        "支付父订单数": "payment_parents_order",
        "揽收包裹数": "packages_collect",
        "发货包裹数": "packages_delivering",
        "派送包裹数": "packages_delivered",
        "签收成功包裹数": "packages_sign",
        "平均支付_签收时长(秒)": "avg_trading_time",
        "描述相符评分": "description_points",
        "物流服务评分": "delivery_points",
        "服务态度评分": "service_points",
        "下单-支付转化率": "order_payment_conversion_rate",
        "PC端下单-支付转化率": "pc_order_payment_conversion_rate",
        "无线端下单-支付转化率": "mobile_order_payment_conversion_rate",
        "支付商品数": "goods_paid",
        "PC端支付商品数": "pc_goods_paid",
        "无线端支付商品数": "mobile_goods_paid",
        "店铺收藏买家数": "shop_favorite_buyers",
        "PC端店铺收藏买家数": "pc_shop_favorite_buyers",
        "无线端店铺收藏买家数": "mobile_shop_favorite_buyers",
    }

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    statistical_time = models.DateTimeField(verbose_name='统计日期')
    pc_unique_visitor = models.IntegerField(verbose_name='PC访客数')
    pc_page_views = models.IntegerField(verbose_name='PC端浏览量')
    unique_visitor = models.IntegerField(verbose_name='访客数')
    mobile_unique_visitor = models.IntegerField(verbose_name='无线端访客数')
    page_views = models.IntegerField(verbose_name='浏览量')
    mobile_page_views = models.IntegerField(verbose_name='无线端浏览量')
    product_unique_visitor = models.IntegerField(verbose_name='商品访客数')
    mobile_product_unique_visitor = models.IntegerField(verbose_name='无线端商品访客数')
    pc_product_unique_visitor = models.IntegerField(verbose_name='PC端商品访客数')
    product_page_views = models.IntegerField(verbose_name='商品浏览量')
    mobile_product_page_views = models.IntegerField(verbose_name='无线端商品浏览量')
    pc_product_page_views = models.IntegerField(verbose_name='PC端商品浏览量')
    avg_stay_time = models.FloatField(verbose_name='平均停留时长')
    mobile_avg_stay_time = models.FloatField(verbose_name='无线端平均停留时长')
    pc_avg_stay_time = models.FloatField(verbose_name='PC端平均停留时长')
    bounce_rate = models.FloatField(verbose_name='跳失率')
    mobile_bounce_rate = models.FloatField(verbose_name='无线端跳失率')
    pc_bounce_rate = models.FloatField(verbose_name='PC端跳失率')
    product_favorite_buyers = models.IntegerField(verbose_name='商品收藏买家数')
    mobile_product_favorite_buyers = models.IntegerField(verbose_name='无线端商品收藏买家数')
    pc_product_favorite_buyers = models.IntegerField(verbose_name='PC端商品收藏买家数')
    favorite_number = models.IntegerField(verbose_name='商品收藏次数')
    mobile_favorite_number = models.IntegerField(verbose_name='无线端商品收藏次数')
    pc_favorite_number = models.IntegerField(verbose_name='PC端商品收藏次数')
    shopping_buyers = models.IntegerField(verbose_name='加购人数')
    mobile_shopping_buyers = models.IntegerField(verbose_name='无线端加购人数')
    pc_shopping_buyers = models.IntegerField(verbose_name='PC端加购人数')
    payment_amount = models.FloatField(verbose_name='支付金额')
    pc_payment_amount = models.FloatField(verbose_name='PC端支付金额')
    mobile_payment_amount = models.FloatField(verbose_name='无线端支付金额')
    payment_buyers = models.IntegerField(verbose_name='支付买家数')
    pc_payment_buyers = models.IntegerField(verbose_name='PC端支付买家数')
    mobile_payment_buyers = models.IntegerField(verbose_name='无线端支付买家数')
    payment_suborder = models.IntegerField(verbose_name='支付子订单数')
    pc_payment_suborder = models.IntegerField(verbose_name='PC端支付子订单数')
    mobile_payment_suborder = models.IntegerField(verbose_name='无线端支付子订单数')
    payment_quantity = models.IntegerField(verbose_name='支付件数')
    pc_payment_quantity = models.IntegerField(verbose_name='PC端支付件数')
    mobile_payment_quantity = models.IntegerField(verbose_name='无线端支付件数')
    order_amount = models.FloatField(verbose_name='下单金额')
    pc_order_amount = models.FloatField(verbose_name='PC端下单金额')
    mobile_order_amount = models.FloatField(verbose_name='无线端下单金额')
    order_buyers = models.IntegerField(verbose_name='下单买家数')
    pc_order_buyers = models.IntegerField(verbose_name='PC端下单买家数')
    mobile_order_buyers = models.IntegerField(verbose_name='无线端下单买家数')
    order_quantity = models.IntegerField(verbose_name='下单件数')
    pc_order_quantity = models.IntegerField(verbose_name='PC端下单件数')
    mobile_order_quantity = models.IntegerField(verbose_name='无线端下单件数')
    avg_page_views = models.FloatField(verbose_name='人均浏览量')
    pc_avg_page_views = models.FloatField(verbose_name='PC端人均浏览量')
    mobile_avg_page_views = models.FloatField(verbose_name='无线端人均浏览量')
    order_conversion_rate = models.FloatField(verbose_name='下单转化率')
    pc_order_conversion_rate = models.FloatField(verbose_name='PC端下单转化率')
    mobile_order_conversion_rate = models.FloatField(verbose_name='无线端下单转化率')
    payment_conversion_rate = models.FloatField(verbose_name='支付转化率')
    pc_payment_conversion_rate = models.FloatField(verbose_name='PC端支付转化率')
    mobile_payment_conversion_rate = models.FloatField(verbose_name='无线端支付转化率')
    per_customer_transaction = models.FloatField(verbose_name='客单价')
    pc_per_customer_transaction = models.FloatField(verbose_name='PC端客单价')
    mobile_per_customer_transaction = models.FloatField(verbose_name='无线端客单价')
    uv_value = models.FloatField(verbose_name='UV价值')
    pc_uv_value = models.FloatField(verbose_name='PC端UV价值')
    mobile_uv_value = models.FloatField(verbose_name='无线端UV价值')
    repeat_visitor = models.IntegerField(verbose_name='老访客数')
    new_visitor = models.IntegerField(verbose_name='新访客数')
    mobile_repeat_visitor = models.IntegerField(verbose_name='无线端老访客数')
    mobile_new_visitor = models.IntegerField(verbose_name='无线端新访客数')
    pc_repeat_visitor = models.IntegerField(verbose_name='PC端老访客数')
    pc_new_visitor = models.IntegerField(verbose_name='PC端新访客数')
    shopping_goods = models.IntegerField(verbose_name='加购件数')
    pc_shopping_goods = models.IntegerField(verbose_name='PC端加购件数')
    mobile_shopping_goods = models.IntegerField(verbose_name='无线端加购件数')
    payment_repeat_visitor = models.IntegerField(verbose_name='支付老买家数')
    pc_payment_repeat_visitor = models.IntegerField(verbose_name='PC端支付老买家数')
    mobile_payment_repeat_visitor = models.IntegerField(verbose_name='无线端支付老买家数')
    amount_repeat_visitor = models.FloatField(verbose_name='老买家支付金额')
    fee_through_train = models.FloatField(verbose_name='直通车消耗')
    cost_per_thousand = models.FloatField(verbose_name='钻石展位消耗')
    commission_promoter = models.FloatField(verbose_name='淘宝客佣金')
    refund_amount = models.FloatField(verbose_name='成功退款金额')
    comment = models.IntegerField(verbose_name='评价数')
    has_photograph_comment = models.IntegerField(verbose_name='有图评价数')
    positive_comment = models.IntegerField(verbose_name='正面评价数')
    negative_comment = models.IntegerField(verbose_name='负面评价数')
    repeat_visitor_positive_comment = models.IntegerField(verbose_name='老买家正面评价数')
    repeat_visitor_negative_comment = models.IntegerField(verbose_name='老买家负面评价数')
    payment_parents_order = models.IntegerField(verbose_name='支付父订单数')
    packages_collect = models.IntegerField(verbose_name='揽收包裹数')
    packages_delivering = models.IntegerField(verbose_name='发货包裹数')
    packages_delivered = models.IntegerField(verbose_name='派送包裹数')
    packages_sign = models.IntegerField(verbose_name='签收成功包裹数')
    avg_trading_time = models.FloatField(verbose_name='平均支付_签收时长(秒)')
    description_points = models.FloatField(verbose_name='描述相符评分')
    delivery_points = models.FloatField(verbose_name='物流服务评分')
    service_points = models.FloatField(verbose_name='服务态度评分')
    order_payment_conversion_rate = models.FloatField(verbose_name='下单-支付转化率')
    pc_order_payment_conversion_rate = models.FloatField(verbose_name='PC端下单-支付转化率')
    mobile_order_payment_conversion_rate = models.FloatField(verbose_name='无线端下单-支付转化率')
    goods_paid = models.IntegerField(verbose_name='支付商品数')
    pc_goods_paid = models.IntegerField(verbose_name='PC端支付商品数')
    mobile_goods_paid = models.IntegerField(verbose_name='无线端支付商品数')
    shop_favorite_buyers = models.IntegerField(verbose_name='店铺收藏买家数')
    pc_shop_favorite_buyers = models.IntegerField(verbose_name='PC端店铺收藏买家数')
    mobile_shop_favorite_buyers = models.IntegerField(verbose_name='无线端店铺收藏买家数')
    shop = models.ForeignKey(ShopInfo, on_delete=models.SET_NULL, verbose_name='店铺', null=True, blank=True)
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')

    class Meta:
        verbose_name = '天猫店铺维度原始运营指标表'
        verbose_name_plural = verbose_name
        db_table = 'ops_tbshoporikip'

    def __str__(self):
        return self.statistical_time

