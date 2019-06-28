# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 20:58
# @Author  : Hann
# @Site    :
# @File    : models.py
# @Software: PyCharm


from django.db import models

from db.base_model import BaseModel
from tbd2.settings import AUTH_USER_MODEL


class OriorderInfo(BaseModel):
    VERIFY_FIELD = ['order_id', 'nickname', 'payment_amount', 'order_status', 'payment_time', 'goods_title', 'memorandum', 'refund_amount']
    STATUS = (
        (1, '无需处理'),
        (2, '特别跟进'),
        (3, '暂不处理'),
        (4, '半退未发'),
        (5, '未发订金'),
        (0, '等待处理'),
    )
    order_id = models.CharField(max_length=30, verbose_name='订单编号')
    nickname = models.CharField(max_length=60, verbose_name='买家会员名')
    alipay_id = models.CharField(max_length=50, verbose_name='买家支付宝账号')
    alipay_order_id = models.CharField(max_length=50, verbose_name='支付单号')
    alipay_desc = models.CharField(max_length=200, verbose_name='支付详情')
    account_payable = models.FloatField(verbose_name='买家应付货款')
    post_fee = models.FloatField(verbose_name='买家应付邮费')
    point_payable = models.IntegerField(verbose_name='买家支付积分')
    total_amount = models.FloatField(verbose_name='总金额')
    point = models.IntegerField(verbose_name='返点积分')
    payment_amount = models.FloatField(verbose_name='买家实际支付金额')
    payment_point = models.IntegerField(verbose_name='买家实际支付积分')
    order_status = models.CharField(max_length=70, verbose_name='订单状态')
    buyer_message = models.TextField(verbose_name='买家留言')
    receiver = models.CharField(max_length=60, verbose_name='收货人姓名')
    address = models.CharField(max_length=150, verbose_name='收货地址')
    delivery_type = models.CharField(max_length=20, verbose_name='运送方式')
    telephone = models.CharField(max_length=20, verbose_name='联系电话')
    mobile = models.CharField(max_length=30, verbose_name='联系手机')
    order_create_time = models.DateTimeField(verbose_name='订单创建时间')
    payment_time = models.DateTimeField(verbose_name='订单付款时间')
    goods_title = models.CharField(max_length=150, verbose_name='宝贝标题')
    goods_type = models.CharField(max_length=30, verbose_name='宝贝种类')
    memorandum = models.TextField(verbose_name='订单备注')
    goods_quantity = models.IntegerField(verbose_name='宝贝总数量')
    shop_id = models.CharField(max_length=30, verbose_name='店铺Id')
    cause_closed = models.CharField(max_length=100, verbose_name='订单关闭原因')
    shop_name = models.CharField(max_length=30, verbose_name='店铺名称')
    refund_amount = models.FloatField(verbose_name='退款金额')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name='单据处理状态')


    class Meta:
        verbose_name = "订单查询表"
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
        verbose_name = '待处理订单'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.goods_title


class SpecialOrderInfo(OriorderInfo):
    class Meta:
        verbose_name = '特别跟进等订单'
        verbose_name_plural = verbose_name
        proxy = True


class RefundOrderInfo(OriorderInfo):
    class Meta:
        verbose_name = '部分退款订单'
        verbose_name_plural = verbose_name
        proxy = True


