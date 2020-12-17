# -*- coding:  utf-8 -*-
# @Time    :  2018/11/26 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel
from apps.crm.orders.models import OrderInfo


class CustomerInfo(BaseModel):

    mobile = models.CharField(max_length=30, unique=True, db_index=True, verbose_name='手机')

    e_mail = models.EmailField(null=True, blank=True, verbose_name='电子邮件')
    qq = models.CharField(null=True, blank=True, max_length=30, verbose_name='QQ')
    wangwang = models.CharField(null=True, blank=True, max_length=60, verbose_name='旺旺')
    jdfbp_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='京东FBP账号')
    jdzy_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='京东自营账号')
    gfsc_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='官方商城账号')
    alipay_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='支付宝账号')
    pdd_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='拼多多账号')
    webchat = models.CharField(null=True, blank=True, max_length=60, verbose_name='微信号')
    others_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='其他平台')

    birthday = models.DateTimeField(null=True, blank=True, verbose_name='生日')
    total_amount = models.FloatField(default=0, verbose_name='购买总金额')
    total_times = models.IntegerField(default=0, verbose_name='购买总次数')
    last_time = models.DateTimeField(null=True, blank=True, verbose_name='最近购买时间')

    return_time = models.DateTimeField(null=True, blank=True, verbose_name='最后一次回访时间')
    contact_times = models.IntegerField(null=True, blank=True, default=0, verbose_name='回访关怀次数')

    free_service_times = models.IntegerField(default=0, verbose_name='无金额发货次数')
    maintenance_times = models.IntegerField(default=0, verbose_name='中央维修次数')
    memorandum = models.CharField(null=True, blank=True, max_length=30, verbose_name='备注')
    order_failure_times = models.IntegerField(default=0, verbose_name='退款次数')

    class Meta:
        verbose_name = 'CRM-C-客户信息'
        verbose_name_plural = verbose_name
        db_table = 'crm_c_customerinfo'

    def __str__(self):
        return str(self.mobile)


class OrderList(BaseModel):
    order = models.OneToOneField(OrderInfo, on_delete=models.CASCADE, verbose_name='订单')

    class Meta:
        verbose_name = 'CRM-C-订单列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_c_order_list'

    def __str__(self):
        return str(self.order.id)


class CountIdList(BaseModel):
    ori_order_trade_no = models.CharField(max_length=120, verbose_name='计数单号列表', db_index=True, unique=True)

    class Meta:
        verbose_name = 'CRM-C-计数单号列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_c_order_countlist'

    def __str__(self):
        return str(self.ori_order_trade_no)

