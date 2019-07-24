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


class WWFilterationInfo(BaseModel):
    VERIFY_FIELD = ['dialogue_time','buyer_ww','start_time','end_time','cs_ww','filter_category']
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    dialogue_time = models.DateTimeField(verbose_name='聊天时间')
    buyer_ww = models.CharField(max_length=60, verbose_name='买家旺旺')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    cs_ww = models.CharField(max_length=60, verbose_name='客服旺旺')
    filter_category = models.CharField(max_length=30, verbose_name='过滤类型')
    shop = models.ForeignKey(ShopInfo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='店铺')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='系统状态')

    class Meta:
        verbose_name = '旺旺接待过滤'
        verbose_name_plural = verbose_name
        db_table = 'ops_ww_filteration'

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WWReceptionInfo(BaseModel):
    VERIFY_FIELD = ['dialogue_time','start_time','end_time','buyer_ww','cs_ww','category','initiator']
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    dialogue_time = models.DateTimeField(verbose_name='日期')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    buyer_ww = models.CharField(max_length=60, verbose_name='买家旺旺')
    cs_ww = models.CharField(max_length=60, verbose_name='客服旺旺')
    category = models.CharField(max_length=30, verbose_name='接待类型')
    initiator = models.CharField(max_length=30, verbose_name='接待发起')
    order_status = models.CharField(max_length=30, verbose_name='状态')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='系统状态')

    class Meta:
        verbose_name = '旺旺接待记录'
        verbose_name_plural = verbose_name
        db_table = 'ops_ww_reception'

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WWNoReplayInfo(BaseModel):
    VERIFY_FIELD = ['dialogue_time', 'start_time', 'buyer_ww', 'cs_ww']
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    dialogue_time = models.DateTimeField(verbose_name='日期')
    start_time = models.TimeField(verbose_name='开始时间')
    buyer_ww = models.CharField(max_length=60, verbose_name='买家旺旺')
    cs_ww = models.CharField(max_length=60, verbose_name='客服旺旺')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='系统状态')

    class Meta:
        verbose_name = '旺旺未回复'
        verbose_name_plural = verbose_name
        db_table = 'ops_ww_noreplay'

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WWDialogueListInfo(BaseModel):
    VERIFY_FIELD = []
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    CATEGORY = (
        (0, '接待'),
        (1, '非接待'),
        (2, '未回复'),
    )
    dialogue_time = models.DateTimeField(verbose_name='聊天时间')
    buyer_ww = models.CharField(max_length=60, verbose_name='买家旺旺')
    cs_ww = models.CharField(max_length=60, verbose_name='客服旺旺')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='类型')
    memorandum = models.TextField(blank=True, null=True, verbose_name='备注')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='系统状态')

    class Meta:
        verbose_name = '旺旺对话总明细'
        verbose_name_plural = verbose_name
        db_table = 'ops_ww_dialogue'




