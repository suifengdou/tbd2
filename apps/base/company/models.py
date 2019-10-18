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


class CompanyInfo(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '正常'),
    )
    CATEGORY = (
        (0, '小狗体系'),
        (1, '物流快递'),
        (2, '仓库存储'),
        (3, '生产制造'),
        (4, '其他类型'),
    )

    company_name = models.CharField(unique=True, max_length=30, verbose_name='公司简称', db_index=True)
    company = models.CharField(null=True, blank=True, max_length=60, verbose_name='公司名称')
    tax_fil_number = models.CharField(unique=True, null=True, blank=True, max_length=30, verbose_name='税号')
    status = models.IntegerField(choices=ORDER_STATUS, default=1, verbose_name='状态')
    category = models.IntegerField(choices=CATEGORY, default=1, verbose_name='公司类型')

    class Meta:
        verbose_name = 'BASE-公司-公司管理'
        verbose_name_plural = verbose_name
        db_table = 'base_company'

    def __str__(self):
        return self.company_name


class LogisticsInfo(CompanyInfo):

    class Meta:
        verbose_name = 'BASE-公司-快递物流'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.company_name


class ManuInfo(CompanyInfo):
    class Meta:
        verbose_name = 'BASE-公司-生产制造'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.company_name


class WareInfo(CompanyInfo):
    class Meta:
        verbose_name = 'BASE-公司-仓库存储'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.company_name