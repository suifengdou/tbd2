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
from apps.base.company.models import CompanyInfo


class PlatformInfo(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '正常'),
    )

    platform = models.CharField(unique=True, max_length=30, verbose_name='平台名称', db_index=True)
    status = models.IntegerField(choices=ORDER_STATUS, default=1, verbose_name='平台状态')

    class Meta:
        verbose_name = 'BASE-平台类型'
        verbose_name_plural = verbose_name
        db_table = 'base_platform'

    def __str__(self):
        return self.platform


class ShopInfo(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '正常'),
    )

    shop_name = models.CharField(unique=True, max_length=30, verbose_name='店铺名', db_index=True)
    shop_id = models.CharField(unique=True, max_length=30, verbose_name='店铺ID', db_index=True, null=True, blank=True)
    platform = models.ForeignKey(PlatformInfo, on_delete=models.SET_NULL, verbose_name='平台', null=True, blank=True)
    group_name = models.CharField(max_length=30, verbose_name='店铺分组')
    company = models.ForeignKey(CompanyInfo, on_delete=models.SET_NULL, verbose_name='公司', null=True, blank=True)
    status = models.IntegerField(choices=ORDER_STATUS, default=1, verbose_name='店铺状态')

    class Meta:
        verbose_name = 'BASE-店铺'
        verbose_name_plural = verbose_name
        db_table = 'base_shop'

    def __str__(self):
        return self.shop_name

