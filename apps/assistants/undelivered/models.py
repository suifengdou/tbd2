# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 20:58
# @Author  : Hann
# @Site    :
# @File    : models.py
# @Software: PyCharm


from django.db import models

from db.base_model import BaseModel


class OriorderInfo(BaseModel):
    VERIFY_FIELD = ['order_id', 'nickname', 'payment_amount', 'payment_time', 'goods_title', 'memorandum']
    ORDER_STATUS = (
        (0, '订单取消'),
        (1, '等待处理'),
        (2, '处理完成'),
        (3, '特殊订单'),
    )

    ORDER_TAG = (
        (0, '未标记'),
        (1, '订金订单'),
        (2, '时效外'),
        (3, '时效内'),
        (4, '暂不发货'),
        (5, '有退款'),
    )

    order_id = models.CharField(max_length=30, verbose_name='订单编号')
    nickname = models.CharField(max_length=60, verbose_name='买家会员名')
    payment_amount = models.FloatField(verbose_name='买家实际支付金额')
    buyer_message = models.TextField(verbose_name='买家留言')
    order_create_time = models.DateTimeField(verbose_name='订单创建时间')
    payment_time = models.DateTimeField(verbose_name='订单付款时间')
    goods_title = models.CharField(max_length=150, verbose_name='宝贝标题')
    memorandum = models.TextField(verbose_name='订单备注')
    goods_quantity = models.IntegerField(verbose_name='宝贝总数量')
    shop_name = models.CharField(max_length=30, verbose_name='店铺名称')

    order_status = models.IntegerField(choices=ORDER_STATUS, default=0, verbose_name='单据处理状态')
    status_tag = models.SmallIntegerField(choices=ORDER_TAG, default=0, verbose_name='订单标记')


    class Meta:
        verbose_name = "ASS-后台-订单查询表"
        verbose_name_plural = verbose_name
        db_table = 'ass_und_undelivered'

    def __str__(self):
        return self.order_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class PendingOrderInfo(OriorderInfo):
    class Meta:
        verbose_name = 'ASS-后台-待处理订单'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.goods_title


class RefundOrderInfo(OriorderInfo):
    class Meta:
        verbose_name = 'ASS-后台-特殊订单'
        verbose_name_plural = verbose_name
        proxy = True



