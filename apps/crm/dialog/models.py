# -*- coding:  utf-8 -*-
# @Time    :  2020/04/24 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel


class DialogTag(BaseModel):
    ORDER_STATUS = (
        (0, '被取消'),
        (1, '正常'),
    )

    CATEGORY = (
        (0, '无法定义'),
        (1, '售前'),
        (2, '售后'),
    )
    name = models.CharField(max_length=30, verbose_name='标签名')
    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='标签类型')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')

    class Meta:
        verbose_name = 'CRM-对话-标签'
        verbose_name_plural = verbose_name
        db_table = 'crm_dialog_tag'

    def __str__(self):
        return self.name


class OriDialogTB(BaseModel):
    shop = models.CharField(max_length=60, verbose_name='店铺')
    servicer = models.CharField(max_length=150, verbose_name='客服')
    customer = models.CharField(max_length=150, verbose_name='客户')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    min = models.IntegerField(verbose_name='时长（秒）')
    dialog_tag = models.ForeignKey(DialogTag, on_delete=models.CASCADE, null=True, blank=True, verbose_name='对话标签')

    class Meta:
        verbose_name = 'CRM-淘系对话-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_dialog_oritaobao'

    def __str__(self):
        return '%s+%s' % (str(self.start_time)[:10], self.customer)


class OriDetailTB(BaseModel):

    dialog_tb = models.ForeignKey(OriDialogTB, on_delete=models.CASCADE, verbose_name='对话')
    sayer = models.CharField(max_length=150, verbose_name='讲话者')
    time = models.DateTimeField(verbose_name='时间')
    content = models.TextField(verbose_name='内容')

    class Meta:
        verbose_name = 'CRM-淘系对话-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_diadetail_oritaobao'

    def __str__(self):
        return self.sayer