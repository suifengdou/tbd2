# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel

from tbd2.settings import AUTH_USER_MODEL
from apps.utils.geography.models import CityInfo


class ManufactoryInfo(BaseModel):
    CATEGORY = (
        (0, '整机厂'),
        (1, '配件厂'),
    )
    name = models.CharField(unique=True, max_length=60, verbose_name='工厂名称')
    code = models.CharField(unique=True, null=True, blank=True, max_length=20, verbose_name='工厂代码')
    city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='城市')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='工厂类型')
    contacts = models.CharField(max_length=60, verbose_name='联系人')
    contacts_phone = models.CharField(max_length=30, verbose_name='电话')
    memorandum = models.CharField(max_length=150, verbose_name='备注')

    class Meta:
        verbose_name = 'BASE-工厂信息'
        verbose_name_plural = verbose_name
        db_table = 'base_manu_manufactory'

    def __str__(self):
        return self.name

