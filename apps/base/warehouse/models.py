# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.utils.geography.models import CityInfo


class WarehouseTypeInfo(BaseModel):
    category = models.CharField(unique=True, max_length=30, verbose_name='仓库类型')

    class Meta:
        verbose_name = '仓库类型'
        verbose_name_plural = verbose_name
        db_table = 'base_w_category'

    def __str__(self):
        return self.category


class WarehouseInfo(BaseModel):
    STATUS = (
        (0, '运行'),
        (1, '停用'),
    )
    warehouse_name = models.CharField(unique=True, max_length=60, verbose_name='仓库名称')
    warehouse_id = models.CharField(unique=True, max_length=20, verbose_name='仓库ID')
    city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='城市地点')
    category = models.ForeignKey(WarehouseTypeInfo, on_delete=models.CASCADE, verbose_name='仓库类型')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name='仓库状态')

    class Meta:
        verbose_name = '仓库类型'
        verbose_name_plural = verbose_name
        db_table = 'base_w_warehouse'

    def __str__(self):
        return self.warehouse_name

