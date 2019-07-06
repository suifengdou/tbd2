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


class StockOutInfo(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    CATEGORY = (
        (0, '常规出库'),
        (1, '客供出库'),
        (2, '配件出库'),
    )

    stockout_id = models.CharField(null=True, blank=True, unique=True, max_length=30, verbose_name='出库单号')
    source_order_id = models.CharField(max_length=30, verbose_name='关联单号')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='状态')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='出库类型')
    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    goods_id = models.CharField(max_length=30, verbose_name='货品编码')
    quantity = models.IntegerField(verbose_name='发货数量')
    warehouse = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, verbose_name='仓库名称')
    nickname = models.CharField(null=True, blank=True, max_length=60, verbose_name='昵称')
    receiver = models.CharField(null=True, blank=True, max_length=60, verbose_name='收货人')
    province = models.CharField(null=True, blank=True, max_length=30, verbose_name='省份')
    city = models.CharField(null=True, blank=True, max_length=30, verbose_name='城市')
    district = models.CharField(null=True, blank=True, max_length=60, verbose_name='区县')
    mobile = models.CharField(null=True, blank=True, max_length=30, verbose_name='收货人手机')
    memorandum = models.TextField(null=True, blank=True, verbose_name='备注')

    class Meta:
        verbose_name = 'WMS-O-出库单'
        verbose_name_plural = verbose_name
        db_table = 'wms_stk_stockout'


class StockOutPenddingInfo(StockOutInfo):

    class Meta:
        verbose_name = 'WMS-O-未审核出库单'
        verbose_name_plural = verbose_name
        proxy = True


