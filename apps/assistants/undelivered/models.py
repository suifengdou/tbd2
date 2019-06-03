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
    STATUS = (
        (0, '未处理'),
        (1, '订金'),
        (2, '异常'),
        (3, '先不发货'),
        (4, '延保'),
        (5, '未超时'),
        (6, '已完成')
    )
    order_id = models.CharField(max_length=30, verbose_name='订单编号')
    nickname = models.CharField(max_length=60, verbose_name='买家会员名')
    alipay_id = models.CharField(max_length=50, verbose_name='买家支付宝账号')
    alipay_order_id = models.CharField(max_length=50, verbose_name='支付单号')
    alipay_desc = models.CharField(max_length=200, verbose_name='支付详情')
    account_payable = models.IntegerField(verbose_name='买家应付货款')
    post_fee = models.IntegerField(verbose_name='买家应付邮费')
    point_payable = models.IntegerField(verbose_name='买家支付积分')
    total_amount = models.IntegerField(verbose_name='总金额')
    point = models.IntegerField(verbose_name='返点积分')
    payment_amount = models.IntegerField(verbose_name='买家实际支付金额')
    payment_point = models.IntegerField(verbose_name='买家实际支付积分')
    order_status = models.CharField(max_length=10, verbose_name='订单状态')
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
    shop_name = models.CharField(max_length=30, verbose_name='店铺名称')
    refund_amount = models.IntegerField(verbose_name='退款金额')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name='单据处理状态')
    created_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(class)s_createdby',
                                   verbose_name='操作人', null=True)

    class Meta:
        verbose_name = "未发货订单检查表"
        verbose_name_plural = verbose_name
        db_table = 'ass_und_undelivered'

    def __str__(self):
        return self.order_id


class ErrorOrderInfo(OriorderInfo):
    class Meta:
        verbose_name = '错误订单列表'
        verbose_name_plural = verbose_name
        proxy = True


class AppointmentOrderInfo(OriorderInfo):
    class Meta:
        verbose_name = '预约发货订单列表'
        verbose_name_plural = verbose_name
        proxy = True





