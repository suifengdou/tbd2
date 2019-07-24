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

    company_name = models.CharField(unique=True, max_length=30, verbose_name='公司名称', db_index=True)
    tax_fil_number = models.CharField(unique=True, max_length=30, verbose_name='税号')
    status = models.IntegerField(choices=ORDER_STATUS, default=1, verbose_name='状态')

    class Meta:
        verbose_name = 'BASE-公司'
        verbose_name_plural = verbose_name
        db_table = 'base_company'

    def __str__(self):
        return self.company_name

