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
from apps.oms.manuorder.models import ManuOrderInfo


class StockInInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已入库'),
        (3, '异常'),
    )
    CATEGORY = (
        (0, '质检入库'),
        (1, '采购入库'),
    )
    ERROR_TAG = (
        (0, '正常'),
        (1, '入库单保存错误'),
        (2, '货品错误'),
    )
    stockin_id = models.CharField(null=True, blank=True, unique=True, max_length=30, verbose_name='入库单号')
    source_order_id = models.CharField(null=True, blank=True, max_length=30, verbose_name='来源单号')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='状态')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='入库单类型')
    batch_num = models.ForeignKey(ManuOrderInfo, on_delete=models.SET_NULL, null=True, blank=True,verbose_name='批次号')
    planorder_id = models.CharField(null=True, blank=True, max_length=30, verbose_name='采购单号')
    warehouse = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, verbose_name='仓库名称')
    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    goods_id = models.CharField(max_length=30, verbose_name='货品编码')
    quantity = models.IntegerField(verbose_name='入库数量')
    memorandum = models.CharField(null=True, blank=True, max_length=300, verbose_name='备注')
    error_tag = models.SmallIntegerField(choices=ERROR_TAG, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'WMS-I-入库单'
        verbose_name_plural = verbose_name
        db_table = 'wms_stk_stockin'


class StockInPenddingInfo(StockInInfo):

    class Meta:
        verbose_name = 'WMS-I-未审核入库单'
        verbose_name_plural = verbose_name
        proxy = True


