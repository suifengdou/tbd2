# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.base.warehouse.models import WarehouseInfo
from apps.oms.planorder.models import CusPartOrderInfo


class StockInfo(BaseModel):
    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    goods_id = models.CharField(max_length=20, verbose_name='货品编码')
    goods_category = models.IntegerField(verbose_name='货品类型')
    manufactory = models.CharField(max_length=60, verbose_name='工厂')
    size = models.CharField(max_length=10, verbose_name='规格')
    warehouse = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, verbose_name='仓库')
    inventory = models.IntegerField(verbose_name='库存')


