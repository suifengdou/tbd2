# -*- coding:  utf-8 -*-
# @Time    :  2018/11/26 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel


class CustomerInfo(BaseModel):

    mobile = models.CharField(max_length=30, verbose_name='手机')
    satisficing = models.IntegerField(default=100, verbose_name='客户满意指数')
    category = models.CharField(null=True, blank=True, max_length=30, verbose_name='客户类别')
    name = models.CharField(max_length=100, verbose_name='姓名')
    gender = models.CharField(null=True, blank=True, max_length=30, verbose_name='性别')
    nationality = models.CharField(null=True, blank=True, max_length=30, verbose_name='国家')
    province = models.CharField(max_length=30, verbose_name='省份')
    city = models.CharField(max_length=30, verbose_name='城市')
    district = models.CharField(null=True, blank=True, max_length=30, verbose_name='区县')
    address = models.CharField(max_length=300, verbose_name='地址')
    e_mail = models.EmailField(null=True, blank=True, verbose_name='电子邮件')
    qq = models.CharField(null=True, blank=True, max_length=30, verbose_name='QQ')
    wangwang = models.CharField(null=True, blank=True, max_length=60, verbose_name='旺旺')
    jdfbp_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='京东FBP账号')
    jdzy_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='京东自营账号')
    gfsc_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='官方商城账号')
    wxxcx_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='微信小程序账号')
    alipay_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='支付宝账号')
    pdd_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='拼多多账号')
    birthday = models.DateTimeField(null=True, blank=True, verbose_name='生日')
    total_fee = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='购买总金额')
    total_times = models.IntegerField(default=0, verbose_name='购买总次数')
    last_time = models.DateTimeField(null=True, blank=True, verbose_name='上次购买时间')
    tag = models.CharField(null=True, blank=True, max_length=30, verbose_name='用户标签')
    gift_times = models.IntegerField(default=0, verbose_name='赠品次数')
    vip_type = models.CharField(null=True, blank=True, max_length=30, verbose_name='特殊类型')
    return_time = models.DateTimeField(null=True, blank=True, verbose_name='最后一次回访时间')
    contact_times = models.IntegerField(null=True, blank=True, default=0, verbose_name='回访关怀次数')
    wechat = models.CharField(null=True, blank=True, max_length=60, verbose_name='微信号')
    customers_service_times = models.IntegerField(default=0, verbose_name='售后次数')
    maintenance_times = models.IntegerField(default=0, verbose_name='中央维修次数')
    momery = models.CharField(null=True, blank=True, max_length=30, verbose_name='备注')
    order_failure_times = models.IntegerField(default=0, verbose_name='订单失败')
    custom_field2 = models.CharField(null=True, blank=True, max_length=30, verbose_name='未定义标签2')
    custom_field3 = models.CharField(null=True, blank=True, max_length=30, verbose_name='未定义标签3')
    custom_field4 = models.CharField(null=True, blank=True, max_length=30, verbose_name='未定义标签4')
    custom_field5 = models.CharField(null=True, blank=True, max_length=30, verbose_name='未定义标签5')

    class Meta:
        verbose_name = '客户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.mobile


class CustomerTendency(BaseModel):

    customer_id = models.IntegerField(default=0, verbose_name='客户编号')
    mobile = models.CharField(max_length=30, verbose_name='手机')
    habit_time = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='习惯趋向-时间')
    habit_area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='习惯趋向-区域')
    ability_consume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='消费能力趋向')

    class Meta:
        verbose_name = '客户积分卡'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.mobile