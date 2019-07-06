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
from apps.wms.stockin.models import StockInInfo
from apps.wms.stockout.models import StockOutInfo


class StockInfo(BaseModel):
    CATEGORY = (
        (0, "整机"),
        (1, "配件"),
        (2, "礼品"),
    )

    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    goods_id = models.CharField(max_length=30, verbose_name='货品编码')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='货品类型')
    size = models.CharField(null=True, blank=True, max_length=10, verbose_name='规格')
    warehouse = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, verbose_name='仓库')
    quantity = models.IntegerField(verbose_name='库存')

    class Meta:
        verbose_name = 'WMS-S-库存'
        verbose_name_plural = verbose_name
        db_table = 'wms_stk_stock'

    def available_quantity(self):
        return self.quantity - self.occupied_quantity()
    available_quantity.short_description = '可用库存'

    def occupied_quantity(self):
        stockout_orders = StockOutInfo.objects.filter(goods_id=self.goods_id, status__in=[1, 2])
        occupied_quantity = 0
        if stockout_orders:
            for stockout_order in stockout_orders:
                occupied_quantity += stockout_order.quantity
        return occupied_quantity
    occupied_quantity.short_description = '库存占用'


class StockMachineInfo(StockInfo):

    class Meta:
        verbose_name = 'WMS-S-整机库存'
        verbose_name_plural = verbose_name
        proxy = True


class StockPartInfo(StockInfo):
    class Meta:
        verbose_name = 'WMS-S-配件库存'
        verbose_name_plural = verbose_name
        proxy = True


class StockGiftInfo(StockInfo):
    class Meta:
        verbose_name = 'WMS-S-礼品库存'
        verbose_name_plural = verbose_name
        proxy = True
